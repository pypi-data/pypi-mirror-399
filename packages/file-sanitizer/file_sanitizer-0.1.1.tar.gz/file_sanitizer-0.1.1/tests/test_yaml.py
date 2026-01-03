import tempfile
import yaml
import os
from file_sanitizer.yaml_sanitizer import YamlSanitizer


def test_yaml_sanitize():
    data = {"api": {"token": "abcd"}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(data, f)
        path = f.name

    try:
        s = YamlSanitizer()
        scan = s.scan(path)
        assert len(scan["findings"]) == 1
        assert scan["findings"][0]["key"] == "token"

        res = s.sanitize(path)
        assert res["modified"] == 1

        with open(path) as f:
            sanitized = yaml.safe_load(f)
        assert sanitized["api"]["token"] == "***"
    finally:
        os.unlink(path)