import tempfile
import pandas as pd
import os
from file_sanitizer.csv_sanitizer import CsvSanitizer


def test_csv_sanitize():
    df = pd.DataFrame({"username": ["u1", "u2"], "password": ["p1", "p2"]})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f, index=False)
        path = f.name

    try:
        s = CsvSanitizer()
        scan = s.scan(path)
        assert len(scan["findings"]) == 2
        assert scan["findings"][0]["col"] == "password"

        res = s.sanitize(path, partial=True)
        assert res["modified"] == 2

        sanitized_df = pd.read_csv(path)
        assert "***" not in sanitized_df["password"].values  # partial masking
        assert "p" not in sanitized_df["password"].iloc[0]   # fully changed
    finally:
        os.unlink(path)