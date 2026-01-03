"""CSV sanitizer (uses pandas)"""
from pathlib import Path
from typing import Dict

from .utils import load_rules, is_sensitive_key, smart_mask, partial_hash
from .backup import create_backup, restore_backup
import pandas as pd


class CsvSanitizer:
    def __init__(self, rules_path: str = None):
        self.rules = load_rules(rules_path)

    def scan(self, path: str) -> Dict:
        p = Path(path)
        try:
            df = pd.read_csv(p, dtype=str)  # read everything as str to avoid type issues
        except Exception as e:
            raise ValueError(f"Failed to read CSV {p}: {e}")

        findings = []
        for col in df.columns:
            if is_sensitive_key(col, self.rules):
                nonempty = df[~df[col].isna() & (df[col].str.strip() != "")]
                for idx, val in nonempty[col].items():
                    findings.append({"col": col, "row": int(idx), "value": val})
        return {"file": str(p), "findings": findings}

    def sanitize(
        self,
        path: str,
        mask: str = "***",
        partial: bool = False,
        backup: bool = True,
        remove_nan: bool = False,
        delete_col: str = None,
        hash_values: bool = False,
        drop_duplicates: bool = False,
    ) -> Dict:
        p = Path(path)
        try:
            df = pd.read_csv(p, dtype=str)
        except Exception as e:
            raise ValueError(f"Failed to read CSV {p}: {e}")

        if backup:
            create_backup(str(p))

        modified = 0

        # Handle column deletion first
        if delete_col and delete_col in df.columns:
            df.drop(columns=[delete_col], inplace=True)
            modified += 1  # count as one structural change

        # Sanitize sensitive columns
        for col in list(df.columns):
            if is_sensitive_key(col, self.rules):
                def mask_val(x):
                    nonlocal modified
                    if pd.isna(x) or str(x).strip() == "":
                        return x
                    modified += 1
                    if hash_values:
                        return partial_hash(str(x))
                    if partial:
                        return smart_mask(str(x))
                    return mask
                df[col] = df[col].apply(mask_val)

        # Post-processing
        before_len = len(df)
        if remove_nan:
            df = df.dropna()
        if drop_duplicates:
            df = df.drop_duplicates()

        # Count net row changes
        row_changes = before_len - len(df)
        if row_changes > 0:
            modified += row_changes

        df.to_csv(p, index=False)
        return {"file": str(p), "modified": modified}

    def undo(self, path: str) -> bool:
        return bool(restore_backup(path))