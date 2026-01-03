"""Utility functions for file detection, rule loading, and value masking."""
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib


def detect_file_type(content: str, filename: str = None) -> str:
    """Detect file type based on extension and content."""
    if filename:
        fn = filename.lower()
        if fn.endswith(".json"):
            return "json"
        if fn.endswith(".yaml") or fn.endswith(".yml"):
            return "yaml"
        if fn.endswith(".env") or fn.endswith(".env.example"):
            return "env"
        if fn.endswith(".csv"):
            return "csv"

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not lines:
        return "unknown"

    # ENV detection: KEY=VALUE (allow dots, underscores, hyphens in key)
    if re.match(r"^[A-Za-z0-9_\-\.]+\s*=", lines[0]):
        return "env"

    # JSON detection: starts with { or [ after whitespace
    s = content.lstrip()
    if s.startswith("{") or s.startswith("["):
        try:
            json.loads(s)
            return "json"
        except (ValueError, TypeError):
            pass  # Not valid JSON, continue

    # CSV detection: at least one comma in first non-comment line
    if "," in lines[0]:
        return "csv"

    # YAML detection: contains colon + space (common pattern)
    if re.search(r"\w+\s*:\s*\S", content):
        return "yaml"

    return "unknown"


def load_rules(rules_path: Optional[str]) -> Dict[str, Any]:
    """Load sensitivity rules from JSON file. Returns default rules if None."""
    default_rules = {
        "sensitive_keys": [
            "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
            "access_key", "private_key", "ssh_key", "credential", "auth", "jwt",
            "encryption_key", "license_key", "db_password", "mysql_pwd", "user_password"
        ]
    }
    if rules_path is None:
        return default_rules
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # On failure, fall back to default rules (fail-safe)
        return default_rules


def is_sensitive_key(key: str, rules: Dict[str, Any]) -> bool:
    """Check if a key matches any sensitive pattern (case-insensitive, whole words only)."""
    key_lower = key.lower()
    sensitive_list = rules.get("sensitive_keys", [])
    for pattern in sensitive_list:
        # Match only if pattern appears as a whole word (with _ or . allowed as separators)
        if re.search(rf"(^|[_\-.]){re.escape(pattern)}([_\-.]|$)", key_lower):
            return True
    return False


def smart_mask(value: str) -> str:
    """Partially mask a value: show first 2 and last 2 chars, hide middle with *."""
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def partial_hash(value: str) -> str:
    """Return SHA-256 hash of the value (for irreversible anonymization)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# Regex to match user:password in database URLs
# Supports: postgresql://user:pass@host, mysql://..., redis://:pass@...
DB_URL_PATTERN = re.compile(
    r"([a-zA-Z0-9+.-]+://[^:@/]*):([^@]+)@",
    re.IGNORECASE
)


def redact_db_url_password(url: str, mask: str = "***") -> str:
    """
    Redact password in database URLs like:
    postgresql://user:secret@host → postgresql://user:***@host
    Returns original URL if no match.
    """
    def replace_password(match):
        scheme_user = match.group(1)
        return f"{scheme_user}:{mask}@"
    return DB_URL_PATTERN.sub(replace_password, url)