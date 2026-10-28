"""백엔드 단위 테스트: 날씨 변환, 회원·기록 DB, 모델 예측."""
from datetime import date, datetime

import pytest

from backend import auth
from backend.predictor import Predictor, level_of, normalize_flight
from backend.weather import ms_to_kt, parse_precip, vilage_base, KST


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
