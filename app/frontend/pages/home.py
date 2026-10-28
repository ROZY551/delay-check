"""1. 홈 → 2·3. 결과 → 4. 등록되지 않은 편명 (한 페이지 안에서 상태로 바꿔 보여준다)."""
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components

from backend.weather import KST
from backend.services import get_predictor, run_prediction, today_kst
from frontend.components import cards
from frontend.components.charts import hourly_chart
from frontend.components.hero import DATA_PERIOD, hero_html, hour_kr
from frontend.components.style import footer, header

p = get_predictor()
header("home")
view = st.session_state.get("view", "home")


def search_form(error: str = "") -> None:
    today = today_kst()
    if "dep_time" not in st.session_state:
        nxt = (datetime.now(KST) + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        st.session_state["dep_time"] = nxt.time()
    d = st.session_state.get("dep_date")
    if d is None or not (today <= d <= today + timedelta(days=3)):
        st.session_state["dep_date"] = today
    with st.container(key="search_card"):
        a, b = st.columns([1, 1], vertical_alignment="center")
        a.markdown('<span style="background:#0B2545;color:#fff;border-radius:999px;padding:7px 16px;font-size:15px;font-weight:700">편명으로 조회</span>', unsafe_allow_html=True)
        b.markdown('<div style="text-align:right;font-size:15px;color:#4A5568">출발 날짜는 오늘 ~ 3일 뒤 중에서 고를 수 있어요</div>', unsafe_allow_html=True)
        with st.form("search", border=False):
            c1, c2, c3, c4 = st.columns([1.3, 1, 0.8, 0.9], vertical_alignment="bottom")
            c1.text_input("편명", key="flight_no", placeholder="예: KE705")
            c2.date_input("출발 날짜", key="dep_date", min_value=today,
                          max_value=today + timedelta(days=3), format="YYYY-MM-DD")
            c3.time_input("출발 시각", key="dep_time", step=timedelta(minutes=5))
            go = c4.form_submit_button("지연 확률 확인", type="primary", use_container_width=True)
        if error:
            st.error(error, icon=":material/error:")
    if go:
        no = st.session_state.get("flight_no", "").strip()
        if not no:
            st.toast("편명을 입력해 주세요.")
            return
        with st.spinner("기상청 예보를 불러와 지연 확률을 계산하고 있어요…"):
            result = run_prediction(no, st.session_state["dep_date"], st.session_state["dep_time"])
        if result is None:
            st.session_state.update(view="notfound", notfound_no=no.upper())
        else:
            st.session_state.update(view="result", result=result)
        st.rerun()


def back_to_search() -> None:
    st.session_state["view"] = "home"


def use_example(code: str) -> None:
    st.session_state["flight_no"] = code
    st.session_state["view"] = "home"


# ---------------- 결과 ----------------
if view == "result" and st.session_state.get("result"):
    r = st.session_state["result"]
    st.button("← 다시 조회", on_click=back_to_search)
    st.markdown(cards.summary_card(r), unsafe_allow_html=True)
    if r["weather"].get("출처") == "월평균":
        st.info("기상청 예보를 불러오지 못해 이 달의 평균 날씨로 계산했어요. 잠시 뒤 다시 조회해 보세요.", icon=":material/cloud_off:")
    if r.pop("saved", False):          # 알림은 처음 한 번만
        st.toast("조회 기록에 저장했어요.", icon=":material/history:")
    elif not st.session_state.get("user"):
        st.caption("로그인하면 조회한 항공편이 기록에 저장돼요.")

    st.markdown('<h2 style="margin:26px 0 12px;font-size:22px;font-weight:900;color:#0B2545">자세히 보기</h2>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(cards.weather_card(r["weather"]), unsafe_allow_html=True)
    c2.markdown(cards.factors_card(r["factors"]), unsafe_allow_html=True)
    with c3.container(key="chart_card"):
        st.markdown(cards.chart_title(r["dep"].hour, r["hour_rate"], p.prior), unsafe_allow_html=True)
        color = "#C2410C" if r["level"] == "높음" else "#FFB81C"
        st.altair_chart(hourly_chart(p.hourly, r["dep"].hour, height=130, high_color=color), use_container_width=True)
    st.caption("예측 결과는 과거 운항 기록과 기상청 예보로 계산한 참고 정보예요. 실제 출발 시각은 항공사 안내를 확인하세요.")

# ---------------- 등록되지 않은 편명 ----------------
elif view == "notfound":
    st.markdown('<div style="height:96px"></div>', unsafe_allow_html=True)   # 조회 카드가 위로 겹쳐 올라오는 만큼 띄우기
    search_form(error=f"‘{st.session_state.get('notfound_no', '')}’은(는) 등록되지 않은 편명이에요.")
    st.markdown("""
<div class="card" style="margin-top:20px">
<h1 style="margin:0 0 6px;font-size:24px;font-weight:900;display:flex;align-items:center;gap:10px">
<span class="dc-shake" style="width:38px;height:38px;border-radius:10px;background:#E8590C;color:#fff;display:flex;align-items:center;justify-content:center">!</span>이 편명은 학습한 운항 기록에 없어요</h1>
<p style="margin:0 0 10px;color:#4A5568">아래 내용을 확인한 뒤 다시 입력해 주세요.</p>
<ol style="margin:0;padding-left:22px;line-height:1.9;font-size:16px">
<li><b>편명 형식</b> — 항공사 코드 2자리 + 숫자예요. 탑승권이나 전자항공권(e-티켓)의 ‘편명’ 칸에 적혀 있어요.</li>
<li><b>인천공항 출발편만</b> 조회돼요. 도착편이나 김포·김해 출발편은 예측할 수 없어요.</li>
<li><b>새로 생긴 노선</b>은 아직 예측하지 못해요. 2025년 9월 ~ 2026년 9월에 운항한 편명 2,360개만 조회할 수 있어요.</li>
</ol></div>""", unsafe_allow_html=True)
    st.markdown("**이렇게 입력해요**")
    e1, e2, e3, _ = st.columns([1, 1, 1, 1.2])
    for col, code, label in ((e1, "KE705", "대한항공 · 도쿄/나리타"), (e2, "7C1301", "제주항공 · 간사이"), (e3, "TW205", "트리니티항공 · 후쿠오카")):
        col.button(f"{code} · {label}", key=f"ex_{code}", on_click=use_example, args=(code,), use_container_width=True)

# ---------------- 홈 ----------------
else:
    st.markdown('<p class="dc-up" style="margin:0 0 12px;background:#fff;border-radius:10px;padding:11px 18px;font-size:15px;color:#1C2B40">'
                '<b style="color:#0B2545">[안내]</b>&nbsp; 출발 시각의 날씨는 기상청 단기예보로 자동 반영돼요.</p>', unsafe_allow_html=True)
    components.html(hero_html(p.hourly), height=476)
    search_form()

    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    with st.container(key="chart_card", border=False):
        hi = max(p.hourly, key=p.hourly.get)
        lo = min(p.hourly, key=p.hourly.get)
        st.markdown(cards._title("시간대별 평균 지연 비율", "#0E9384", cards.ICON_BARS)
                    + f'<span style="font-size:15px;color:#4A5568">인천공항 출발편 {DATA_PERIOD} · 전체 평균 {p.prior*100:.1f}% · '
                      f'<b style="color:#C2410C">■</b> 가장 높음 {hour_kr(hi)} {p.hourly[hi]*100:.1f}% · '
                      f'<b style="color:#1D5FD1">■</b> 가장 낮음 {hour_kr(lo)} {p.hourly[lo]*100:.1f}%</span>',
                    unsafe_allow_html=True)
        st.altair_chart(hourly_chart(p.hourly, mark_extremes=True, height=170), use_container_width=True)

    st.markdown("""
<div class="card" style="margin-top:24px">
<h2 style="margin:0 0 16px;font-size:24px;font-weight:900">이용 안내</h2>
<div style="display:flex;flex-wrap:wrap;gap:24px">
<div class="dc-up" style="animation-delay:.1s;flex:1 1 240px"><b style="font-size:18px">① 편명·날짜·시각 입력</b><br><span style="color:#4A5568">항공사와 목적지는 편명으로 자동 조회돼요</span></div>
<div class="dc-up" style="animation-delay:.25s;flex:1 1 240px"><b style="font-size:18px">② 날씨 자동 반영</b><br><span style="color:#4A5568">출발 3일 이내라 기상청 예보를 바로 불러와요</span></div>
<div class="dc-up" style="animation-delay:.4s;flex:1 1 240px"><b style="font-size:18px">③ 지연 확률 확인</b><br><span style="color:#4A5568">시간대·과거 기록·날씨를 함께 계산해요</span></div>
</div></div>""", unsafe_allow_html=True)

footer()
