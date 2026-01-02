import pandas as pd
import os
import curses
from .select_data import (
    select_class_exam,
    select_from_list,
    select_from_list_no_curses,
    CURSES_ENABLED,
)


def display_df(df, title):
    # Create a copy to avoid modifying the original DataFrame
    df_display = df.copy()

    # Format float columns to integers
    for col in df_display.select_dtypes(include=["float64"]).columns:
        df_display[col] = df_display[col].apply(
            lambda x: str(int(round(x))) if pd.notna(x) else ""
        )

    # Convert all columns to string type for consistent width calculation
    for col in df_display.columns:
        df_display[col] = df_display[col].astype(str)

    # Calculate the maximum width for each column
    col_widths = {
        col: max(len(col), df_display[col].str.len().max())
        for col in df_display.columns
    }

    # Create the header string with padding and a separator
    header = " | ".join(
        f"{col.upper():<{col_widths[col]}}" for col in df_display.columns
    )
    separator = "-+-".join("-" * col_widths[col] for col in df_display.columns)

    # Print the title centered above the table
    table_width = len(header)
    print(f"\n    {title.upper().center(table_width)}")
    print(f"    {'=' * table_width}")

    # Print the header and separator
    print(f"    {header}")
    print(f"    {separator}")

    # Print each row with proper padding
    for _, row in df_display.iterrows():
        row_str = " | ".join(
            f"{row[col]:<{col_widths[col]}}" for col in df_display.columns
        )
        print(f"    {row_str}")

    # Print the bottom border of the table
    print(f"    {'=' * table_width}\n")


def view_data_flow():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    base_path = os.path.join("user-data", s_class, s_exam)
    opts = ["Percentage", "Grouped", "Full Result", "All"]

    if CURSES_ENABLED:
        dtype = curses.wrapper(
            select_from_list, "Select Data to View", opts, "Up/Down, Enter, q to quit."
        )
    else:
        dtype = select_from_list_no_curses(
            "Select Data to View", opts, "Up/Down, Enter, q to quit."
        )

    if not dtype:
        return
    files = {
        "Percentage": ["percentage.csv"],
        "Grouped": ["grouped.csv"],
        "Full Result": ["result.csv"],
        "All": ["percentage.csv", "result.csv", "grouped.csv"],
    }
    for f in files.get(dtype, []):
        fpath = os.path.join(base_path, f)
        if os.path.isfile(fpath):
            display_df(pd.read_csv(fpath), f.replace(".csv", " Data").title())
        else:
            print(f"    {f} not available.")
