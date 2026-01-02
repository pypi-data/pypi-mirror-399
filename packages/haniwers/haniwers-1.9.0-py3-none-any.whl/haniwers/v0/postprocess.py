"""グラフを作成するモジュール（作成途中）"""

import pandas as pd
import altair as alt


def event_rate(data: pd.DataFrame):
    # イベントレート
    hbars = (
        alt.Chart(data)
        .mark_bar(opacity=0.5, color="grey")
        .encode(
            alt.X("time"),
            alt.Y("event_rate").title("イベントレート [Hz]"),
        )
        .properties(width=1200, height=500)
    )

    # 気温
    marks = (
        alt.Chart(data)
        .mark_point(color="blue")
        .encode(
            alt.X("time"),
            alt.Y("tmp").title("気温 [degC]").scale(domain=[20, 35]),
        )
        .properties(width=1200, height=500)
    )

    layers = alt.layer(hbars, marks).resolve_scale(
        y="independent",
    )
    return layers
