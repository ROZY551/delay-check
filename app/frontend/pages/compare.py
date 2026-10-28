"""5. 편 비교: 같은 목적지로 가는 편들을 그날 날씨로 예측해서 덜 늦는 순서로 보여준다."""
from datetime import timedelta

import streamlit as st

from backend.airports import code_of
from backend.services import day_weather, get_predictor, run_prediction, today_kst
from frontend.components import cards
from frontend.components.style import PAGES, footer, header

p = get_predictor()
header("compare")

st.markdown('<h1 class="dc-h1" style="margin:18px 0 4px;font-size:32px;font-weight:900;color:#0B2545">같은 목적지, 어떤 편이 덜 늦을까요?</h1>'
            '<p style="margin:0 0 16px;font-size:17px;color:#4A5568">목적지와 날짜를 고르면 그날 출발하는 편들의 지연 확률을 한 번에 비교해 드려요.</p>',
            unsafe_allow_html=True)

dests = p.destinations()
today = today_kst()
with st.container(key="form_card"):
    with st.form("compare", border=False):
        c1, c2, c3 = st.columns([1.4, 1, 0.8], vertical_alignment="bottom")
        dest = c1.selectbox("목적지", dests, index=dests.index("도쿄/나리타") if "도쿄/나리타" in dests else 0,
                            format_func=lambda d: f"{code_of(d)}  {d}" if code_of(d) else d, key="cmp_dest")
        day = c2.date_input("출발 날짜", value=today, min_value=today, max_value=today + timedelta(days=3),
                            format="YYYY-MM-DD", key="cmp_day")
        go = c3.form_submit_button("비교하기", type="primary", use_container_width=True)

if go or "cmp_result" in st.session_state:
    if go:
        with st.spinner("편마다 지연 확률을 계산하고 있어요…"):
            weather, err = day_weather(day)
            st.session_state["cmp_result"] = {"dest": dest, "day": day, "items": p.compare(dest, day, weather),
                                              "weather": weather, "err": err}
    res = st.session_state["cmp_result"]
    items = res["items"]
    if not items:
        st.warning("이 목적지로 정기적으로 운항한 여객편이 없어요.")
    else:
        n_avg = sum(it["avg_weather"] for it in items)
        if res["err"]:
            st.info("기상청 예보를 불러오지 못해 이 달의 평균 날씨로 계산했어요.", icon=":material/cloud_off:")
        elif n_avg:
            st.info(f"{n_avg}편은 출발 시각의 예보가 아직 나오지 않아 이 달의 평균 날씨로 계산했어요. "
                    "표에 ‘평균 날씨’라고 표시돼 있어요.", icon=":material/partly_cloudy_day:")
        best = items[0]
        w_best = res["weather"].get(best["dep"].hour, {})
        st.markdown(cards.recommend_banner(best, res["dest"], res["day"], len(items), w_best.get("설명", "월평균 날씨")),
                    unsafe_allow_html=True)
        st.markdown('<div style="height:14px"></div>' + cards.COMPARE_HEAD
                    + "".join(cards.compare_row(i + 1, it) for i, it in enumerate(items[:10])), unsafe_allow_html=True)
        if len(items) > 10:
            with st.expander(f"나머지 {len(items) - 10}편 더 보기"):
                st.markdown("".join(cards.compare_row(i + 11, it) for i, it in enumerate(items[10:])), unsafe_allow_html=True)

        st.markdown("**자세히 볼 편**")
        a, b = st.columns([2, 1], vertical_alignment="bottom")
        pick = a.selectbox("편 선택", [it["flight"]["편명"] for it in items], label_visibility="collapsed",
                           format_func=lambda no: next(f"{no} · {it['flight']['항공사']} · {it['dep']:%H:%M}" for it in items if it["flight"]["편명"] == no))
        if b.button("이 편 자세히 보기", type="primary", use_container_width=True):
            it = next(x for x in items if x["flight"]["편명"] == pick)
            result = run_prediction(pick, res["day"], it["dep"].time())
            st.session_state.update(view="result", result=result, flight_no=pick, dep_date=res["day"], dep_time=it["dep"].time())
            st.switch_page(PAGES["home"])
    st.caption("평소 출발 시각과 과거 지연율은 2025년 9월 ~ 2026년 9월 운항 기록 기준이에요.")

footer()
