"""시간대별 지연 비율 막대그래프 (Altair, Streamlit에 기본 포함)."""
from __future__ import annotations

import altair as alt
import pandas as pd


def hourly_chart(hourly: dict[int, float], highlight: int | None = None, height: int = 180,
                 high_color: str = "#FFB81C", mark_extremes: bool = False) -> alt.Chart:
    df = pd.DataFrame({"시": list(hourly.keys()), "지연비율": [v * 100 for v in hourly.values()]})
    if mark_extremes:
        hi, lo = df.loc[df["지연비율"].idxmax(), "시"], df.loc[df["지연비율"].idxmin(), "시"]
        df["색"] = df["시"].map(lambda h: "#C2410C" if h == hi else ("#1D5FD1" if h == lo else "#9DB0CB"))
    else:
        df["색"] = df["시"].map(lambda h: high_color if h == highlight else "#9DB0CB")
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("시:O", title=None, axis=alt.Axis(labelAngle=0, labelExpr="(datum.value % 6 == 0 || datum.value == 23) ? datum.value + '시' : ''",
                                                      ticks=False, domainColor="#8A9BB5", labelColor="#4A5568", labelFontSize=12)),
            y=alt.Y("지연비율:Q", title=None, axis=None),
            color=alt.Color("색:N", scale=None),
            tooltip=[alt.Tooltip("시:O", title="출발 시각(시)"), alt.Tooltip("지연비율:Q", title="평균 지연 비율(%)", format=".1f")],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0)
    )
