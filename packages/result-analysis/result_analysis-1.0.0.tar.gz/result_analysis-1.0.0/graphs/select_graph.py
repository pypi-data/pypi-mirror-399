"""Simple UI to select Class, Exam, and Graph Type for plotting.
- Uses arrow keys (Up/Down) to navigate, Enter to select, 'q' to quit.
- Follows the same pattern as ui/select_data.py
- User selects: Class -> Exam -> Graph Type -> Shows the graph
"""

import os
import curses
from ui.select_data import list_classes, list_exams


def draw_menu(stdscr, title, options, index):
    """Draw a simple menu with options."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, "Use Up/Down arrows and Enter. Press q to quit.")
    top = 4
    for i, opt in enumerate(options):
        marker = ">" if i == index else " "
        line = f" {marker} {opt}"
        if top + i < h - 1:
            stdscr.addstr(top + i, 2, line)
    stdscr.refresh()


def select_from_list(stdscr, title, options):
    """Let user select an option from a list using arrow keys."""
    if not options:
        return None
    index = 0
    while True:
        draw_menu(stdscr, title, options, index)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            index = (index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j')):
            index = (index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[index]
        elif key in (ord('q'), ord('Q')):
            return None


def get_graph_types():
    """Return list of available graph types."""
    return [
        "Bar Chart - Student Performance",
        "Subject Comparison - All Students",
        "Line Chart - Performance Trend",
        "Pie Chart - Pass/Fail Distribution",
        "Horizontal Bar - Student Rankings",
        "Subject Average - Class Performance",
        "Scatter Plot - Roll No vs Percentage",
        "Box Plot - Subject Distribution"
    ]


def select_class_exam_and_graph(base_dir='user-data'):
    """Main function to select class, exam, and graph type.
    Returns: (class_name, exam_name, graph_type) or (None, None, None) if cancelled.
    """
    
    # Step 1: Select Class
    classes = list_classes(base_dir)
    if not classes:
        print("No classes found in", base_dir)
        return None, None, None
    
    selected_class = curses.wrapper(select_from_list, "Select Class", classes)
    if not selected_class:
        return None, None, None
    
    # Step 2: Select Exam
    exams = list_exams(base_dir, selected_class)
    if not exams:
        print("No exams found for class:", selected_class)
        return None, None, None
    
    selected_exam = curses.wrapper(select_from_list, f"Select Exam for {selected_class}", exams)
    if not selected_exam:
        return None, None, None
    
    # Step 3: Select Graph Type
    graph_types = get_graph_types()
    selected_graph = curses.wrapper(select_from_list, "Select Graph Type", graph_types)
    if not selected_graph:
        return None, None, None
    
    return selected_class, selected_exam, selected_graph


if __name__ == "__main__":
    class_name, exam_name, graph_type = select_class_exam_and_graph()
    if class_name and exam_name and graph_type:
        print(f"\nSelected:")
        print(f"  Class: {class_name}")
        print(f"  Exam: {exam_name}")
        print(f"  Graph: {graph_type}")
    else:
        print("No selection made.")
