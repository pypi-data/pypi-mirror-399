"""YAML sanitizer (uses PyYAML)"""
from pathlib import Path
from typing import Any, Dict

from .utils import load_rules, is_sensitive_key, smart_mask, partial_hash
from .backup import create_backup, restore_backup
import yaml


class YamlSanitizer:
    def __init__(self, rules_path: str = None):
        self.rules = load_rules(rules_path)

    def scan(self, path: str) -> Dict:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="latin1")
        data = yaml.safe_load(text)
        if data is None:
            return {"file": str(p), "findings": []}

        findings = []

        def walker(o, parent=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    current_path = f"{parent}/{k}" if parent else k
                    if is_sensitive_key(k, self.rules):
                        if isinstance(v, (str, int, float)) and str(v).strip() != "":
                            findings.append({"key": k, "path": current_path, "value": v})
                    walker(v, current_path)
            elif isinstance(o, list):
                for i, item in enumerate(o):
                    walker(item, f"{parent}[{i}]")

        walker(data)
        return {"file": str(p), "findings": findings}

    def sanitize(
        self,
        path: str,
        mask: str = "***",
        backup: bool = True,
        partial: bool = False,
        hash_values: bool = False,
    ) -> Dict:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="latin1")

        data = yaml.safe_load(text)
        if data is None:
            return {"file": str(p), "modified": 0}

        if backup:
            create_backup(str(p))

        modified = 0

        def walker(o):
            nonlocal modified
            if isinstance(o, dict):
                for k in list(o.keys()):
                    v = o[k]
                    if is_sensitive_key(k, self.rules):
                        if isinstance(v, (str, int, float)) and str(v).strip() != "":
                            if hash_values:
                                o[k] = partial_hash(str(v))
                            elif partial:
                                o[k] = smart_mask(str(v))
                            else:
                                o[k] = mask
                            modified += 1
                        # Continue traversal even if key is sensitive (value may be nested)
                    walker(v)
            elif isinstance(o, list):
                for item in o:
                    walker(item)

        walker(data)
        p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return {"file": str(p), "modified": modified}

    def undo(self, path: str) -> bool:
        return bool(restore_backup(path))