from pathlib import Path
from .parser import extract_class_results, results_to_dfs
from .utils import sanitize_for_path


def save_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    out_dir = (
        Path(base_dir)
        / sanitize_for_path(parsed.get("class_name"))
        / sanitize_for_path(parsed.get("exam_name"))
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    df_r, df_p = results_to_dfs(parsed)
    df_r.to_csv(out_dir / "result.csv", index=False)
    df_p.to_csv(out_dir / "percentage.csv", index=False)
    return out_dir
