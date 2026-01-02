# This file is the main entry point for handling Excel parsing.
# It imports functions from other modules for organization.

import pandas as pd
import numpy as np
from pathlib import Path

# Import from submodules
from .parser import extract_class_results, extractDataFromExcel
from .printer import print_parsed_summary, print_class_results
from .saver import results_to_dataframes, save_class_results_to_csv, save_and_report
from .utils import coerce_number, sanitize_for_path, excludeRollNoAndName

def run_pipeline():
    # This function runs the full pipeline: input file path, extract data, show summary, save to CSV, notify.
    print("Welcome to the Class Results Processor!")
    print("Please provide the path to your Excel file (e.g., data/sample/subject-analysis.xlsx):")
    file_path = input("Excel file path: ").strip()
    if not file_path:
        print("No file path provided. Exiting.")
        return

    # Try to display available sheet names to help the user choose
    try:
        xls = pd.ExcelFile(file_path)
        if xls.sheet_names:
            print("\nAvailable sheets in this workbook:")
            for i, nm in enumerate(xls.sheet_names, 1):
                print(f"  {i}. {nm}")
    except Exception as e:
        # Non-fatal; continue to prompt without listing
        print(f"(Could not read sheet names: {e})")

    raw_sheet = input("Sheet name or number (press Enter for first sheet): ").strip()
    sheet_name = None
    try:
        # If user typed a number, treat it as 1-based index
        if raw_sheet.isdigit() and 'xls' in locals():
            idx = int(raw_sheet) - 1
            if 0 <= idx < len(xls.sheet_names):
                sheet_name = xls.sheet_names[idx]
        elif raw_sheet and 'xls' in locals():
            # Try exact match
            if raw_sheet in xls.sheet_names:
                sheet_name = raw_sheet
            else:
                # Try trimmed/case-insensitive matches
                trimmed = raw_sheet.strip()
                lower_map = {s.lower(): s for s in xls.sheet_names}
                if trimmed.lower() in lower_map:
                    sheet_name = lower_map[trimmed.lower()]
                else:
                    # Try startswith (case-insensitive)
                    candidates = [s for s in xls.sheet_names if s.lower().startswith(trimmed.lower())]
                    if candidates:
                        sheet_name = candidates[0]
        # If still None and we have sheets, fall back to first
        if sheet_name is None and 'xls' in locals() and xls.sheet_names:
            print("No matching sheet found. Using first sheet.")
            sheet_name = xls.sheet_names[0]
    except Exception:
        # As a last resort, let pandas default to first sheet by passing None
        sheet_name = None
    base_dir = input("Base directory for saving CSVs (press Enter for 'user-data'): ").strip() or "user-data"

    try:
        # Extract data
        print("\nExtracting data from the Excel file...")
        parsed = extract_class_results(file_path, sheet_name=sheet_name)
        print("Data extracted successfully!")

        # Show summary
        print("\n--- Results Summary ---")
        print_parsed_summary(parsed)

        # Save to CSV
        print("\nSaving data to CSV files...")
        out_dir = save_class_results_to_csv(file_path, sheet_name=sheet_name, base_dir=base_dir)
        print(f"CSVs saved in: {out_dir}")

        # Notify
        class_name = parsed.get("class_name", "Unknown")
        exam_name = parsed.get("exam_name", "Unknown")
        print(f"\nData for class '{class_name}' and exam '{exam_name}' has been stored properly!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_pipeline()


