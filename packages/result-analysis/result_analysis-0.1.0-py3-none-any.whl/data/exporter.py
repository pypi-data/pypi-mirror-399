import pandas as pd


def export_df_to_excel(df, fname="export.xlsx"):
    if input("    Save to Excel? (y/n): ").strip().lower() in ("y", "yes"):
        name = input(f"    Filename ('{fname}'): ").strip() or fname
        out_path = name if name.lower().endswith(".xlsx") else name + ".xlsx"
        try:
            df.to_excel(out_path, index=False)
            print("    Saved:", out_path)
            return out_path
        except Exception as e:
            print("    Error:", e)
    return None
