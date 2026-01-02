import os
import pandas as pd
import curses
from ui.select_data import (
    select_class_exam,
    select_from_list,
    select_from_list_no_curses,
    CURSES_ENABLED,
)
from .plotter import plot_chart


def plot_graphs_flow(base_dir="user-data"):
    c_name, e_name = select_class_exam(base_dir)
    if not (c_name and e_name):
        return

    opts = ["Bar Chart", "Line Chart", "Scatter Plot"]
    if CURSES_ENABLED:
        g_type = curses.wrapper(
            select_from_list, "Select Graph Type", opts, "Up/Down, Enter, q to quit."
        )
    else:
        g_type = select_from_list_no_curses(
            "Select Graph Type", opts, "Up/Down, Enter, q to quit."
        )

    if not g_type:
        return
    csv_path = os.path.join(base_dir, c_name, e_name, "percentage.csv")
    if not os.path.isfile(csv_path):
        print(f"    percentage.csv not found for {c_name} - {e_name}")
        return
    df = pd.read_csv(csv_path)
    title = f"{g_type} - {c_name} - {e_name}"
    if "Bar" in g_type:
        plot_chart(
            df,
            "Name",
            "Overall_Percentage",
            title,
            "Students",
            "Percentage (%)",
            kind="bar",
        )
    elif "Line" in g_type:
        plot_chart(
            df,
            "Name",
            "Overall_Percentage",
            title,
            "Students",
            "Percentage (%)",
            kind="line",
        )
    elif "Scatter" in g_type:
        plot_chart(
            df,
            "Roll No",
            "Overall_Percentage",
            title,
            "Roll Number",
            "Percentage (%)",
            kind="scatter",
        )
