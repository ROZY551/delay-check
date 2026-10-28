"""8. 회원가입 (이름·아이디·비밀번호만 받는다)"""
import streamlit as st

from backend import auth
from frontend.components.style import PAGES, footer, header

header("signup")

_, mid, _ = st.columns([1, 2, 1])
with mid:
    st.markdown("""
<div class="dc-up" style="background:#0B2545;color:#fff;border-radius:24px 24px 0 0;padding:26px 32px;margin-top:24px">
<h1 style="margin:0;font-size:28px;font-weight:900;color:#fff">회원가입</h1>
<p style="margin:6px 0 0;font-size:16px;color:#B9C6DA">가입하면 조회한 항공편을 저장하고 다시 볼 수 있어요.</p></div>""", unsafe_allow_html=True)
    with st.container(key="auth_card"):
        with st.form("signup", border=False):
            name = st.text_input("이름(닉네임)", placeholder="화면에 표시될 이름")
            a, b = st.columns([3, 1], vertical_alignment="bottom")
            username = a.text_input("아이디", placeholder="영문·숫자 4~12자")
            check = b.form_submit_button("중복 확인", use_container_width=True)
            pw = st.text_input("비밀번호", type="password", placeholder="8자 이상")
            pw2 = st.text_input("비밀번호 확인", type="password", placeholder="한 번 더 입력하세요")
            agreed = st.checkbox("[필수] 아이디·이름과 조회 기록 저장에 동의해요. 다른 개인정보는 받지 않아요.")
            submit = st.form_submit_button("가입하기", type="primary", use_container_width=True)

        if check:
            if not auth.USERNAME_RE.match(username):
                st.warning("아이디는 영문·숫자 4~12자로 입력해 주세요.")
            elif auth.username_available(username):
                st.success("사용할 수 있는 아이디예요.")
            else:
                st.error("이미 사용 중인 아이디예요.")
        if submit:
            problem = auth.validate_signup(name, username, pw, pw2, agreed)
            if problem:
                st.error(problem)
            elif not auth.create_user(name, username, pw):
                st.error("이미 사용 중인 아이디예요.")
            else:
                st.success("가입했어요! 로그인해 주세요.")
                st.page_link(PAGES["login"], label="로그인 하러 가기", icon=":material/login:")
        st.markdown('<div style="text-align:center;color:#4A5568;margin-top:8px">이미 계정이 있나요?</div>', unsafe_allow_html=True)
        st.page_link(PAGES["login"], label="로그인", icon=":material/login:")

footer()
