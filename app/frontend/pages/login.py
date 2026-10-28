"""7. 로그인"""
import streamlit as st

from backend import auth
from frontend.components.style import PAGES, footer, header

header("login")

left, right = st.columns([1, 1.2], gap="large", vertical_alignment="center")
with left:
    st.markdown("""
<section class="dc-up" style="background:#0B2545;color:#fff;border-radius:24px;padding:40px 36px;margin-top:24px">
<div style="font-family:'Montserrat',sans-serif;font-style:italic;font-weight:900;font-size:30px">DELAY<span style="color:#FFB81C">CHECK</span></div>
<h2 style="margin:18px 0;font-size:26px;line-height:1.4;font-weight:900;color:#fff">로그인하면<br>조회한 항공편이 저장돼요</h2>
<div style="display:flex;flex-direction:column;gap:12px;font-size:16px;color:#DDE5F0">
<span><b style="color:#FFB81C">✓</b> 최근 조회한 10편을 다시 볼 수 있어요</span>
<span><b style="color:#FFB81C">✓</b> 누르면 최신 날씨 예보로 다시 계산해요</span>
<span><b style="color:#FFB81C">✓</b> 로그인하지 않아도 예측은 할 수 있어요</span>
</div></section>""", unsafe_allow_html=True)

with right:
    with st.container(key="auth_card"):
        st.markdown('<h1 class="dc-h1" style="margin:0 0 8px;font-size:30px;font-weight:900;color:#0B2545">로그인</h1>', unsafe_allow_html=True)
        with st.form("login", border=False):
            username = st.text_input("아이디", placeholder="아이디를 입력하세요")
            pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            ok = st.form_submit_button("로그인", type="primary", use_container_width=True)
        if ok:
            user = auth.verify_user(username.strip(), pw)
            if user:
                st.session_state["user"] = user
                st.switch_page(PAGES["history"])
            else:
                st.error("아이디 또는 비밀번호가 맞지 않아요.")
        st.markdown('<div style="text-align:center;color:#4A5568">아직 회원이 아니신가요?</div>', unsafe_allow_html=True)
        st.page_link(PAGES["signup"], label="회원가입 하러 가기", icon=":material/person_add:")

footer()
