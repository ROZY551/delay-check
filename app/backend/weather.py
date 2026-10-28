"""기상청 단기예보 조회서비스(공공데이터포털)로 인천공항 출발 시각의 날씨를 가져온다.

- 지났거나 지금      → 초단기실황 (getUltraSrtNcst)
- 6시간 이내         → 초단기예보 (getUltraSrtFcst)
- 그 뒤 (약 3일까지) → 단기예보   (getVilageFcst)
- 못 가져오면        → 호출한 쪽에서 월평균 날씨로 대체

학습 데이터(AMOS)와 단위를 맞춘다: 풍속 m/s → KT, 강수량 글자 → mm 숫자.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

KST = ZoneInfo("Asia/Seoul")
NX, NY = 51, 124                       # 인천공항 격자 (위도 37.46, 경도 126.44)
BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
MS_TO_KT = 1.94384
VILAGE_HOURS = [2, 5, 8, 11, 14, 17, 20, 23]

SKY = {"1": "맑음", "3": "구름 많음", "4": "흐림"}
PTY = {"0": "", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기", "5": "빗방울", "6": "빗방울/눈날림", "7": "눈날림"}


class WeatherError(Exception):
    pass


# ---------- 값 변환 ----------
def parse_precip(value) -> float:
    """'강수없음', '1mm 미만', '1.0mm', '30.0~50.0mm', '50.0mm 이상', '0' → mm 숫자"""
    s = str(value).strip()
    if s in ("", "-", "강수없음", "0", "0.0", "None"):
        return 0.0
    if "미만" in s:
        return 0.5
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]
    if not nums:
        return 0.0
    if "~" in s and len(nums) >= 2:
        return (nums[0] + nums[1]) / 2
    return nums[0]


def ms_to_kt(ms) -> float:
    return round(float(ms) * MS_TO_KT, 1)


def describe(weather: dict) -> str:
    """'맑음, 바람 약함' 같은 한 줄 설명"""
    rain, wind = weather["강수량"], weather["풍속"]
    sky = weather.get("하늘") or ("비" if rain > 0 else "")
    if rain > 0 and sky in ("", "맑음", "구름 많음", "흐림"):
        sky = "비"
    wind_text = "바람 강함" if wind >= 20 else ("바람 보통" if wind >= 12 else "바람 약함")
    return f"{sky}, {wind_text}" if sky else wind_text


# ---------- 발표 시각 계산 ----------
def ncst_base(now: datetime) -> datetime:
    """초단기실황: 매시 정각 발표, 40분 뒤부터 조회"""
    t = now - timedelta(minutes=40)
    return t.replace(minute=0, second=0, microsecond=0)


def ultra_fcst_base(now: datetime) -> datetime:
    """초단기예보: 매시 30분 발표, 45분 뒤부터 조회"""
    t = now - timedelta(minutes=45)
    return t.replace(minute=30, second=0, microsecond=0)


def vilage_base(now: datetime) -> datetime:
    """단기예보: 02·05·08·11·14·17·20·23시 발표, 10분 뒤부터 조회"""
    t = now - timedelta(minutes=10)
    for h in reversed(VILAGE_HOURS):
        if t.hour >= h:
            return t.replace(hour=h, minute=0, second=0, microsecond=0)
    prev = t - timedelta(days=1)
    return prev.replace(hour=23, minute=0, second=0, microsecond=0)


def previous_base(kind: str, base: datetime) -> datetime:
    if kind == "vilage":
        return vilage_base(base - timedelta(minutes=1) + timedelta(minutes=10))
    return base - timedelta(hours=1)


# ---------- API 호출 ----------
def fetch_items(endpoint: str, base: datetime, key: str, session=None, timeout: int = 8) -> list[dict]:
    params = {
        "serviceKey": key, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON",
        "base_date": base.strftime("%Y%m%d"), "base_time": base.strftime("%H%M"),
        "nx": NX, "ny": NY,
    }
    http = session or requests
    try:
        res = http.get(f"{BASE_URL}/{endpoint}", params=params, timeout=timeout)
    except requests.RequestException as e:
        raise WeatherError(f"기상청 서버에 연결하지 못했어요 ({e.__class__.__name__})") from e
    try:
        body = res.json()["response"]
    except Exception as e:                       # 인증 오류는 XML로 온다
        raise WeatherError("기상청 응답을 읽지 못했어요 (인증키를 확인해 주세요)") from e
    code = body["header"]["resultCode"]
    if code == "03":
        return []                                # NO_DATA: 아직 발표 전
    if code != "00":
        raise WeatherError(f"기상청 오류 {code}: {body['header'].get('resultMsg', '')}")
    return body["body"]["items"]["item"]


def _pick(items: list[dict], target: datetime) -> dict[str, str]:
    d, t = target.strftime("%Y%m%d"), target.strftime("%H00")
    return {it["category"]: it["fcstValue"] for it in items
            if it.get("fcstDate") == d and it.get("fcstTime") == t}


def _fetch_with_retry(kind: str, endpoint: str, base: datetime, key: str, session=None) -> tuple[list[dict], datetime]:
    items = fetch_items(endpoint, base, key, session)
    if not items:                                # 발표 직후라 비어 있으면 한 단계 전 발표로
        base = previous_base(kind, base)
        items = fetch_items(endpoint, base, key, session)
    return items, base


def get_weather(target: datetime, key: str, now: datetime | None = None, session=None) -> dict:
    """출발 시각(target)의 풍속(KT)·기온(℃)·강수량(mm). 못 가져오면 WeatherError."""
    if not key:
        raise WeatherError("날씨 API 인증키가 설정되지 않았어요")
    now = (now or datetime.now(KST)).astimezone(KST)
    target = target.replace(tzinfo=KST) if target.tzinfo is None else target.astimezone(KST)
    slot = target.replace(minute=0, second=0, microsecond=0)
    hours_ahead = (slot - now).total_seconds() / 3600

    if hours_ahead <= 0:
        items, base = _fetch_with_retry("ncst", "getUltraSrtNcst", ncst_base(now), key, session)
        obs = {it["category"]: it["obsrValue"] for it in items}
        if not obs:
            raise WeatherError("현재 날씨 관측값이 없어요")
        w = {"풍속": ms_to_kt(obs.get("WSD", 0)), "기온": float(obs.get("T1H", 0)),
             "강수량": parse_precip(obs.get("RN1", 0)), "하늘": PTY.get(obs.get("PTY", "0"), "")}
        source = "기상청 초단기실황"
    else:
        use_ultra = hours_ahead <= 5
        if use_ultra:
            items, base = _fetch_with_retry("ultra", "getUltraSrtFcst", ultra_fcst_base(now), key, session)
            v = _pick(items, slot)
            temp_key, rain_key = "T1H", "RN1"
            source = "기상청 초단기예보"
        if not use_ultra or not v:
            items, base = _fetch_with_retry("vilage", "getVilageFcst", vilage_base(now), key, session)
            v = _pick(items, slot)
            temp_key, rain_key = "TMP", "PCP"
            source = "기상청 단기예보"
        if not v:
            raise WeatherError("이 시각의 예보가 아직 없어요")
        pty = PTY.get(v.get("PTY", "0"), "")
        w = {"풍속": ms_to_kt(v.get("WSD", 0)), "기온": float(v.get(temp_key, 0)),
             "강수량": parse_precip(v.get(rain_key, 0)), "하늘": pty or SKY.get(v.get("SKY", ""), "")}

    w["출처"] = source
    w["발표"] = base.strftime("%m.%d %H:%M")
    w["설명"] = describe(w)
    return w


def get_day_forecast(day, key: str, now: datetime | None = None, session=None) -> dict[int, dict]:
    """편 비교용: 그날 0~23시 단기예보를 한 번에. {시: 날씨}"""
    now = (now or datetime.now(KST)).astimezone(KST)
    items, base = _fetch_with_retry("vilage", "getVilageFcst", vilage_base(now), key, session)
    d = day.strftime("%Y%m%d")
    by_hour: dict[int, dict[str, str]] = {}
    for it in items:
        if it.get("fcstDate") == d:
            by_hour.setdefault(int(it["fcstTime"][:2]), {})[it["category"]] = it["fcstValue"]
    out = {}
    for h, v in by_hour.items():
        if "TMP" in v and "WSD" in v:
            w = {"풍속": ms_to_kt(v["WSD"]), "기온": float(v["TMP"]), "강수량": parse_precip(v.get("PCP", 0)),
                 "하늘": PTY.get(v.get("PTY", "0"), "") or SKY.get(v.get("SKY", ""), "")}
            w["출처"], w["발표"] = "기상청 단기예보", base.strftime("%m.%d %H:%M")
            w["설명"] = describe(w)
            out[h] = w
    return out
