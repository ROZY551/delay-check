"""딜레이 체크 — 인천공항 출발 항공편 지연 확률 예측 웹앱

실행 (저장소 맨 위 폴더에서):  streamlit run app/main.py
"""
import streamlit as st

from backend.services import get_predictor, init_db
from frontend.components.style import PAGES, inject_css

st.set_page_config(page_title="딜레이 체크 · 인천공항 출발 지연 예측", page_icon="✈️", layout="wide")

init_db()
get_predictor()          # 첫 실행 때 모델을 한 번만 불러온다
inject_css()

pages = [
    st.Page(PAGES["home"], title="지연 예측", default=True),
    st.Page(PAGES["compare"], title="편 비교", url_path="compare"),
    st.Page(PAGES["history"], title="조회 기록", url_path="history"),
    st.Page(PAGES["login"], title="로그인", url_path="login"),
    st.Page(PAGES["signup"], title="회원가입", url_path="signup"),
]
st.navigation(pages, position="hidden").run()
