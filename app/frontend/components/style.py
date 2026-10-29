"""공통 스타일(CSS), 머리글, 바닥글. 디자인 캔버스의 색·글꼴을 그대로 옮겼다."""
from __future__ import annotations

import streamlit as st

NAVY, AMBER, BG = "#0B2545", "#FFB81C", "#E6ECF4"

PAGES = {
    "home": "frontend/pages/home.py",
    "compare": "frontend/pages/compare.py",
    "history": "frontend/pages/history.py",
    "login": "frontend/pages/login.py",
    "signup": "frontend/pages/signup.py",
}

FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900"
         "&family=JetBrains+Mono:wght@500;700;800&family=Montserrat:ital,wght@1,900&display=swap")

CSS = """
<style>
@import url('%(fonts)s');
html, body, [class*="st-"], .stMarkdown, button, input, textarea { font-family: 'Noto Sans KR', sans-serif; }
/* 위 글꼴 지정이 아이콘까지 덮으면 'schedule' 같은 아이콘 이름이 글자로 보인다 → 아이콘 글꼴은 되돌린다 */
[data-testid="stIconMaterial"], [data-testid$="DynamicIcon"] { font-family: 'Material Symbols Rounded' !important; }
.stApp { background: %(bg)s; }
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], footer { display: none !important; }
[data-testid="stMainBlockContainer"] { max-width: 1200px; padding: 0 24px 0; %(zoom)s }
.mono { font-family: 'JetBrains Mono', monospace; }

/* 머리글 */
.st-key-topbar { background: #FFFFFF; border-radius: 0 0 18px 18px; padding: 10px 18px; margin-bottom: 14px;
  box-shadow: 0 2px 10px rgba(11,37,69,.06); }
.st-key-logo button { background: transparent !important; border: none !important; box-shadow: none !important;
  padding: 4px 0 !important; min-height: 44px; }
.st-key-logo button p { font-family: 'Montserrat', sans-serif !important; font-style: italic; font-weight: 900 !important;
  font-size: 24px !important; color: %(navy)s; letter-spacing: -.02em; white-space: nowrap; overflow: visible; }
.st-key-logo button div { overflow: visible; }
.st-key-logo button p::after { content: '✈'; font-size: 16px; color: %(navy)s; position: relative; top: -14px; left: 2px; }
[data-testid="stPageLink"] a { min-height: 44px; border-radius: 10px; padding: 0 16px; font-weight: 800; }
[data-testid="stPageLink"] a p { font-size: 16px; font-weight: 800; color: #2D3748; }
.st-key-nav_active [data-testid="stPageLink"] a { background: %(navy)s; }
.st-key-nav_active [data-testid="stPageLink"] a p, .st-key-nav_active [data-testid="stIconMaterial"] { color: #FFFFFF; }
.st-key-nav { background: #EEF2F7; border-radius: 14px; padding: 4px; }

/* 버튼 */
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] {
  background: %(amber)s; color: %(navy)s; border: none; border-radius: 14px; min-height: 56px; font-weight: 900; font-size: 18px; }
.stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover { background: #F2A900; color: %(navy)s; }
.stButton button[kind="primary"] p, .stFormSubmitButton button[kind="primaryFormSubmit"] p { font-size: 18px; font-weight: 900; }
.stButton button[kind="secondary"], .stFormSubmitButton button[kind="secondaryFormSubmit"] { border-radius: 10px; min-height: 44px; font-weight: 700; }
.stButton button[kind="secondary"] p, .stFormSubmitButton button[kind="secondaryFormSubmit"] p { font-size: 16px; font-weight: 700; }

/* 입력 (날짜·시각 칸은 <input>이 아니라 role="group" 안의 글자 조각으로 그려진다) */
.stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div {
  min-height: 52px; font-size: 18px; font-weight: 700; border-radius: 12px; }
[data-testid="stDateInput"] [role="group"], [data-testid="stTimeInput"] [role="group"],
[data-testid="stDateInput"] [role="group"] *, [data-testid="stTimeInput"] [role="group"] *,
[data-testid="stSelectbox"] input { font-size: 18px !important; font-weight: 700; min-height: 40px; }
[data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 700; color: #2D3748; }
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p { font-size: 15px !important; font-weight: 500; }
.st-key-flight_no input { font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 800; text-transform: uppercase; }

/* 카드 */
.card { background: #FFFFFF; border-radius: 18px; padding: 22px 24px; box-shadow: 0 4px 14px rgba(11,37,69,.06); }
.st-key-search_card { background: #FFFFFF; border-radius: 20px; padding: 20px 26px 8px; margin: -96px 36px 0;
  width: calc(100%% - 72px) !important; position: relative; z-index: 5; box-shadow: 0 12px 32px rgba(11,37,69,.14); }
@media (max-width: 640px) {
  .st-key-search_card { margin: -64px 8px 0; width: calc(100%% - 16px) !important; padding: 16px 16px 6px; }
  [data-testid="stMainBlockContainer"] { padding: 0 12px 0; }
}
.st-key-chart_card, .st-key-form_card, .st-key-auth_card { background: #FFFFFF; border-radius: 18px; padding: 20px 24px;
  box-shadow: 0 4px 14px rgba(11,37,69,.06); }
.cmp-row { background: #FFFFFF; }
/* ---------- 애니메이션 ---------- */
@keyframes dc-up { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes dc-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes dc-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes dc-rise { from { clip-path: inset(100%% 0 0 0); } to { clip-path: inset(0 0 0 0); } }
@keyframes dc-pop { 0%% { transform: scale(.6); opacity: 0; } 70%% { transform: scale(1.08); opacity: 1; } 100%% { transform: scale(1); } }
@keyframes dc-slide { from { left: -10px; } }
@keyframes dc-spin { to { transform: rotate(360deg); } }
@keyframes dc-drip { 0%%, 100%% { transform: translateY(0); } 50%% { transform: translateY(2px); } }
@keyframes dc-shine { 0%%, 60%% { opacity: .55; } 30%% { opacity: 1; } }
@keyframes dc-shake { 0%%, 100%% { transform: rotate(0); } 20%% { transform: rotate(-12deg); } 40%% { transform: rotate(10deg); } 60%% { transform: rotate(-6deg); } 80%% { transform: rotate(4deg); } }
@keyframes dc-fly { 0%%, 100%% { transform: translate(0, 0); } 50%% { transform: translate(3px, -3px); } }
@keyframes dc-sweep { from { transform: translateX(-120%%) skewX(-20deg); } to { transform: translateX(220%%) skewX(-20deg); } }
@property --dc-n { syntax: '<integer>'; inherits: false; initial-value: 0; }
@keyframes dc-count { from { --dc-n: 0; } to { --dc-n: var(--to); } }

/* 머리글이 위에서 내려오고, 로고 비행기는 둥실 떠 있다 */
.st-key-topbar { animation: dc-fade .5s ease both; }
.st-key-logo button p::after { display: inline-block; animation: dc-fly 2.6s ease-in-out infinite; }
.st-key-logo button:hover p::after { animation: none; transform: translate(8px, -8px); transition: transform .3s; }
/* 메뉴: 마우스를 올리면 배경이 차오르고, 지금 메뉴는 살짝 튀어나온다 */
[data-testid="stPageLink"] a { transition: background .25s, transform .2s; }
.st-key-nav [data-testid="stPageLink"] a:hover { background: #DDE5F0; transform: translateY(-2px); }
.st-key-nav_active [data-testid="stPageLink"] a { animation: dc-pop .4s ease both; }
.st-key-nav_active [data-testid="stPageLink"] a:hover { background: %(navy)s; }
/* 노란 버튼: 올리면 떠오르고 빛이 한 번 지나간다, 누르면 눌린다 */
.stButton button, .stFormSubmitButton button { transition: transform .18s, box-shadow .18s, background .2s; }
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] { position: relative; overflow: hidden; }
.stButton button[kind="primary"]::before, .stFormSubmitButton button[kind="primaryFormSubmit"]::before { content: ''; position: absolute; top: 0; bottom: 0; left: 0; width: 40%%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.55), transparent); transform: translateX(-120%%) skewX(-20deg); pointer-events: none; }
.stButton button[kind="primary"]:hover::before, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover::before { animation: dc-sweep .7s ease; }
.stButton button:hover:not(:disabled), .stFormSubmitButton button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(11,37,69,.16); }
.stButton button:active:not(:disabled), .stFormSubmitButton button:active:not(:disabled) { transform: translateY(1px) scale(.98); box-shadow: none; }
/* 입력칸: 누르면 노란 테두리가 번진다 */
.stTextInput div[data-baseweb="input"], .stDateInput div[data-baseweb="input"], .stTimeInput div[data-baseweb="select"] > div,
.stSelectbox div[data-baseweb="select"] > div { transition: box-shadow .25s; }
.stTextInput div[data-baseweb="input"]:focus-within, .stDateInput div[data-baseweb="input"]:focus-within { box-shadow: 0 0 0 4px rgba(255,184,28,.35); }

/* 조회칸·카드·제목이 아래에서 차례로 올라온다 */
.st-key-search_card { animation: dc-up .7s cubic-bezier(.2,.8,.2,1) .15s both; }
.st-key-chart_card, .st-key-form_card, .st-key-auth_card, .card, .dc-up { animation: dc-up .6s cubic-bezier(.2,.8,.2,1) both; }
[data-testid="stColumn"]:nth-child(2) .card, [data-testid="stColumn"]:nth-child(2) .st-key-chart_card { animation-delay: .12s; }
[data-testid="stColumn"]:nth-child(3) .card, [data-testid="stColumn"]:nth-child(3) .st-key-chart_card { animation-delay: .24s; }
.card, .st-key-chart_card { transition: transform .25s, box-shadow .25s; }
.card:hover, .st-key-chart_card:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(11,37,69,.12); }
/* 그래프: 막대가 아래에서 위로 자라난다 */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] { animation: dc-rise 1s cubic-bezier(.2,.8,.2,1) .25s both; }

/* 결과 요약: 카드가 올라오고, 지연 확률 숫자가 0부터 올라가고, 단계 막대 동그라미가 미끄러진다 */
.dc-summary { animation: dc-up .6s cubic-bezier(.2,.8,.2,1) both; margin-bottom: 12px; }
.dc-count { --dc-n: var(--to); counter-reset: dc var(--dc-n); animation: dc-count 1.2s cubic-bezier(.2,.8,.2,1) .3s both; }
.dc-count::before { content: counter(dc); }
.dc-chip { display: inline-block; animation: dc-pop .5s ease 1.3s both; }
.dc-marker { animation: dc-slide 1.2s cubic-bezier(.2,.8,.2,1) .3s both; }
.dc-scale { transform-origin: left; animation: dc-grow .8s ease .1s both; }
/* 카드 제목 아이콘: 해는 돌고, 비구름은 톡톡, 전구는 반짝, 느낌표는 흔들 */
.dc-ic-sun svg { animation: dc-spin 12s linear infinite; }
.dc-ic-rain svg { animation: dc-drip 1.2s ease-in-out infinite; }
.dc-ic-bulb svg { animation: dc-shine 2.4s ease-in-out infinite; }
.dc-ic-bars svg path:not(:last-child) { transform-box: fill-box; transform-origin: bottom; animation: dc-grow-y .8s ease both; }
@keyframes dc-grow-y { from { transform: scaleY(0); } to { transform: scaleY(1); } }
.dc-shake { animation: dc-shake .7s ease .3s both; }
/* 예측 근거 줄이 하나씩 나타난다 */
.dc-row { animation: dc-up .45s ease both; }

/* 편 비교: 추천 띠가 먼저, 표 줄은 차례로, 막대는 왼쪽부터 채워진다 */
.dc-cmp-row { animation: dc-up .45s ease both; transition: background .2s; }
.dc-cmp-row:hover { background: #F3F7FC !important; }
.dc-fill { transform-origin: left; animation: dc-grow .9s cubic-bezier(.2,.8,.2,1) both; }
.dc-star { display: inline-block; animation: dc-pop .5s ease .4s both; }
/* 휴대폰: 비교 표는 과거 지연율 칸과 막대를 숨기고 편명·시각·확률·단계만 */
@media (max-width: 640px) {
  .dc-cmp-row, .dc-cmp-head { grid-template-columns: 22px 1.6fr 1fr .9fr .9fr !important; gap: 8px !important; padding-left: 12px !important; padding-right: 12px !important; }
  .dc-cmp-row > :nth-child(4), .dc-cmp-head > :nth-child(4), .dc-cmp-row > :nth-child(5) > :first-child { display: none !important; }
}
/* 조회 기록 카드도 차례로 올라온다 */
[data-testid="stVerticalBlockBorderWrapper"]:has(.dc-hist) { animation: dc-up .5s ease both; transition: transform .2s, box-shadow .2s; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.dc-hist):hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(11,37,69,.10); }
/* 페이지 큰 제목 */
.dc-h1 { animation: dc-up .55s ease both; }

/* 움직임 줄이기를 켠 사람에게는 애니메이션을 모두 끈다 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
"""


def inject_css() -> None:
    zoom = "zoom: 1.12;" if st.session_state.get("big_text") else ""
    st.markdown(CSS % {"fonts": FONTS, "bg": BG, "navy": NAVY, "amber": AMBER, "zoom": zoom}, unsafe_allow_html=True)


def reset_search() -> None:
    for k in ("view", "result", "flight_no", "dep_date", "dep_time", "notfound_no"):
        st.session_state.pop(k, None)


def header(active: str) -> None:
    """active: home / compare / history / login / signup"""
    user = st.session_state.get("user")
    with st.container(key="topbar"):
        c_logo, c_nav, c_size, c_user = st.columns([1.8, 3.6, 1.1, 1.7], vertical_alignment="center")
        with c_logo:
            if st.button("DELAYCHECK", key="logo", help="처음 화면으로"):
                reset_search()
                st.switch_page(PAGES["home"])
        with c_nav:
            with st.container(key="nav", horizontal=True, gap="small"):
                for key, label, icon in (("home", "지연 예측", ":material/schedule:"),
                                         ("compare", "편 비교", ":material/compare_arrows:"),
                                         ("history", "조회 기록", ":material/history:")):
                    with st.container(key="nav_active" if key == active else f"nav_{key}"):
                        st.page_link(PAGES[key], label=label, icon=icon)
        with c_size:
            big = st.toggle("큰 글자", value=st.session_state.get("big_text", False), key="big_toggle")
            if big != st.session_state.get("big_text", False):
                st.session_state["big_text"] = big
                st.rerun()
        with c_user:
            if user:
                a, b = st.columns([1.2, 1], vertical_alignment="center")
                a.markdown(f"**{user['name']}님**")
                if b.button("로그아웃", key="logout"):
                    st.session_state.pop("user", None)
                    reset_search()
                    st.switch_page(PAGES["home"])
            else:
                a, b = st.columns(2)
                with a:
                    st.page_link(PAGES["login"], label="로그인")
                with b:
                    st.page_link(PAGES["signup"], label="회원가입")


def footer() -> None:
    st.markdown(f"""
    <div style="margin-top:48px;background:{NAVY};color:#B9C6DA;border-radius:18px 18px 0 0;padding:26px 28px 32px;font-size:14px;line-height:1.7">
      <div style="font-family:'Montserrat',sans-serif;font-style:italic;font-weight:900;font-size:22px;color:#fff">DELAY<span style="color:{AMBER}">CHECK</span></div>
      데이터 출처: 항공정보포털시스템(국토교통부) · 기상청 기상자료개방포털(공항기상관측 AMOS) · 기상청 단기예보 조회서비스<br>
      예측 결과는 과거 운항 기록과 날씨 예보로 계산한 참고 정보예요. 실제 출발 시각은 항공사 안내를 확인하세요.
    </div>""", unsafe_allow_html=True)
