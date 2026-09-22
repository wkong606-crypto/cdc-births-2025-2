"""Data loading, validation, and transformation module for CDC Natality 2025."""

from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

# State name to two-letter USPS abbreviation mapping (50 states + DC)
STATE_TO_ABBR: Dict[str, str] = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Chronological order of calendar months
MONTH_ORDER: List[str] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

EXPECTED_ROWS: int = 1224
EXPECTED_GEOGRAPHIES: int = 51
EXPECTED_MONTHS: int = 12
EXPECTED_SEXES: int = 2
EXPECTED_TOTAL_BIRTHS: int = 3604640


def validate_raw_dataset(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Audit the raw dataset against expected benchmarks.

    Returns:
        (is_valid, error_messages)
    """
    errors: List[str] = []

    # 1. Row count check
    if len(df) != EXPECTED_ROWS:
        errors.append(f"Expected {EXPECTED_ROWS} rows, got {len(df)}.")

    # 2. Null values check
    missing_count = int(df.isnull().sum().sum())
    if missing_count > 0:
        errors.append(f"Expected 0 missing values, found {missing_count}.")

    # 3. Duplicate rows check
    duplicates = int(df.duplicated().sum())
    if duplicates > 0:
        errors.append(f"Expected 0 duplicate rows, found {duplicates}.")

    # 4. Total births benchmark
    total_births = int(df["Births"].sum())
    if total_births != EXPECTED_TOTAL_BIRTHS:
        errors.append(
            f"Expected {EXPECTED_TOTAL_BIRTHS:,} total births, got {total_births:,}."
        )

    # 5. Geography count
    geo_count = df["State of Residence"].nunique()
    if geo_count != EXPECTED_GEOGRAPHIES:
        errors.append(
            f"Expected {EXPECTED_GEOGRAPHIES} geographies, found {geo_count}."
        )

    # 6. Month count
    month_count = df["Month"].nunique()
    if month_count != EXPECTED_MONTHS:
        errors.append(f"Expected {EXPECTED_MONTHS} months, found {month_count}.")

    # 7. Infant sex categories
    sex_count = df["Sex of Infant"].nunique()
    if sex_count != EXPECTED_SEXES:
        errors.append(f"Expected {EXPECTED_SEXES} sexes, found {sex_count}.")

    return (len(errors) == 0, errors)


@st.cache_data(show_spinner="Loading provisional natality data...")
def load_natality_data() -> pd.DataFrame:
    """Load and validate the provisional 2025 CDC natality workbook.

    Cached to ensure the Excel workbook is read only once per session.
    """
    # Build resilient relative path compatible with local and cloud hosting
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "data" / "Provisional_Natality_2025_CDC.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found at {file_path}. Please verify the file path."
        )

    # Read the first worksheet (untouched read-only mode)
    df = pd.read_excel(file_path, sheet_name=0)

    # Validate against expected quality standards
    is_valid, validation_errors = validate_raw_dataset(df)
    if not is_valid:
        raise ValueError(f"Data validation failed: {'; '.join(validation_errors)}")

    # Add 2-letter USPS state code for Choropleth maps
    df["State Code"] = df["State of Residence"].map(STATE_TO_ABBR)

    # Ensure Month is an ordered categorical variable to preserve chronological order
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    return df


def filter_data(
    df: pd.DataFrame,
    selected_states: List[str],
    selected_months: List[str],
    selected_sexes: List[str],
) -> pd.DataFrame:
    """Filter natality dataframe based on user selections."""
    if not selected_states or not selected_months or not selected_sexes:
        return df.iloc[0:0].copy()

    mask = (
        df["State of Residence"].isin(selected_states)
        & df["Month"].isin(selected_months)
        & df["Sex of Infant"].isin(selected_sexes)
    )
    return df[mask].copy()


def calculate_kpis(filtered_df: pd.DataFrame) -> Dict[str, any]:
    """Calculate executive KPI summary metrics for the active filter view."""
    if filtered_df.empty:
        return {
            "total_births": 0,
            "selected_geographies": 0,
            "avg_monthly_births": 0,
            "top_geo": "N/A",
            "top_geo_births": 0,
            "top_month": "N/A",
            "top_month_births": 0,
        }

    total_births = int(filtered_df["Births"].sum())
    selected_geographies = int(filtered_df["State of Residence"].nunique())
    unique_months_count = max(1, filtered_df["Month"].nunique())
    avg_monthly_births = total_births / unique_months_count

    # Geography with highest selected births
    geo_totals = (
        filtered_df.groupby("State of Residence")["Births"].sum().reset_index()
    )
    top_geo_row = geo_totals.sort_values(by="Births", ascending=False).iloc[0]
    top_geo = top_geo_row["State of Residence"]
    top_geo_births = int(top_geo_row["Births"])

    # Month with highest selected births
    month_totals = (
        filtered_df.groupby("Month", observed=False)["Births"].sum().reset_index()
    )
    top_month_row = month_totals.sort_values(by="Births", ascending=False).iloc[0]
    top_month = str(top_month_row["Month"])
    top_month_births = int(top_month_row["Births"])

    return {
        "total_births": total_births,
        "selected_geographies": selected_geographies,
        "avg_monthly_births": avg_monthly_births,
        "top_geo": top_geo,
        "top_geo_births": top_geo_births,
        "top_month": top_month,
        "top_month_births": top_month_births,
    }
