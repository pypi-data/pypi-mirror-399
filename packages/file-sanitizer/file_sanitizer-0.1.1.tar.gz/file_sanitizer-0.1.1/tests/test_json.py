import tempfile
import json
import os
from file_sanitizer.json_sanitizer import JsonSanitizer


def test_json_sanitize():
    data = {"database": {"password": "admin"}, "normal": 1}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name

    try:
        s = JsonSanitizer()
        scan = s.scan(path)
        assert len(scan["findings"]) == 1
        assert scan["findings"][0]["key"] == "password"

        res = s.sanitize(path)
        assert res["modified"] == 1

        with open(path) as f:
            sanitized = json.load(f)
        assert sanitized["database"]["password"] == "***"
    finally:
        os.unlink(path)