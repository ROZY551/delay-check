"""화면들이 같이 쓰는 기능: 모델·DB 준비, 날씨 가져오기(캐시), 예측 실행."""
from __future__ import annotations

import os
from datetime import date, datetime, time

import streamlit as st

from backend import auth
from backend.predictor import Predictor
from backend.weather import KST, WeatherError, describe, get_day_forecast, get_weather


@st.cache_resource(show_spinner=False)
def get_predictor() -> Predictor:
    return Predictor()


@st.cache_resource(show_spinner=False)
def init_db() -> bool:
    auth.init_db()
    return True


def api_key() -> str:
    try:
        key = st.secrets.get("KMA_SERVICE_KEY", "")
    except Exception:            # secrets 파일이 없을 때
        key = ""
    return key or os.environ.get("KMA_SERVICE_KEY", "")


@st.cache_data(ttl=600, show_spinner=False)
def _weather_cached(target_iso: str, key: str) -> dict:
    return get_weather(datetime.fromisoformat(target_iso), key)


@st.cache_data(ttl=600, show_spinner=False)
def _day_cached(day_iso: str, key: str) -> dict:
    return get_day_forecast(date.fromisoformat(day_iso), key)


def weather_for(dep: datetime) -> dict:
    """예보를 가져오고, 실패하면 월평균 날씨로 대체 (화면에 안내가 나간다)."""
    try:
        return _weather_cached(dep.replace(tzinfo=KST).isoformat(), api_key())
    except WeatherError as e:
        w = get_predictor().monthly_average_weather(dep.month)
        w.update({"출처": "월평균", "발표": "", "오류": str(e)})
        w["설명"] = describe(w)
        return w


def day_weather(day: date) -> tuple[dict, str]:
    try:
        return _day_cached(day.isoformat(), api_key()), ""
    except WeatherError as e:
        return {}, str(e)


def run_prediction(flight_no: str, dep_date: date, dep_time: time) -> dict | None:
    """예측하고 결과를 세션에 저장. 로그인 상태면 조회 기록에도 저장. 없는 편명이면 None."""
    p = get_predictor()
    if p.find_flight(flight_no) is None:
        return None
    dep = datetime.combine(dep_date, dep_time)
    result = p.predict(flight_no, dep, weather_for(dep))
    user = st.session_state.get("user")
    if user:
        auth.add_history(user["id"], result)
        result["saved"] = True
    return result


def today_kst() -> date:
    return datetime.now(KST).date()
