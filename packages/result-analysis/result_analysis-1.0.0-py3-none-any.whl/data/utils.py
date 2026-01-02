import numpy as np


def coerce_number(x):
    try:
        s = str(x).strip()
        if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"):
            return np.nan
        return float(s)
    except (ValueError, TypeError):
        return np.nan


def sanitize_for_path(name):
    return (
        str(name).strip().replace("/", "-").replace("\\", "-").replace(" ", "_")
        if name
        else "UNKNOWN"
    )
