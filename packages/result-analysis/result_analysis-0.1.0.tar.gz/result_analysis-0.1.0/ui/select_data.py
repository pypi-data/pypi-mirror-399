import curses
import glob
import os
import sys
from thefuzz import process

# --- Curses compatibility check ---
CURSES_ENABLED = False
try:
    if sys.stdout and hasattr(sys.stdout, "fileno"):
        stdscr = curses.initscr()
        curses.endwin()
        del stdscr
        CURSES_ENABLED = True
    else:
        CURSES_ENABLED = False
except (curses.error, AttributeError):
    CURSES_ENABLED = False
# --- End Curses compatibility check ---


def draw_menu(stdscr, title, opts, idx, help_text):
    stdscr.clear()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, help_text)
    for i, opt in enumerate(opts):
        stdscr.addstr(4 + i, 2, f" {'>' if i == idx else ' '} {opt}")
    stdscr.refresh()


def select_from_list(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13):
            return opts[idx]
        elif key in (ord("q"), ord("Q")):
            return None


def select_with_delete(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13):
            return opts[idx], "select"
        elif key in (ord("d"), ord("D")):
            return opts[idx], "delete"
        elif key in (ord("q"), ord("Q")):
            return None, None


def select_from_list_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i + 1}. {opt}")
    print(f"    (Enter 'q' to quit)")

    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == "q":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(opts):
                return opts[idx]
            else:
                print("    Invalid number. Please try again.")
        except ValueError:
            print("    Please enter a number.")


def select_with_delete_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i + 1}. {opt}")
    print("    (Enter 'd<number>' to delete, e.g., 'd1')")
    print(f"    (Enter 'q' to quit)")

    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == "q":
            return None, None

        action = "select"
        item_choice = choice
        if choice.startswith("d") and len(choice) > 1:
            action = "delete"
            item_choice = choice[1:]

        try:
            idx = int(item_choice) - 1
            if 0 <= idx < len(opts):
                return opts[idx], action
            else:
                print("    Invalid number. Please try again.")
        except ValueError:
            print("    Please enter a valid number or command.")


def fuzzy_search_file_select_no_curses():
    search_term = ""
    while True:
        search_term = input(
            "\n    Enter search term to find Excel file (or 'q' to quit): "
        ).strip()
        if not search_term or search_term.lower() == "q":
            return None

        all_files = glob.glob("**/*.xlsx", recursive=True)
        if not all_files:
            print(
                "    No .xlsx files found in the current directory or subdirectories."
            )
            continue

        matches = process.extract(search_term, all_files, limit=10)
        search_results = [match[0] for match in matches if match[1] > 30]

        if not search_results:
            print("    No matches found.")
            continue

        print("\n    --- Select a File ---")
        for i, file_path in enumerate(search_results):
            print(f"    {i + 1}. {file_path}")

        choice = input("    Select a number (or 'r' to research): ").strip().lower()
        if choice == "r":
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(search_results):
                return search_results[idx]
            else:
                print("    Invalid number.")
        except ValueError:
            print("    Invalid input.")


def fuzzy_search_file_select(stdscr):
    search_term = ""
    selected_index = 0
    all_files = glob.glob("**/*.xlsx", recursive=True)
    search_results = []

    curses.curs_set(1)
    stdscr.nodelay(0)

    while True:
        stdscr.clear()

        # Display Title and Search Prompt
        stdscr.addstr(1, 2, "Search for an Excel File")
        stdscr.addstr(
            2, 2, "Type to search, Up/Down to navigate, Enter to select, 'q' to quit."
        )
        stdscr.addstr(4, 4, f"Search: {search_term}")

        # Perform search if search_term is not empty
        if search_term:
            matches = process.extract(search_term, all_files, limit=10)
            search_results = [match for match in matches if match[1] > 30]
        else:
            search_results = []

        # Display search results
        if search_results:
            display_line = 6
            for i, (file_path, score) in enumerate(search_results):
                filename = os.path.basename(file_path)
                display_text = f"{filename} ({score}%)"

                if i == selected_index:
                    stdscr.addstr(
                        display_line, 2, f"> {display_text}", curses.A_REVERSE
                    )
                else:
                    stdscr.addstr(display_line, 2, f"  {display_text}")
                display_line += 1
                stdscr.addstr(display_line, 6, f"Path: {file_path}")  # Indented path
                display_line += 2  # Extra line for spacing
        elif search_term:
            stdscr.addstr(6, 2, "  No matches found.")

        stdscr.move(4, 12 + len(search_term))  # Move cursor to end of search term
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_ENTER, 10, 13):
            if search_results:
                return search_results[selected_index][0]
        elif key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(search_results) - 1, selected_index + 1)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            search_term = search_term[:-1]
            selected_index = 0
        elif key in (ord("q"), ord("Q"), 27):  # 27 is escape key
            return None
        elif 32 <= key <= 126:  # Printable characters
            search_term += chr(key)
            selected_index = 0


def select_class_exam(base_dir="user-data"):
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )
    if not classes:
        return None, None

    if CURSES_ENABLED:
        s_class = curses.wrapper(
            select_from_list, "Select Class", classes, "Up/Down, Enter, q to quit."
        )
    else:
        s_class = select_from_list_no_curses(
            "Select Class", classes, "Up/Down, Enter, q to quit."
        )

    if not s_class:
        return None, None
    exams = sorted(
        [
            d
            for d in os.listdir(os.path.join(base_dir, s_class))
            if os.path.isdir(os.path.join(base_dir, s_class, d))
        ]
    )
    if not exams:
        return None, None

    if CURSES_ENABLED:
        s_exam = curses.wrapper(
            select_from_list, f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )
    else:
        s_exam = select_from_list_no_curses(
            f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )

    return s_class, s_exam
