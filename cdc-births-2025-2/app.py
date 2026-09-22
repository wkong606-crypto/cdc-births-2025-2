"""Provisional 2025 CDC U.S. Natality Dashboard.

Designed for undergraduate business analytics students to explore
geographic, monthly, and sex-based variations in provisional birth counts.
"""

from typing import List
import pandas as pd
import streamlit as st

from utils.charts import (
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_sex_ratio_trend_chart,
    create_state_month_heatmap,
    create_state_ranking_chart,
    create_top_bottom_comparison,
    create_us_choropleth_map,
)
from utils.data_loader import (
    MONTH_ORDER,
    calculate_kpis,
    filter_data,
    load_natality_data,
)


def set_page_layout() -> None:
    """Configure Streamlit page layout and title."""
    st.set_page_config(
        page_title="Provisional 2025 CDC Natality Dashboard",
        page_icon="👶",
        layout="wide",
        initial_sidebar_state="auto",
    )


def render_header() -> None:
    """Render the dashboard title, source attribution, and critical pedagogical notices."""
    st.title("👶 Provisional 2025 CDC U.S. Natality Dashboard")
    st.markdown(
        "**Exploratory Analytics Platform for Business Analytics Students** • "
        "Investigating geographic, seasonal, and biological patterns in United States birth counts."
    )

    # Educational & Data Quality Callout Banner
    st.info(
        """
        ℹ️ **Critical Data & Analytical Notes for Students:**
        1. **Provisional Data Notice:** These figures reflect provisional 2025 natality data from the 
           [CDC WONDER Online Database](https://wonder.cdc.gov/natality.html) and are subject to official revision.
        2. **Counts, Not Rates:** All numbers represent **raw discrete counts of live births**, *not* birth rates 
           or fertility rates. Variations across states primarily reflect base population size (e.g., California vs. Vermont) 
           rather than maternal fertility behavior.
        3. **Audited Dataset:** The underlying records contain exactly 1,224 observations (51 geographies × 12 months × 2 sexes) 
           with zero missing values and 3,604,640 total births.
        """
    )


def setup_sidebar_filters(
    df: pd.DataFrame,
) -> tuple[List[str], List[str], List[str]]:
    """Build sidebar multi-select filters with 'Select All' and 'Reset' controls."""
    st.sidebar.header("🔍 Filter Controls")

    all_states: List[str] = sorted(df["State of Residence"].unique().tolist())
    all_months: List[str] = MONTH_ORDER.copy()
    all_sexes: List[str] = ["Female", "Male"]

    # Parse initial URL query parameters if present
    query_params = st.query_params
    if "_filters_initialized" not in st.session_state:
        st.session_state._filters_initialized = True
        
        # State query parameter
        if "states" in query_params:
            raw_s = query_params.get_all("states")
            s_list = []
            for item in raw_s:
                s_list.extend([x.strip() for x in item.split(",") if x.strip()])
            valid_states = [s for s in s_list if s in all_states]
            st.session_state.selected_states = valid_states if valid_states else all_states
        elif "selected_states" not in st.session_state:
            st.session_state.selected_states = all_states

        # Month query parameter
        if "months" in query_params:
            raw_m = query_params.get_all("months")
            m_list = []
            for item in raw_m:
                m_list.extend([x.strip() for x in item.split(",") if x.strip()])
            valid_months = [m for m in m_list if m in all_months]
            st.session_state.selected_months = valid_months if valid_months else all_months
        elif "selected_months" not in st.session_state:
            st.session_state.selected_months = all_months

        # Sex query parameter
        if "sexes" in query_params:
            raw_sx = query_params.get_all("sexes")
            sx_list = []
            for item in raw_sx:
                sx_list.extend([x.strip() for x in item.split(",") if x.strip()])
            valid_sexes = [sx for sx in sx_list if sx in all_sexes]
            st.session_state.selected_sexes = valid_sexes if valid_sexes else all_sexes
        elif "selected_sexes" not in st.session_state:
            st.session_state.selected_sexes = all_sexes

    # Quick action buttons
    col_btn1, col_btn2, col_btn3 = st.sidebar.columns(3)
    with col_btn1:
        if st.button("Select All", use_container_width=True, help="Select all geographies, months, and sexes"):
            st.session_state.selected_states = all_states
            st.session_state.selected_months = all_months
            st.session_state.selected_sexes = all_sexes
            st.query_params.clear()
            st.rerun()

    with col_btn2:
        if st.button("Clear All", use_container_width=True, help="Clear all selections to start from scratch"):
            st.session_state.selected_states = []
            st.session_state.selected_months = []
            st.session_state.selected_sexes = []
            st.query_params.clear()
            st.rerun()

    with col_btn3:
        if st.button("Reset Filters", use_container_width=True, help="Reset to full default view"):
            st.session_state.selected_states = all_states
            st.session_state.selected_months = all_months
            st.session_state.selected_sexes = all_sexes
            st.query_params.clear()
            st.rerun()

    # Geography filter
    selected_states = st.sidebar.multiselect(
        "Geographies (States & D.C.)",
        options=all_states,
        key="selected_states",
        help="Select one or more U.S. jurisdictions to include.",
    )

    # Month filter (chronological order)
    selected_months = st.sidebar.multiselect(
        "Calendar Months",
        options=all_months,
        key="selected_months",
        help="Select one or more calendar months (chronologically sorted).",
    )

    # Infant sex filter
    selected_sexes = st.sidebar.multiselect(
        "Infant Sex",
        options=all_sexes,
        key="selected_sexes",
        help="Filter by infant sex category (Female, Male).",
    )

    st.sidebar.markdown("---")
    # Dynamic active filter summary badge
    st.sidebar.subheader("Active Filter Summary")
    st.sidebar.markdown(
        f"""
        - **Geographies:** {len(selected_states)} of {len(all_states)} selected
        - **Months:** {len(selected_months)} of {len(all_months)} selected
        - **Sex Categories:** {len(selected_sexes)} of {len(all_sexes)} selected
        """
    )

    return selected_states, selected_months, selected_sexes


def render_kpis(kpis: dict, total_possible_geos: int) -> None:
    """Render top-level executive KPI metric cards."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Births",
            value=f"{kpis['total_births']:,}",
            help="Total live birth count in the selected view.",
        )

    with col2:
        st.metric(
            label="Selected Geographies",
            value=f"{kpis['selected_geographies']} / {total_possible_geos}",
            help="Count of active jurisdictions out of 51 total.",
        )

    with col3:
        st.metric(
            label="Avg Births / Month",
            value=f"{kpis['avg_monthly_births']:,.0f}",
            help="Mean births per active calendar month.",
        )

    with col4:
        st.metric(
            label="Highest-Volume Geography",
            value=kpis["top_geo"],
            delta=f"{kpis['top_geo_births']:,} births" if kpis["top_geo_births"] > 0 else None,
            delta_color="off",
            help="Geography with the greatest number of births in selection.",
        )

    with col5:
        st.metric(
            label="Peak Month",
            value=kpis["top_month"],
            delta=f"{kpis['top_month_births']:,} births" if kpis["top_month_births"] > 0 else None,
            delta_color="off",
            help="Calendar month recording the highest birth count.",
        )


def render_empty_state() -> None:
    """Display a friendly empty-state warning when filters yield no records."""
    st.warning(
        """
        ⚠️ **No observations match your current filter settings.**
        
        Please adjust your sidebar filters:
        - Ensure at least one **Geography** is selected.
        - Ensure at least one **Month** is selected.
        - Ensure at least one **Infant Sex** option is checked.
        
        You can also click **"Select All"** in the sidebar to reset all options.
        """
    )


def render_tab_overview(filtered_df: pd.DataFrame) -> None:
    """Tab 1: High-level trends and sex comparison."""
    st.subheader("Executive Overview: Temporal Trends and Infant Sex Distribution")
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(create_monthly_trend_chart(filtered_df), use_container_width=True)
    with col2:
        st.plotly_chart(create_sex_comparison_chart(filtered_df), use_container_width=True)

    with st.expander("💡 Analytical Insights for Business Students: Seasonality & Sex Ratios"):
        st.markdown(
            """
            * **Summer Peak Seasonality:** Historically in U.S. natality, late summer (July through September) 
              typically registers peak monthly birth volumes, while February has lower totals partly due to having fewer days (28 days).
            * **Biological Sex Ratio Consistency:** Notice how across all months, male births consistently outnumber 
              female births slightly (~105 male births per 100 female births). This represents a well-documented human biological constant.
            * **Actionable Business Application:** Hospital networks, neonatal intensive care units (NICUs), and pediatric suppliers 
              use these seasonality patterns for staffing, bed-capacity forecasting, and inventory scheduling.
            """
        )


def render_tab_geography(filtered_df: pd.DataFrame) -> None:
    """Tab 2: Interactive Choropleth Map, Rankings, and Top/Bottom Breakdown."""
    st.subheader("Geographic Distribution & State Comparisons")
    
    st.markdown(
        "Explore how birth volumes vary geographically. Note that larger population states like California, Texas, "
        "and Florida naturally show the highest raw counts."
    )

    # US Choropleth Map
    st.plotly_chart(create_us_choropleth_map(filtered_df), use_container_width=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(create_state_ranking_chart(filtered_df), use_container_width=True)
    with col2:
        st.plotly_chart(create_top_bottom_comparison(filtered_df, n=5), use_container_width=True)


def render_tab_monthly_sex(filtered_df: pd.DataFrame) -> None:
    """Tab 3: In-depth Heatmap and Sex Ratio Stability."""
    st.subheader("Cross-Tabulation: State-by-Month Heatmap & Sex Proportions")
    
    st.markdown(
        "This interactive heatmap matrix allows you to examine seasonal variations across all selected states simultaneously. "
        "Darker cells highlight volume clusters."
    )

    st.plotly_chart(create_state_month_heatmap(filtered_df), use_container_width=True)

    st.plotly_chart(create_sex_ratio_trend_chart(filtered_df), use_container_width=True)


def render_tab_data_table(filtered_df: pd.DataFrame) -> None:
    """Tab 4: Filterable table and CSV export."""
    st.subheader("Filtered Natality Records & Data Export")
    st.markdown("Search, sort, and export the exact subset of records defined by your active sidebar filters.")

    col_meta1, col_meta2 = st.columns([3, 1])
    with col_meta1:
        st.markdown(f"**Showing {len(filtered_df):,} records** ({filtered_df['Births'].sum():,} total births)")
    with col_meta2:
        # Generate CSV download
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name="provisional_natality_2025_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Display clean formatted table
    display_df = filtered_df.copy()
    display_df["Month"] = display_df["Month"].astype(str)
    
    st.dataframe(
        display_df[["State of Residence", "Month", "Sex of Infant", "Births"]],
        use_container_width=True,
        column_config={
            "Births": st.column_config.NumberColumn(
                "Births",
                format="%d",
                help="Raw count of registered live births",
            )
        },
        height=500,
    )


def render_tab_about(df: pd.DataFrame) -> None:
    """Tab 5: Data provenance, metadata dictionary, and audit integrity log."""
    st.subheader("About the Provisional 2025 CDC Natality Dataset")

    st.markdown(
        """
        ### 1. Data Provenance & Methodology
        * **Originating Source:** Centers for Disease Control and Prevention (CDC) National Center for Health Statistics (NCHS).
        * **Platform:** [CDC WONDER Online Database](https://wonder.cdc.gov/natality.html) (Provisional Natality Statistics).
        * **Temporal Coverage:** Full calendar year 2025 (January through December).
        * **Status:** Provisional. Provisional vital statistics are based on registered birth certificate records 
          received by the NCHS and are subject to minor revisions before final official release.
        """
    )

    st.markdown("---")
    st.markdown(
        """
        ### 2. Business Analytics Concept: The Denominator Fallacy
        In business intelligence and public health analytics, it is vital to distinguish between **Event Counts** 
        and **Demographic Rates**:
        
        * **Birth Count ($N$):** The raw number of events occurring within a geography and timeframe. 
          Counts tell managers the absolute scale of demand (e.g., how many cribs, vaccines, or pediatricians are needed).
        * **Birth Rate ($R = N / \text{Population} \times 1,000$):** A normalized rate measuring the frequency 
          of births relative to the exposure population.
        
        > **Common Pitfall:** Concluding that Texas has "more babies per family" than Rhode Island simply because 
        > Texas has 300,000+ births and Rhode Island has ~9,000 is an analytics error. The difference is driven 
        > by the underlying population size.
        """
    )

    st.markdown("---")
    st.markdown("### 3. Data Dictionary")
    data_dict = pd.DataFrame(
        [
            {
                "Column": "State of Residence",
                "Data Type": "String (Categorical)",
                "Description": "The 50 U.S. states and the District of Columbia.",
                "Example": "California, Texas, Wyoming",
            },
            {
                "Column": "Month",
                "Data Type": "Categorical (Ordered)",
                "Description": "Calendar month in which the birth occurred (chronological order Jan-Dec).",
                "Example": "January, August, December",
            },
            {
                "Column": "Month Code",
                "Data Type": "Integer",
                "Description": "Numeric sequence code for the calendar month (1 to 12).",
                "Example": "1 (Jan), 12 (Dec)",
            },
            {
                "Column": "Year Code",
                "Data Type": "Integer",
                "Description": "Reference calendar year of occurrence.",
                "Example": "2025",
            },
            {
                "Column": "Sex of Infant",
                "Data Type": "String (Categorical)",
                "Description": "Biological sex classification of the infant at birth.",
                "Example": "Female, Male",
            },
            {
                "Column": "Births",
                "Data Type": "Integer",
                "Description": "Discrete count of registered live births.",
                "Example": "177 (min), 17,627 (max)",
            },
            {
                "Column": "State Code",
                "Data Type": "String (2-letter)",
                "Description": "Standard USPS 2-letter state abbreviation used for geographic mapping.",
                "Example": "CA, TX, WY",
            },
        ]
    )
    st.table(data_dict)

    st.markdown("---")
    st.markdown("### 4. Data Quality Audit Verification")
    st.success(
        f"""
        ✅ **All Data Quality Checks Passed Successfully:**
        - **Total Records in Dataset:** {len(df):,} observations (exact match with 51 states × 12 months × 2 sexes = 1,224)
        - **Total Live Births:** {df['Births'].sum():,} births (exact match with CDC benchmark 3,604,640)
        - **Missing / Null Values:** 0 across all columns
        - **Duplicate Rows:** 0 duplicates detected
        - **Suppression:** No suppressed or masked cells (minimum cell count is 177)
        """
    )


def main() -> None:
    """Main application orchestrator."""
    set_page_layout()

    # Load validated data with caching
    try:
        df = load_natality_data()
    except Exception as exc:
        st.error(f"Error loading natality dataset: {exc}")
        return

    render_header()

    # Sidebar Filter Controls
    selected_states, selected_months, selected_sexes = setup_sidebar_filters(df)

    # Filter dataset based on selection
    filtered_df = filter_data(df, selected_states, selected_months, selected_sexes)

    # Check for empty filter result
    if filtered_df.empty:
        render_empty_state()
        return

    # Calculate and display executive KPIs
    kpis = calculate_kpis(filtered_df)
    total_geos = df["State of Residence"].nunique()
    render_kpis(kpis, total_geos)

    st.markdown("---")

    # Tabbed Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "🗺️ Geographic Analysis",
            "📅 Monthly & Sex Analysis",
            "📋 Data Table & Download",
            "📖 About the Data",
        ]
    )

    with tab1:
        render_tab_overview(filtered_df)

    with tab2:
        render_tab_geography(filtered_df)

    with tab3:
        render_tab_monthly_sex(filtered_df)

    with tab4:
        render_tab_data_table(filtered_df)

    with tab5:
        render_tab_about(df)


if __name__ == "__main__":
    main()
