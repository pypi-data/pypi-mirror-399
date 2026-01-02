import pandas as pd
import numpy as np
from .utils import coerce_number


def find_row_with_text(df, text, max_rows=30):
    text_lower = text.lower()
    for i in range(min(max_rows, len(df))):
        if any(text_lower in str(v).lower() for v in df.iloc[i] if not pd.isna(v)):
            return i
    return None


def find_header_and_meta_rows(df):
    header_row = None
    for i in range(min(50, len(df))):
        row_vals = [str(v).strip().lower() for v in df.iloc[i].astype(str).fillna("")]
        if any(v in ("rollno", "roll no", "roll_no") for v in row_vals) and (
            "total" in row_vals
            or any(v in ("per", "%", "percent", "percentage") for v in row_vals)
        ):
            header_row = i
            break
    return (
        header_row,
        find_row_with_text(df, "CLASS :", 10),
        find_row_with_text(df, "NAME OF EXAMINATION", 10),
    )


def parse_exam_and_outof(df, exam_row):
    if exam_row is None:
        return None, None
    for val in (str(v) for v in df.iloc[exam_row] if not pd.isna(v)):
        if val.strip() and "NAME OF EXAMINATION" not in val:
            exam_name = val.strip()
            if "(" in exam_name and ")" in exam_name:
                start, end = exam_name.find("(") + 1, exam_name.find(")")
                try:
                    per_subject_out_of = int(float(exam_name[start:end].strip()))
                except (ValueError, TypeError):
                    per_subject_out_of = None
                return exam_name[: start - 1].strip(), per_subject_out_of
            return exam_name, None
    return None, None


def parse_class_name(df, class_row):
    if class_row is None:
        return None
    row = [str(v) for v in df.iloc[class_row] if not pd.isna(v)]
    for idx, val in enumerate(row):
        if (
            val.strip().upper().startswith("CLASS")
            and idx + 1 < len(row)
            and row[idx + 1].strip()
        ):
            return row[idx + 1].strip()
    for val in row[1:]:
        if val.strip():
            return val.strip()
    return None


def detect_subject_columns(df, header_row):
    headers = [
        str(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else ""
        for v in df.iloc[header_row]
    ]
    subjects, subject_to_cols, total_col, per_col = [], {}, None, None

    for ci, h in enumerate(headers):
        label = h.strip().upper()
        if label == "TOTAL":
            total_col = ci
        elif label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci

    end_ci = total_col if total_col is not None else len(headers)
    ci = 2 if len(headers) > 2 else 0
    while ci < end_ci:
        name = headers[ci].strip()
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            marks_col = ci
            percent_col = None
            if ci + 1 < end_ci and headers[ci + 1].strip() == name:
                percent_col = ci + 1
                ci += 2
            elif ci + 1 < end_ci and headers[ci + 1].strip() == "":
                numeric_like = 0
                for r in range(header_row + 1, min(header_row + 11, len(df))):
                    num = coerce_number(df.iat[r, ci + 1])
                    if not np.isnan(num) and 0 <= num <= 100:
                        numeric_like += 1
                if numeric_like >= 2:
                    percent_col = ci + 1
                    ci += 2
                else:
                    ci += 1
            else:
                ci += 1
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1
    return subjects, subject_to_cols, total_col, per_col


def extract_class_results(file_path, sheet_name=None):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)
    if isinstance(df, dict):
        df = next(iter(df.values()))
    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None:
        raise ValueError("Header row not found.")
    exam_name, _ = parse_exam_and_outof(df, exam_row)
    per_subject_out_of = 100
    class_name = parse_class_name(df, class_row)
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(
        df, header_row
    )
    students = []
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        try:
            roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError):
            continue
        name = (
            str(row.iloc[1]).strip()
            if len(row) > 1 and not pd.isna(row.iloc[1])
            else ""
        )

        marks, subject_percentages = {}, {}
        for s in subjects:
            cols = subject_to_cols[s]
            marks_val = (
                coerce_number(row.iloc[cols.get("marks")])
                if cols.get("marks") is not None and cols.get("marks") < len(row)
                else np.nan
            )
            marks[s] = marks_val

            percent_val = np.nan
            if not np.isnan(marks_val):
                percent_val = round((marks_val / per_subject_out_of) * 100, 2)
            subject_percentages[s] = percent_val

        valid_marks_values = [m for m in marks.values() if not np.isnan(m)]
        total = np.nansum(valid_marks_values)

        num_valid_subjects = len(valid_marks_values)

        percent = np.nan
        if num_valid_subjects > 0:
            denom = per_subject_out_of * num_valid_subjects
            if denom > 0:
                percent = round((total / denom) * 100, 2)

        if not name and all(np.isnan(v) for v in marks.values()):
            continue
        students.append(
            {
                "roll_no": roll_no,
                "name": name,
                "marks": marks,
                "subject_percentages": subject_percentages,
                "total": total,
                "percentage": percent,
            }
        )

    result = {
        "class_name": class_name,
        "exam_name": exam_name,
        "subjects": subjects,
        "per_subject_out_of": per_subject_out_of,
        "students": students,
    }
    if per_subject_out_of and subjects:
        num_subjects = len(subjects)
        result["total_out_of"] = per_subject_out_of * num_subjects
    return result


def results_to_dfs(parsed):
    subjects = parsed.get("subjects", [])
    rows_r, rows_p = [], []
    for s in parsed.get("students", []):
        base = {"Roll No": s.get("roll_no"), "Name": s.get("name", "")}
        row_r, row_p = base.copy(), base.copy()
        for subj in subjects:
            row_r[f"{subj}_Marks"] = s.get("marks", {}).get(subj)
            row_p[f"{subj}_%"] = s.get("subject_percentages", {}).get(subj)
        row_r["Total"], row_r["Percentage"] = s.get("total"), s.get("percentage")
        row_p["Overall_Percentage"] = s.get("percentage")
        rows_r.append(row_r)
        rows_p.append(row_p)
    return pd.DataFrame(rows_r), pd.DataFrame(rows_p)
