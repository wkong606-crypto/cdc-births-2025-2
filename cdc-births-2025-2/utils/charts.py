"""Visualization builders using Plotly for the CDC Natality Dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List
from .data_loader import MONTH_ORDER

# Accessible, high-contrast, colorblind-friendly palette
COLOR_MALE = "#2b5c8f"    # Deep Slate Blue
COLOR_FEMALE = "#e07a5f"  # Warm Terracotta
COLOR_TOTAL = "#1f77b4"   # Primary Accent Blue

CHART_THEME = "plotly_white"


def create_monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create a monthly birth trend line & area chart with formatted tooltips."""
    # Group by month and preserve chronological order
    monthly_data = (
        df.groupby("Month", observed=False)["Births"]
        .sum()
        .reindex(MONTH_ORDER)
        .dropna()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly_data["Month"],
            y=monthly_data["Births"],
            mode="lines+markers",
            name="Total Births",
            line=dict(color=COLOR_TOTAL, width=3),
            marker=dict(size=8, color=COLOR_TOTAL),
            hovertemplate="<b>%{x}</b><br>Total Births: %{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Total Monthly Births (2025 Provisional)</b><br><sup>Chronological trend across all selected records</sup>",
        xaxis=dict(title="Calendar Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(
            title="Total Births (Count)",
            rangemode="tozero",  # Avoid deceptive axis truncation
            tickformat=",.0f",
        ),
        template=CHART_THEME,
        hovermode="x unified",
        margin=dict(l=40, r=40, t=70, b=40),
        height=420,
    )
    return fig


def create_sex_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart comparing Female and Male births across months."""
    sex_monthly = (
        df.groupby(["Month", "Sex of Infant"], observed=False)["Births"]
        .sum()
        .reset_index()
    )

    # Filter to months present in dataset
    sex_monthly = sex_monthly[sex_monthly["Month"].isin(MONTH_ORDER)]

    fig = go.Figure()

    # Female trace
    female_data = sex_monthly[sex_monthly["Sex of Infant"] == "Female"]
    if not female_data.empty:
        fig.add_trace(
            go.Bar(
                x=female_data["Month"],
                y=female_data["Births"],
                name="Female",
                marker_color=COLOR_FEMALE,
                hovertemplate="<b>Female - %{x}</b><br>Births: %{y:,.0f}<extra></extra>",
            )
        )

    # Male trace
    male_data = sex_monthly[sex_monthly["Sex of Infant"] == "Male"]
    if not male_data.empty:
        fig.add_trace(
            go.Bar(
                x=male_data["Month"],
                y=male_data["Births"],
                name="Male",
                marker_color=COLOR_MALE,
                hovertemplate="<b>Male - %{x}</b><br>Births: %{y:,.0f}<extra></extra>",
            )
        )

    fig.update_layout(
        title="<b>Births by Infant Sex Across Months</b><br><sup>Comparison between male and female provisional birth counts</sup>",
        barmode="group",
        xaxis=dict(title="Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(
            title="Birth Count",
            rangemode="tozero",  # Start at 0
            tickformat=",.0f",
        ),
        template=CHART_THEME,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=70, b=40),
        height=420,
    )
    return fig


def create_state_ranking_chart(df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart ranking selected states by birth count."""
    geo_data = (
        df.groupby("State of Residence")["Births"]
        .sum()
        .reset_index()
        .sort_values(by="Births", ascending=True)  # Ascending for bottom-to-top horizontal bar
    )

    # Dynamically adjust height depending on number of states selected
    chart_height = max(400, len(geo_data) * 22)

    fig = go.Figure(
        go.Bar(
            x=geo_data["Births"],
            y=geo_data["State of Residence"],
            orientation="h",
            marker=dict(
                color=geo_data["Births"],
                colorscale="Blues",
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Selected Births: %{x:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Geographic Ranking by Birth Count</b><br><sup>States sorted from lowest to highest within current selection (zero baseline)</sup>",
        xaxis=dict(
            title="Total Birth Count",
            rangemode="tozero",
            tickformat=",.0f",
        ),
        yaxis=dict(title="", tickfont=dict(size=11)),
        template=CHART_THEME,
        margin=dict(l=140, r=40, t=70, b=40),
        height=chart_height,
    )
    return fig


def create_us_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """Create an interactive US choropleth map showing birth counts by state."""
    state_totals = (
        df.groupby(["State of Residence", "State Code"])["Births"]
        .sum()
        .reset_index()
    )

    fig = go.Figure(
        go.Choropleth(
            locations=state_totals["State Code"],
            z=state_totals["Births"],
            locationmode="USA-states",
            colorscale="Viridis",
            marker_line_color="white",
            marker_line_width=1,
            colorbar=dict(
                title="Births",
                tickformat=",.0f",
                thickness=15,
                len=0.7,
            ),
            customdata=state_totals["State of Residence"],
            hovertemplate="<b>%{customdata} (%{location})</b><br>Births: %{z:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Geographic Distribution of Births across the United States</b><br><sup>Counts represent raw totals (higher values generally reflect larger state populations)</sup>",
        geo=dict(
            scope="usa",
            projection=dict(type="albers usa"),
            showlakes=True,
            lakecolor="rgb(240, 248, 255)",
        ),
        template=CHART_THEME,
        margin=dict(l=20, r=20, t=70, b=20),
        height=520,
    )
    return fig


def create_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create an interactive state-by-month heatmap matrix."""
    pivot = df.pivot_table(
        index="State of Residence",
        columns="Month",
        values="Births",
        aggfunc="sum",
        observed=False,
    )

    # Reindex columns to standard chronological order
    active_months = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[active_months]

    # Sort states by annual total descending for intuitive inspection
    state_order = pivot.sum(axis=1).sort_values(ascending=False).index.tolist()
    pivot = pivot.loc[state_order]

    chart_height = max(450, len(pivot) * 20)

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=active_months,
            y=pivot.index.tolist(),
            colorscale="YlGnBu",
            colorbar=dict(title="Births", tickformat=",.0f", len=0.8),
            hovertemplate="<b>State:</b> %{y}<br><b>Month:</b> %{x}<br><b>Births:</b> %{z:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>State-by-Month Natality Matrix</b><br><sup>Heatmap showing seasonality and birth volumes across jurisdictions</sup>",
        xaxis=dict(title="Calendar Month", tickangle=0),
        yaxis=dict(title="", autorange="reversed", tickfont=dict(size=10)),
        template=CHART_THEME,
        margin=dict(l=140, r=40, t=70, b=40),
        height=chart_height,
    )
    return fig


def create_top_bottom_comparison(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """Create a comparative chart showing the top N and bottom N states."""
    geo_totals = (
        df.groupby("State of Residence")["Births"]
        .sum()
        .reset_index()
        .sort_values(by="Births", ascending=False)
    )

    if len(geo_totals) < (2 * n):
        n = max(1, len(geo_totals) // 2)

    top_states = geo_totals.head(n).copy()
    top_states["Group"] = f"Top {n} States"

    bottom_states = geo_totals.tail(n).copy().sort_values(by="Births", ascending=True)
    bottom_states["Group"] = f"Bottom {n} States"

    combined = pd.concat([top_states, bottom_states])

    fig = go.Figure()

    # Top group trace
    fig.add_trace(
        go.Bar(
            x=top_states["State of Residence"],
            y=top_states["Births"],
            name=f"Top {n} (Highest Volume)",
            marker_color="#1b4965",
            hovertemplate="<b>%{x}</b><br>Births: %{y:,.0f}<extra></extra>",
        )
    )

    # Bottom group trace
    fig.add_trace(
        go.Bar(
            x=bottom_states["State of Residence"],
            y=bottom_states["Births"],
            name=f"Bottom {n} (Lowest Volume)",
            marker_color="#62b6cb",
            hovertemplate="<b>%{x}</b><br>Births: %{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"<b>Comparison: Top {n} vs. Bottom {n} Geographies</b><br><sup>Highlights volume disparities (reflecting base population scale)</sup>",
        xaxis=dict(title="Geography"),
        yaxis=dict(
            title="Total Birth Count",
            rangemode="tozero",
            tickformat=",.0f",
        ),
        template=CHART_THEME,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=70, b=40),
        height=420,
    )
    return fig


def create_sex_ratio_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create a line chart showing the percentage of male vs female births across months.

    Demonstrates biological stability (~51.2% male to 48.8% female).
    """
    sex_pivot = df.pivot_table(
        index="Month",
        columns="Sex of Infant",
        values="Births",
        aggfunc="sum",
        observed=False,
    )

    active_months = [m for m in MONTH_ORDER if m in sex_pivot.index]
    sex_pivot = sex_pivot.reindex(active_months)

    if "Male" not in sex_pivot.columns or "Female" not in sex_pivot.columns:
        return go.Figure()

    sex_pivot["Total"] = sex_pivot["Male"] + sex_pivot["Female"]
    sex_pivot["Male Pct"] = (sex_pivot["Male"] / sex_pivot["Total"]) * 100
    sex_pivot["Female Pct"] = (sex_pivot["Female"] / sex_pivot["Total"]) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=sex_pivot.index,
            y=sex_pivot["Male Pct"],
            mode="lines+markers",
            name="Male %",
            line=dict(color=COLOR_MALE, width=2.5),
            marker=dict(size=7),
            hovertemplate="<b>%{x} (Male)</b>: %{y:.2f}%<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=sex_pivot.index,
            y=sex_pivot["Female Pct"],
            mode="lines+markers",
            name="Female %",
            line=dict(color=COLOR_FEMALE, width=2.5),
            marker=dict(size=7),
            hovertemplate="<b>%{x} (Female)</b>: %{y:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Sex Proportion Distribution by Month</b><br><sup>Illustrates biological consistency (~51.2% male, ~48.8% female)</sup>",
        xaxis=dict(title="Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(
            title="Share of Total Births (%)",
            range=[40, 60],
            ticksuffix="%",
        ),
        template=CHART_THEME,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=70, b=40),
        height=380,
    )
    return fig
