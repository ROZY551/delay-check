"""6. 조회 기록: 로그인한 계정에 저장된 최근 10편."""
from datetime import datetime, timedelta

import streamlit as st

from backend import auth
from backend.services import run_prediction, today_kst
from frontend.components import cards
from frontend.components.style import PAGES, footer, header

header("history")
user = st.session_state.get("user")

st.markdown('<h1 class="dc-h1" style="margin:18px 0 4px;font-size:32px;font-weight:900;color:#0B2545">조회 기록</h1>', unsafe_allow_html=True)

if not user:
    st.markdown('<p style="margin:0 0 16px;font-size:17px;color:#4A5568">로그인하면 조회한 항공편이 저장되고, 여기서 다시 볼 수 있어요.</p>', unsafe_allow_html=True)
    with st.container(key="auth_card"):
        st.markdown("#### 로그인이 필요해요")
        a, b, _ = st.columns([1, 1, 3])
        if a.button("로그인", type="primary", use_container_width=True):
            st.switch_page(PAGES["login"])
        if b.button("회원가입", use_container_width=True):
            st.switch_page(PAGES["signup"])
else:
    top_l, top_r = st.columns([4, 1], vertical_alignment="bottom")
    top_l.markdown('<p style="margin:0;font-size:17px;color:#4A5568">로그인한 계정에 최근 조회한 항공편 10개까지 저장돼요.</p>', unsafe_allow_html=True)
    rows = auth.list_history(user["id"])
    if rows and top_r.button("전체 삭제", use_container_width=True):
        auth.clear_history(user["id"])
        st.rerun()

    if not rows:
        st.info("아직 조회한 항공편이 없어요. 지연 예측에서 편명을 조회해 보세요.", icon=":material/flight:")
    today = today_kst()
    for h in rows:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1.2, 0.5], vertical_alignment="center")
            c1.markdown(cards.history_card(h), unsafe_allow_html=True)
            dep = datetime.fromisoformat(h["dep_at"])
            still_open = today <= dep.date() <= today + timedelta(days=3)
            if c2.button("다시 보기", key=f"re_{h['id']}", type="primary", use_container_width=True,
                         disabled=not still_open, help=None if still_open else "출발일이 지나 다시 계산할 수 없어요"):
                result = run_prediction(h["flight_no"], dep.date(), dep.time())
                st.session_state.update(view="result", result=result, flight_no=h["flight_no"], dep_date=dep.date(), dep_time=dep.time())
                st.switch_page(PAGES["home"])
            if c3.button("", key=f"del_{h['id']}", icon=":material/delete:", help="이 기록 삭제"):
                auth.delete_history(user["id"], h["id"])
                st.rerun()
    st.caption("‘다시 보기’를 누르면 지금 날씨 예보로 다시 계산해요. 저장된 확률과 달라질 수 있어요.")

footer()
