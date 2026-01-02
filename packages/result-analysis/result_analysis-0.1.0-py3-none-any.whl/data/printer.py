# Functions for printing parsed data summaries.

import pandas as pd
import numpy as np

from .parser import extract_class_results

def print_parsed_summary(data):
    # This function prints a summary of the parsed data.
    # It shows exam, class, subjects, and then each student's details.
    class_name = data.get("class_name")
    exam_name = data.get("exam_name")
    subjects = data.get("subjects", [])
    total_out_of = data.get("total_out_of")

    # Print header info
    header_parts = [
        f"Exam: {exam_name if exam_name else 'N/A'}",
        f"Class: {class_name if class_name else 'N/A'}",
        f"Subjects ({len(subjects)}): {', '.join(subjects) if subjects else 'N/A'}",
    ]
    if total_out_of is not None:
        header_parts.append(f"Total Out Of: {total_out_of}")
    print(" | ".join(header_parts))

    # Print each student
    for s in data.get("students", []):
        roll = s.get("roll_no")
        name = s.get("name") or ""
        marks = s.get("marks", {})
        subj_perc = s.get("subject_percentages", {})
        total = s.get("total")
        percent = s.get("percentage")

        def format_number(v):
            # Helper to format numbers nicely
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return ""
            try:
                fv = float(v)
                if fv.is_integer():
                    return str(int(fv))
                else:
                    return f"{fv:.2f}"
            except:
                return str(v)

        # Build marks string like "Math:85 (85.00%), Science:90 (90.00%)"
        parts = []
        for subj in subjects:
            m = format_number(marks.get(subj))
            p = format_number(subj_perc.get(subj))
            if p != "":
                parts.append(f"{subj}:{m} ({p}%)")
            else:
                parts.append(f"{subj}:{m}")
        marks_str = ", ".join(parts)
        line = f"Roll:{roll}  Name:{name}  Marks: [{marks_str}]  Total:{format_number(total)}  %:{format_number(percent)}"
        print(line)

def print_class_results(file_path, sheet_name=None):
    # This function reads the Excel file, parses it, and prints the summary.
    # It's a shortcut to do both extraction and printing.
    data = extract_class_results(file_path, sheet_name=sheet_name)
    print_parsed_summary(data)