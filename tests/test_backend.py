"""백엔드 단위 테스트: 날씨 변환, 회원·기록 DB, 모델 예측."""
from datetime import date, datetime

import pytest

from backend import auth
from backend.predictor import Predictor, level_of, normalize_flight
from backend.weather import KST, WeatherError, get_day_forecast, get_weather, ms_to_kt, parse_precip, vilage_base


# ---------- 날씨 ----------
@pytest.mark.parametrize("text, mm", [
    ("강수없음", 0.0), ("0", 0.0), ("1mm 미만", 0.5), ("1.0mm", 1.0),
    ("30.0~50.0mm", 40.0), ("50.0mm 이상", 50.0),
])
def test_parse_precip(text, mm):
    assert parse_precip(text) == mm


def test_ms_to_kt():
    assert ms_to_kt(10) == 19.4


def test_vilage_base_uses_previous_day_before_0210():
    now = datetime(2026, 10, 28, 2, 5, tzinfo=KST)
    assert vilage_base(now) == datetime(2026, 10, 27, 23, 0, tzinfo=KST)


# ---------- 회원·기록 ----------
def test_signup_login_history(tmp_path):
    db = tmp_path / "t.db"
    auth.init_db(db)
    assert auth.create_user("테스트", "tester1", "password1", db)
    assert not auth.create_user("테스트", "tester1", "password1", db)       # 같은 아이디
    user = auth.verify_user("tester1", "password1", db)
    assert user and auth.verify_user("tester1", "wrong", db) is None

    result = {"flight": {"편명": "KE705", "항공사": "대한항공", "도착지": "도쿄/나리타", "도착코드": "NRT"},
              "dep": datetime(2026, 10, 29, 10, 0), "prob": 0.3, "level": "보통"}
    for _ in range(auth.HISTORY_LIMIT + 3):
        auth.add_history(user["id"], result, db)
    assert len(auth.list_history(user["id"], db)) == auth.HISTORY_LIMIT


def test_validate_signup():
    assert auth.validate_signup("이름", "ab", "password1", "password1", True)    # 아이디 짧음
    assert auth.validate_signup("이름", "tester1", "password1", "password1", True) is None


# ---------- 모델 ----------
@pytest.fixture(scope="module")
def predictor():
    return Predictor()


def test_level_and_normalize():
    assert [level_of(x) for x in (0.1, 0.2, 0.5)] == ["낮음", "보통", "높음"]
    assert normalize_flight(" ke 705 ") == "KE705"


def test_predict(predictor):
    w = predictor.monthly_average_weather(10)
    r = predictor.predict("KE705", datetime(2026, 10, 29, 10, 0), w)
    assert 0 <= r["prob"] <= 1 and len(r["factors"]) == 3
    assert predictor.predict("XX0000", datetime(2026, 10, 29, 10, 0), w) is None


def test_compare_sorted_and_marks_average_weather(predictor):
    items = predictor.compare("도쿄/나리타", date(2026, 10, 29), {})
    probs = [it["prob"] for it in items]
    assert items and probs == sorted(probs) and all(it["avg_weather"] for it in items)


# ---------- 예보 시각 맞추기 (3일 뒤는 3시간 간격) ----------
class FakeSession:
    """기상청 대신 정해 둔 예보를 돌려준다: 10월 31일 9시·12시만 있음."""
    def get(self, url, params, timeout):
        items = [{"fcstDate": "20261031", "fcstTime": t, "category": c, "fcstValue": v}
                 for t, wsd in (("0900", "5"), ("1200", "10"))
                 for c, v in (("TMP", "12"), ("WSD", wsd), ("PCP", "강수없음"), ("SKY", "1"), ("PTY", "0"))]
        body = {"response": {"header": {"resultCode": "00"}, "body": {"items": {"item": items}}}}
        return type("Res", (), {"json": lambda self: body})()


def test_get_weather_uses_nearest_forecast_hour():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=KST)
    w = get_weather(datetime(2026, 10, 31, 10, 0), "key", now=now, session=FakeSession())
    assert w["풍속"] == ms_to_kt(5) and w["출처"] == "기상청 단기예보 (9시 예보)"
    with pytest.raises(WeatherError):                                        # 9시·12시에서 2시간 넘게 떨어짐
        get_weather(datetime(2026, 10, 31, 15, 0), "key", now=now, session=FakeSession())


def test_day_forecast_fills_hours_between_3h_steps():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=KST)
    f = get_day_forecast(date(2026, 10, 31), "key", now=now, session=FakeSession())
    assert sorted(f) == [7, 8, 9, 10, 11, 12, 13, 14]
    assert f[11]["풍속"] == ms_to_kt(10) and f[9]["출처"] == "기상청 단기예보"
