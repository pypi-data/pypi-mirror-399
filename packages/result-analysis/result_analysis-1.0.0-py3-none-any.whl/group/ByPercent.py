import pandas as pd
import os
from pathlib import Path
from ui.view_data import display_df
from ui.select_data import select_class_exam
from data.exporter import export_df_to_excel


def group_by_percent(csv_path):
    df = pd.read_csv(csv_path)
    user_input = input("    Custom grouping (e.g., 90,80,33) or Enter for default: ")
    thresholds = sorted(
        [int(t) for t in user_input.split(",")]
        if user_input
        else [90, 80, 70, 60, 50, 40, 33],
        reverse=True,
    )
    if 100 not in thresholds:
        thresholds.insert(0, 100)
    grouping = [
        [(thresholds[i + 1] + 1 if i + 1 < len(thresholds) else 0), thresholds[i]]
        for i in range(len(thresholds))
    ]
    subjects = [
        c[:-2] for c in df.columns if c.endswith("_%") and c != "Overall_Percentage"
    ]
    summary = []
    for subj in subjects:

        def get_group(score):
            if pd.isna(score):
                return "N/A"
            for low, high in grouping:
                if low <= score <= high:
                    return f"{low}-{high}"
            return "Other"

        summary.append(
            {
                "Subject": subj,
                **df[f"{subj}_%"].apply(get_group).value_counts().to_dict(),
            }
        )
    summary_df = pd.DataFrame(summary).fillna(0)
    display_df(summary_df, "Grouped Summary (counts)")
    return df, summary_df


def group_by_percent_interactive():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    path = os.path.join("user-data", s_class, s_exam, "percentage.csv")
    if not os.path.isfile(path):
        print(f"    'percentage.csv' not found for {s_class} - {s_exam}.")
        return
    _, summary_df = group_by_percent(path)
    if not summary_df.empty:
        (Path(path).parent / "grouped.csv").write_text(summary_df.to_csv(index=False))
        export_df_to_excel(summary_df, fname="grouped.xlsx")
