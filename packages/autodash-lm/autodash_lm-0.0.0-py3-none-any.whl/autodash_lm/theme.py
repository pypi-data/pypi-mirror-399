from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Theme:
    dark: bool = True
    background: str = "#0B0F19"
    surface: str = "#111827"
    text: str = "#E5E7EB"
    muted_text: str = "#9CA3AF"
    accent: str = "#60A5FA"
    good: str = "#34D399"
    warn: str = "#FBBF24"
    bad: str = "#F87171"
    chart_palette: tuple[str, ...] = (
        "#60A5FA", "#34D399", "#FBBF24", "#F87171", "#A78BFA", "#F472B6", "#22D3EE"
    )

    def plotly_template(self) -> Dict[str, Any]:
        return {
            "layout": {
                "paper_bgcolor": self.background,
                "plot_bgcolor": self.surface,
                "font": {"color": self.text},
                "colorway": list(self.chart_palette),
                "xaxis": {"gridcolor": "rgba(255,255,255,0.08)", "zerolinecolor": "rgba(255,255,255,0.10)"},
                "yaxis": {"gridcolor": "rgba(255,255,255,0.08)", "zerolinecolor": "rgba(255,255,255,0.10)"},
                "legend": {"bgcolor": "rgba(0,0,0,0)"},
                "margin": {"l": 40, "r": 20, "t": 55, "b": 40},
            }
        }


def default_theme(dark: bool = True) -> Theme:
    if dark:
        return Theme(dark=True)
    return Theme(
        dark=False,
        background="#F8FAFC",
        surface="#FFFFFF",
        text="#0F172A",
        muted_text="#475569",
        accent="#2563EB",
        chart_palette=("#2563EB", "#16A34A", "#D97706", "#DC2626", "#7C3AED", "#DB2777", "#0891B2"),
    )