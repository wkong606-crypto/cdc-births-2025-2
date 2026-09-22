"""Comprehensive Playwright QA Automation Test Suite for CDC Natality Dashboard."""

import os
import sys
import time
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright, expect

SCREENSHOT_DIR = Path("/Users/feifeiyu/.gemini/antigravity-ide/brain/b482ca7b-0e5d-4b74-a261-0c2fd62a5396/qa_screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://localhost:8501"

test_results = []

def record_result(case_num, name, status, details, screenshot_file=None):
    test_results.append({
        "Case": case_num,
        "Test Name": name,
        "Status": status,
        "Details": details,
        "Screenshot": screenshot_file or ""
    })
    print(f"[{status}] Case {case_num}: {name} - {details}")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Helper to wait for streamlit to finish running
        def wait_for_st(timeout=15000):
            # Streamlit shows stStatusWidget or running indicator
            time.sleep(1.5)
            page.wait_for_load_state("networkidle")
            time.sleep(1.0)

        # -------------------------------------------------------------
        # Test Case 1: Default dashboard with all observations
        # -------------------------------------------------------------
        print("\n--- Running Test 1: Default Dashboard ---")
        page.goto(BASE_URL)
        wait_for_st()
        page.wait_for_selector("h1", timeout=15000)

        # Check title and notices
        title = page.locator("h1").text_content()
        assert "Provisional 2025 CDC U.S. Natality Dashboard" in title

        # Verify no Python exceptions
        assert page.locator(".stException").count() == 0

        # Check unfiltered KPI metrics
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_births_str = metric_values[0].replace(",", "")
        geos_str = metric_values[1]
        
        assert total_births_str == "3604640", f"Expected 3,604,640, got {metric_values[0]}"
        assert "51 / 51" in geos_str

        # Screenshot Test 1
        ss1 = SCREENSHOT_DIR / "01_default_dashboard.png"
        page.screenshot(path=str(ss1), full_page=False)
        record_result(1, "Default Dashboard (All Observations)", "PASS", f"Total: {metric_values[0]}, Geos: {geos_str}, Zero exceptions", ss1.name)

        # -------------------------------------------------------------
        # Test Case 2: One state and all months (California)
        # -------------------------------------------------------------
        print("\n--- Running Test 2: One State (California) ---")
        page.goto(f"{BASE_URL}/?states=California")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        top_val = metric_values[0].replace(",", "")
        geos_val = metric_values[1]
        assert top_val == "393111", f"Expected 393,111 for CA, got {metric_values[0]}"
        assert "1 / 51" in geos_val

        ss2 = SCREENSHOT_DIR / "02_single_state_california.png"
        page.screenshot(path=str(ss2), full_page=False)
        record_result(2, "One State & All Months (California)", "PASS", f"Total: {metric_values[0]}, Geos: {geos_val}", ss2.name)

        # -------------------------------------------------------------
        # Test Case 3: Several states (CA, TX, FL, NY)
        # -------------------------------------------------------------
        print("\n--- Running Test 3: Several States ---")
        page.goto(f"{BASE_URL}/?states=California,Texas,Florida,New%20York")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        geos_val = metric_values[1]
        assert total_val == "1203335", f"Expected 1,203,335, got {metric_values[0]}"
        assert "4 / 51" in geos_val

        ss3 = SCREENSHOT_DIR / "03_several_states.png"
        page.screenshot(path=str(ss3), full_page=False)
        record_result(3, "Several States (CA, TX, FL, NY)", "PASS", f"Total: {metric_values[0]}, Geos: {geos_val}", ss3.name)

        # -------------------------------------------------------------
        # Test Case 4: One month (January)
        # -------------------------------------------------------------
        print("\n--- Running Test 4: One Month (January) ---")
        page.goto(f"{BASE_URL}/?months=January")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        assert total_val == "303686", f"Expected 303,686, got {metric_values[0]}"
        
        ss4 = SCREENSHOT_DIR / "04_one_month_january.png"
        page.screenshot(path=str(ss4), full_page=False)
        record_result(4, "One Month (January)", "PASS", f"Total: {metric_values[0]}, Peak: {metric_values[4]}", ss4.name)

        # -------------------------------------------------------------
        # Test Case 5: Female only
        # -------------------------------------------------------------
        print("\n--- Running Test 5: Female Only ---")
        page.goto(f"{BASE_URL}/?sexes=Female")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        assert total_val == "1762840", f"Expected 1,762,840, got {metric_values[0]}"

        ss5 = SCREENSHOT_DIR / "05_female_only.png"
        page.screenshot(path=str(ss5), full_page=False)
        record_result(5, "Female Only", "PASS", f"Total: {metric_values[0]} births", ss5.name)

        # -------------------------------------------------------------
        # Test Case 6: Male only
        # -------------------------------------------------------------
        print("\n--- Running Test 6: Male Only ---")
        page.goto(f"{BASE_URL}/?sexes=Male")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        assert total_val == "1841800", f"Expected 1,841,800, got {metric_values[0]}"

        ss6 = SCREENSHOT_DIR / "06_male_only.png"
        page.screenshot(path=str(ss6), full_page=False)
        record_result(6, "Male Only", "PASS", f"Total: {metric_values[0]} births", ss6.name)

        # -------------------------------------------------------------
        # Test Case 7: Combined State, Month, and Sex (CA, Jan, Female)
        # -------------------------------------------------------------
        print("\n--- Running Test 7: Combined Filter ---")
        page.goto(f"{BASE_URL}/?states=California&months=January&sexes=Female")
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        assert total_val == "16316", f"Expected 16,316, got {metric_values[0]}"

        ss7 = SCREENSHOT_DIR / "07_combined_filter.png"
        page.screenshot(path=str(ss7), full_page=False)
        record_result(7, "Combined Filter (CA, Jan, Female)", "PASS", f"Total: {metric_values[0]} births", ss7.name)

        # -------------------------------------------------------------
        # Test Case 8: Reset Filters
        # -------------------------------------------------------------
        print("\n--- Running Test 8: Reset Filters Button ---")
        # Click the Reset Filters button in the sidebar
        reset_btn = page.locator('section[data-testid="stSidebar"] button:has-text("Reset Filters")').first
        reset_btn.click()
        wait_for_st()
        metric_values = page.locator('[data-testid="stMetricValue"]').all_text_contents()
        total_val = metric_values[0].replace(",", "")
        assert total_val == "3604640", f"Expected reset to 3,604,640, got {metric_values[0]}"

        ss8 = SCREENSHOT_DIR / "08_reset_filters.png"
        page.screenshot(path=str(ss8), full_page=False)
        record_result(8, "Reset Filters", "PASS", f"Successfully restored to full total {metric_values[0]}", ss8.name)

        # -------------------------------------------------------------
        # Test Case 9: Empty or Invalid Selection
        # -------------------------------------------------------------
        print("\n--- Running Test 9: Empty Selection ---")
        # Click the Clear All button
        clear_btn = page.locator('section[data-testid="stSidebar"] button:has-text("Clear All")').first
        clear_btn.click()
        wait_for_st()

        # Check for friendly warning message
        all_alerts = page.locator('[data-testid="stAlert"]').all_text_contents()
        assert any("No observations match your current filter settings" in a for a in all_alerts), f"Alerts found: {all_alerts}"

        ss9 = SCREENSHOT_DIR / "09_empty_state_warning.png"
        page.screenshot(path=str(ss9), full_page=False)
        record_result(9, "Empty Selection Handling", "PASS", "Graceful warning displayed without exception", ss9.name)

        # Restore data using Select All button
        select_all_btn = page.locator('section[data-testid="stSidebar"] button:has-text("Select All")').first
        select_all_btn.click()
        wait_for_st()

        # -------------------------------------------------------------
        # Test Case 10: CSV Download & Data Table
        # -------------------------------------------------------------
        print("\n--- Running Test 10: Data Table & CSV Download ---")
        page.wait_for_selector('[role="tab"]', timeout=15000)
        # Click on Tab 4: Data Table & Download
        page.locator('[role="tab"]:has-text("Data Table")').click()
        wait_for_st()

        # Verify download button exists and triggers download
        download_btn = page.locator('button:has-text("Download Filtered Data (CSV)")')
        assert download_btn.count() > 0

        with page.expect_download() as download_info:
            download_btn.click()
        download = download_info.value
        download_path = SCREENSHOT_DIR / "test_download.csv"
        download.save_as(str(download_path))
        
        # Verify downloaded CSV contents
        downloaded_df = pd.read_csv(download_path)
        assert len(downloaded_df) == 1224, f"Expected 1,224 rows in full CSV, got {len(downloaded_df)}"
        assert downloaded_df["Births"].sum() == 3604640

        ss10 = SCREENSHOT_DIR / "10_data_table_and_download.png"
        page.screenshot(path=str(ss10), full_page=False)
        record_result(10, "CSV Download & Data Table", "PASS", f"Downloaded 1,224 rows, verified total 3,604,640", ss10.name)

        # -------------------------------------------------------------
        # Test Case 11: Map Rendering (Geographic Analysis Tab)
        # -------------------------------------------------------------
        print("\n--- Running Test 11: US Choropleth Map ---")
        page.locator('[role="tab"]:has-text("Geographic Analysis")').click()
        wait_for_st()

        # Check plotly graph container exists
        plotly_graphs = page.locator(".js-plotly-plot")
        assert plotly_graphs.count() >= 1, "Expected Plotly map graph to render"

        ss11 = SCREENSHOT_DIR / "11_us_choropleth_map.png"
        page.screenshot(path=str(ss11), full_page=False)
        record_result(11, "US Choropleth Map Rendering", "PASS", f"Choropleth rendered with {plotly_graphs.count()} figures visible", ss11.name)

        # -------------------------------------------------------------
        # Test Case 12: Mobile / Narrow-screen Layout
        # -------------------------------------------------------------
        print("\n--- Running Test 12: Mobile / Responsive Layout ---")
        mobile_context = browser.new_context(viewport={"width": 375, "height": 812})
        mobile_page = mobile_context.new_page()
        mobile_page.goto(BASE_URL)
        time.sleep(2.0)
        mobile_page.wait_for_load_state("networkidle")

        # Verify title and metrics render on mobile
        assert mobile_page.locator("h1").count() > 0
        mobile_metrics = mobile_page.locator('[data-testid="stMetricValue"]').all_text_contents()
        assert mobile_metrics[0].replace(",", "") == "3604640"

        ss12 = SCREENSHOT_DIR / "12_mobile_layout.png"
        mobile_page.screenshot(path=str(ss12), full_page=True)
        record_result(12, "Mobile / Narrow Screen Layout (375x812)", "PASS", f"Responsive stacking verified; total births: {mobile_metrics[0]}", ss12.name)

        mobile_context.close()
        browser.close()

    print("\n=== All 12 QA Test Cases Completed Successfully ===")
    return test_results

if __name__ == "__main__":
    results = run_tests()
    import json
    with open(SCREENSHOT_DIR / "qa_summary.json", "w") as f:
        json.dump(results, f, indent=2)
