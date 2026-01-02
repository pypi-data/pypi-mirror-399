from __future__ import annotations

from typing import Optional

import pandas as pd
from dash import dcc, html, Input, Output

from .theme import default_theme
from .utils import load_table, infer_column_types
from .profiling import build_profile
from .builder import (
    fig_missingness,
    fig_numeric_distribution,
    fig_categorical_counts,
    fig_corr_heatmap,
    pick_interesting_numeric,
    pick_interesting_categorical,
)


def _in_notebook() -> bool:
    try:
        from IPython import get_ipython  # type: ignore
        ip = get_ipython()
        if ip is None:
            return False
        # Works for Colab and Jupyter
        return True
    except Exception:
        return False


def show_dashboard(
    path: str,
    dark: bool = True,
    mode: str = "inline",
    host: str = "0.0.0.0",
    port: int = 8050,
    height: int = 900,
) -> None:
    """
    mode:
      - "inline": render inside notebook (recommended for Colab)
      - "external": open in a new browser tab/window
    """
    df = load_table(path)
    numeric_cols, cat_cols, dt_cols = infer_column_types(df)
    theme = default_theme(dark=dark)
    profile = build_profile(df, numeric_cols, cat_cols)

    interesting_numeric = pick_interesting_numeric(df, numeric_cols)
    interesting_cat = pick_interesting_categorical(df, cat_cols)

    # Use JupyterDash in notebooks, regular Dash otherwise
    if _in_notebook():
        from jupyter_dash import JupyterDash  # type: ignore
        app = JupyterDash(__name__)
    else:
        from dash import Dash
        app = Dash(__name__)

    app.title = "AutoDash LM"

    container_style = {
        "minHeight": "100vh",
        "backgroundColor": theme.background,
        "color": theme.text,
        "padding": "18px",
        "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial",
    }
    card_style = {
        "backgroundColor": theme.surface,
        "border": f"1px solid rgba(255,255,255,0.08)" if dark else "1px solid rgba(0,0,0,0.08)",
        "borderRadius": "14px",
        "padding": "14px",
        "marginBottom": "14px",
    }
    button_style = {
        "display": "inline-block",
        "padding": "10px 12px",
        "borderRadius": "10px",
        "textDecoration": "none",
        "backgroundColor": theme.accent,
        "color": "#0B0F19" if dark else "white",
        "fontWeight": 800,
    }

    prebuilt_figs = [fig_missingness(df, theme)]
    for c in interesting_numeric[:3]:
        prebuilt_figs.append(fig_numeric_distribution(df, c, theme))
    for c in interesting_cat[:3]:
        prebuilt_figs.append(fig_categorical_counts(df, c, theme))
    if len(numeric_cols) >= 2:
        prebuilt_figs.append(fig_corr_heatmap(df, numeric_cols, theme))

    app.layout = html.Div(
        style=container_style,
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "gap": "12px"},
                children=[
                    html.Div(
                        children=[
                            html.H2("Auto Dashboard", style={"margin": "0 0 6px 0"}),
                            html.Div(
                                f"Rows: {profile.n_rows} | Columns: {profile.n_cols} | File: {path}",
                                style={"color": theme.muted_text},
                            ),
                        ]
                    ),
                    html.A(
                        "Share on GitHub",
                        href="https://github.com/mahdi123-tech",
                        target="_blank",
                        style=button_style,
                    ),
                ],
            ),

            html.Div(
                style=card_style,
                children=[
                    html.H4("Interactive explorer", style={"marginTop": 0}),
                    html.Div(
                        style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                        children=[
                            html.Div(
                                style={"minWidth": "260px", "flex": "1"},
                                children=[
                                    html.Label("Column", style={"color": theme.muted_text}),
                                    dcc.Dropdown(
                                        options=[{"label": c, "value": c} for c in df.columns],
                                        value=df.columns[0] if len(df.columns) else None,
                                        id="col",
                                        style={"color": "#111"},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"minWidth": "260px", "flex": "1"},
                                children=[
                                    html.Label("Chart type", style={"color": theme.muted_text}),
                                    dcc.Dropdown(
                                        options=[
                                            {"label": "Auto (based on dtype)", "value": "auto"},
                                            {"label": "Histogram (numeric)", "value": "hist"},
                                            {"label": "Bar counts (categorical)", "value": "bar"},
                                        ],
                                        value="auto",
                                        id="chart_type",
                                        style={"color": "#111"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dcc.Graph(id="dynamic_graph", style={"height": f"{height}px"}),
                ],
            ),

            html.Div(
                style=card_style,
                children=[
                    html.H4("Descriptive analytics", style={"marginTop": 0}),
                    html.Ul(
                        children=[
                            html.Li(f"Numeric columns: {len(numeric_cols)}"),
                            html.Li(f"Categorical columns: {len(cat_cols)}"),
                            html.Li(f"Datetime columns: {len(dt_cols)}"),
                            html.Li(f"Total missing cells: {int(df.isna().sum().sum())}"),
                        ]
                    ),
                ],
            ),

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(360px, 1fr))",
                    "gap": "14px",
                },
                children=[html.Div(style=card_style, children=[dcc.Graph(figure=f)]) for f in prebuilt_figs],
            ),

            html.Footer(
                style={
                    "marginTop": "18px",
                    "paddingTop": "10px",
                    "borderTop": f"1px solid rgba(255,255,255,0.10)" if dark else "1px solid rgba(0,0,0,0.10)",
                    "color": theme.muted_text,
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "flexWrap": "wrap",
                    "gap": "10px",
                },
                children=[
                    html.Div(
                        children=[
                            html.Span("Powered With Louati Mahdi "),
                            html.Span("❤", style={"color": theme.bad, "fontSize": "16px", "marginLeft": "4px"}),
                        ]
                    ),
                    html.A(
                        "https://github.com/mahdi123-tech",
                        href="https://github.com/mahdi123-tech",
                        target="_blank",
                        style={"color": theme.accent, "textDecoration": "none", "fontWeight": 800},
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("dynamic_graph", "figure"),
        Input("col", "value"),
        Input("chart_type", "value"),
    )
    def _update(col: Optional[str], chart_type: str):
        if not col:
            return {"layout": {"template": theme.plotly_template(), "title": "No column selected"}}

        s = df[col]
        is_numeric = pd.api.types.is_numeric_dtype(s)

        if chart_type == "auto":
            return fig_numeric_distribution(df, col, theme) if is_numeric else fig_categorical_counts(df, col, theme)
        if chart_type == "hist":
            return fig_numeric_distribution(df, col, theme)
        if chart_type == "bar":
            return fig_categorical_counts(df, col, theme)

        return fig_missingness(df, theme)

    # Run: inline in notebooks; external locally
    run_mode = mode
    if not _in_notebook() and mode == "inline":
        run_mode = "external"

    if _in_notebook():
        # JupyterDash supports inline iframe without user port work
        app.run_server(mode=run_mode, host=host, port=port, debug=False)
    else:
        app.run(host=host, port=port, debug=False)