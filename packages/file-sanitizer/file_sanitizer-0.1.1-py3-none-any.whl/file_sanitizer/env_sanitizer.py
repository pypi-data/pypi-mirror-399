"""ENV file sanitizer with embedded secret support"""
from pathlib import Path
from typing import List, Dict, Tuple
import re

from .utils import (
    load_rules,
    is_sensitive_key,
    smart_mask,
    partial_hash,
    redact_db_url_password
)
from .backup import create_backup, restore_backup

ENV_PAIR = re.compile(r"^\s*([A-Za-z0-9_\-\.]+)\s*=\s*(.*)$")


class EnvSanitizer:
    def __init__(self, rules_path: str = None):
        self.rules = load_rules(rules_path)

    def parse(self, text: str) -> List[Tuple[int, str, str]]:
        """Return list of (line_no, key, value)"""
        lines = text.splitlines()
        out = []
        for i, ln in enumerate(lines, start=1):
            m = ENV_PAIR.match(ln)
            if m:
                k = m.group(1)
                v = m.group(2)
                out.append((i, k, v))
        return out

    def scan(self, path: str) -> Dict:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="latin1")
        findings = []
        for ln, k, v in self.parse(text):
            if is_sensitive_key(k, self.rules) and v.strip() != "":
                findings.append({"line": ln, "key": k, "value": v})
            # Also flag potential embedded secrets in URLs
            elif any(trigger in k.lower() for trigger in ("url", "dsn", "connection", "database")) and "://" in v:
                findings.append({"line": ln, "key": k, "value": v, "type": "embedded_secret"})
        return {"file": str(p), "findings": findings}

    def sanitize(
        self,
        path: str,
        mask: str = "***",
        partial: bool = False,
        backup: bool = True,
        hash_values: bool = False,
    ) -> Dict:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="latin1")

        if backup:
            create_backup(str(p))

        lines = text.splitlines(keepends=False)
        modified = 0
        new_lines = []

        for ln in lines:
            m = ENV_PAIR.match(ln)
            if m:
                k = m.group(1)
                v = m.group(2)
                newv = v  # default: no change

                # Case 1: Key is explicitly sensitive (e.g., DB_PASSWORD)
                if is_sensitive_key(k, self.rules) and v.strip() != "":
                    if hash_values:
                        newv = partial_hash(v)
                    elif partial:
                        newv = smart_mask(v)
                    else:
                        newv = mask
                    modified += 1

                # Case 2: Key suggests it may contain a URL with embedded credentials
                elif any(trigger in k.lower() for trigger in ("url", "dsn", "connection", "database")) and "://" in v:
                    redacted = redact_db_url_password(v, mask)
                    if redacted != v:
                        newv = redacted
                        modified += 1

                if newv != v:
                    new_lines.append(f"{k}={newv}")
                    continue

            new_lines.append(ln)

        p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return {"file": str(p), "modified": modified}

    def undo(self, path: str) -> bool:
        return bool(restore_backup(path))