"""시간대별 지연 비율 막대그래프 (Altair, Streamlit에 기본 포함)."""
from __future__ import annotations

import altair as alt
import pandas as pd


def hourly_chart(hourly: dict[int, float], highlight: int | None = None, height: int = 180,
                 high_color: str = "#FFB81C", mark_extremes: bool = False) -> alt.Chart:
    df = pd.DataFrame({"시": list(hourly.keys()), "지연비율": [v * 100 for v in hourly.values()]})
    df["시각"] = df["시"].map(lambda h: f"{h}시")                  # 마우스를 올리면 나오는 말풍선용
    df["비율"] = df["지연비율"].map(lambda v: f"{v:.1f}%")
    if mark_extremes:
        hi, lo = df.loc[df["지연비율"].idxmax(), "시"], df.loc[df["지연비율"].idxmin(), "시"]
        df["색"] = df["시"].map(lambda h: "#C2410C" if h == hi else ("#1D5FD1" if h == lo else "#9DB0CB"))
        label = "datum.value + '시'"                                # 넓은 홈 그래프는 모든 시각을 적는다
    else:
        df["색"] = df["시"].map(lambda h: high_color if h == highlight else "#9DB0CB")
        # 좁은 결과 카드: 0·6·12·18·23시 + 내 출발 시각. 내 시각과 2시간 안으로 붙는 기준 시각은 빼서 글자가 겹치지 않게
        shown = [h for h in (0, 6, 12, 18, 23) if highlight is None or abs(h - highlight) > 2]
        shown += [highlight] if highlight is not None else []
        label = f"indexof({sorted(shown)}, datum.value) >= 0 ? datum.value + '시' : ''"
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("시:O", title=None, axis=alt.Axis(labelAngle=0, labelExpr=label, ticks=False, domainColor="#8A9BB5",
                                                      labelColor="#4A5568", labelFontSize=12, labelOverlap=False)),
            y=alt.Y("지연비율:Q", title=None, axis=None),
            color=alt.Color("색:N", scale=None),
            tooltip=[alt.Tooltip("시각:N", title="출발"), alt.Tooltip("비율:N", title="평균 지연")],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure(background="#FFFFFF")              # 카드와 같은 흰색 (PNG로 내려받아도 배경이 비지 않게)
    )
