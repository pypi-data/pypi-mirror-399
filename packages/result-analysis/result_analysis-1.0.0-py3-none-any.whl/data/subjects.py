# Functions for detecting and handling subject columns in the Excel sheet.

import numpy as np

from .utils import coerce_number

def detect_subject_columns(df, header_row):
    # This function figures out which columns are for subjects, total, and percentage.
    # It looks at the header row and identifies subject names, their marks and percent columns.
    # Subjects are between RollNo (column 0-1) and Total.
    headers = []
    for val in df.iloc[header_row]:
        # Safely handle NaN/None before converting to string
        if val is None or (isinstance(val, float) and np.isnan(val)):
            headers.append("")
        else:
            headers.append(str(val))
    subjects = []
    # subject_to_cols will map subject name to its column indices for marks and percent
    subject_to_cols = {}
    total_col = None
    per_col = None

    # Find the column index for TOTAL
    for ci in range(len(headers)):
        label = headers[ci].strip().upper()
        if label == "TOTAL":
            total_col = ci
            break
    # Find the column index for PER or %
    for ci in range(len(headers)):
        label = headers[ci].strip().upper()
        if label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci
            break

    # Subjects start from column 2 (after RollNo and Name) up to TOTAL column
    end_ci = total_col if total_col is not None else len(headers)
    start_ci = 2 if len(headers) > 2 else 0

    ci = start_ci
    while ci < end_ci:
        name = headers[ci].strip()
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            # This is a subject column
            marks_col = ci
            percent_col = None
            # Check if the next column has the same name (for percent)
            if ci + 1 < end_ci and headers[ci + 1].strip() == name:
                percent_col = ci + 1
                ci += 2  # Skip next since it's percent
            else:
                # Sometimes the percent column is blank in header but has percent values
                if ci + 1 < end_ci and headers[ci + 1].strip() == "":
                    # Check a few rows below to see if values are 0-100 (percentages)
                    sample_rows = []
                    for r in range(header_row + 1, min(header_row + 1 + 10, len(df))):
                        sample_rows.append(r)
                    numeric_like = 0
                    for r in sample_rows:
                        val = df.iat[r, ci + 1]
                        num = coerce_number(val)
                        if not (isinstance(num, float) and np.isnan(num)):
                            if 0 <= num <= 100:
                                numeric_like += 1
                    if numeric_like >= 2:  # If at least 2 look like percentages
                        percent_col = ci + 1
                        ci += 2
                    else:
                        ci += 1
                else:
                    ci += 1
            # Add to the map
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1

    return subjects, subject_to_cols, total_col, per_col