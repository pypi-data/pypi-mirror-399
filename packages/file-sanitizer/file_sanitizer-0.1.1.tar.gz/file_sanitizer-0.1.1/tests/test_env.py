import tempfile
import os
from file_sanitizer.env_sanitizer import EnvSanitizer


def test_env_sanitize_and_scan():
    # Use SAFE_VALUE to avoid false positive from "secret" in "NOTSECRET"
    sample = "DB_PASSWORD=supersecret\nSAFE_VALUE=value\nAPI_KEY=abcd1234\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(sample)
        path = f.name

    try:
        s = EnvSanitizer()
        scan = s.scan(path)
        assert len(scan["findings"]) == 2  # DB_PASSWORD and API_KEY only

        res = s.sanitize(path, partial=True)
        assert res["modified"] == 2

        with open(path) as f:
            content = f.read()
        # Verify actual partial mask output
        assert "su*******et" in content  # supersecret → 11 chars
        assert "ab****34" in content     # abcd1234 → 8 chars
    finally:
        os.unlink(path)