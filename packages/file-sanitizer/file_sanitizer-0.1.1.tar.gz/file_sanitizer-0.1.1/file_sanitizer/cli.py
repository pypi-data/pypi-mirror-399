"""Simple CLI entrypoint for File Sanitizer — with aesthetic output"""
import argparse
import json
import sys
import datetime
from pathlib import Path

from .utils import detect_file_type
from .env_sanitizer import EnvSanitizer
from .yaml_sanitizer import YamlSanitizer
from .json_sanitizer import JsonSanitizer
from .csv_sanitizer import CsvSanitizer


# ANSI color codes (works in modern terminals, including Windows 10+)
class Colors:
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    INFO = '\033[94m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ENDC = '\033[0m'


def cprint(text, color=None):
    if color:
        print(f"{color}{text}{Colors.ENDC}")
    else:
        print(text)


def divider():
    cprint("─" * 60, Colors.DIM)


# ------------------ AESTHETIC HELP FORMATTER ------------------ #
class AestheticHelpFormatter(argparse.RawTextHelpFormatter):
    def start_section(self, heading):
        heading = f"{Colors.BOLD}{heading.upper()}{Colors.ENDC}"
        super().start_section(heading)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)
        opts = ", ".join(action.option_strings)
        return f"  {Colors.OKGREEN}{opts}{Colors.ENDC}"


# ------------------ SANITIZER SELECTOR ------------------ #
def choose_sanitizer(ftype: str, rules: str = None):
    if ftype == "env":
        return EnvSanitizer(rules)
    if ftype == "json":
        return JsonSanitizer(rules)
    if ftype == "yaml":
        return YamlSanitizer(rules)
    if ftype == "csv":
        return CsvSanitizer(rules)
    return None


# ------------------ OUTPUT PRINTERS ------------------ #
def print_scan_results(results):
    total_findings = 0

    divider()
    cprint("🔍 Scan Results", Colors.BOLD)
    divider()

    for res in results:
        findings = res.get("findings", [])

        if findings:
            cprint(f"\n📄 {res['file']}", Colors.BOLD)
            for f in findings:
                key = f["key"]
                value = f["value"]
                location = ""
                if "line" in f:
                    location = f"(line {f['line']})"
                elif "col" in f:
                    location = f"(row {f['row']}, col {f['col']})"

                cprint(f"   • {key:<20} → {value} {location}", Colors.WARN)

            total_findings += len(findings)
        else:
            cprint(f"\n✅ {res['file']}", Colors.OKGREEN)
            cprint("   No sensitive data detected", Colors.DIM)

    divider()
    if total_findings == 0:
        cprint("✨ Scan completed successfully — no secrets found.", Colors.OKGREEN)
    else:
        cprint(f"⚠️  Scan completed — {total_findings} potential secret(s) detected.", Colors.WARN)
    divider()


def print_sanitize_results(results):
    modified = 0

    divider()
    cprint("🧹 Sanitization Summary", Colors.BOLD)
    divider()

    for res in results:
        if res.get("modified", 0) > 0:
            cprint(
                f"✔ {res['file']} — {res['modified']} value(s) sanitized",
                Colors.OKGREEN
            )
            modified += res["modified"]
        else:
            cprint(
                f"↪ {res['file']} — No changes required",
                Colors.DIM
            )

    divider()
    if modified > 0:
        cprint(
            f"✅ Sanitization complete — {modified} sensitive value(s) secured.",
            Colors.OKGREEN
        )
        cprint("📦 Backup files saved with .bak extension", Colors.DIM)
    else:
        cprint("ℹ️  No files required sanitization.", Colors.INFO)
    divider()


def print_undo_results(results):
    restored = 0

    divider()
    cprint("↩️  Restore Summary", Colors.BOLD)
    divider()

    for res in results:
        if res.get("restored"):
            cprint(
                f"✔ {res['file']} — Restored from backup",
                Colors.OKGREEN
            )
            restored += 1
        else:
            cprint(
                f"✖ {res['file']} — No backup found",
                Colors.FAIL
            )

    divider()
    if restored > 0:
        cprint(
            f"🔄 Restore completed — {restored} file(s) recovered.",
            Colors.OKGREEN
        )
    else:
        cprint("ℹ️  No files were restored.", Colors.INFO)
    divider()

def generate_beautiful_report_text(results) -> str:
    """Generate a human-readable report as plain text (for saving to .txt)"""
    lines = []
    lines.append("🔥 FILE SANITIZER — SCAN REPORT")
    lines.append("=" * 60)
    
    total_findings = 0
    for res in results:
        findings = res.get("findings", [])
        if findings:
            lines.append(f"\n📄 {res['file']}")
            for f in findings:
                key = f["key"]
                value = f["value"]
                location = ""
                if "line" in f:
                    location = f"(line {f['line']})"
                elif "col" in f:
                    location = f"(row {f['row']}, col {f['col']})"
                lines.append(f"   • {key:<20} → {value} {location}")
            total_findings += len(findings)
        else:
            lines.append(f"\n✅ {res['file']} — No secrets found")

    lines.append("\n" + "=" * 60)
    if total_findings == 0:
        lines.append("✨ No sensitive data detected.")
    else:
        lines.append(f"⚠️  {total_findings} potential secret(s) detected.")
    lines.append("=" * 60)
    
    return "\n".join(lines)

# ------------------ MAIN ------------------ #
def main():
    parser = argparse.ArgumentParser(
        prog="filesan",
        description=f"""{Colors.BOLD}File Sanitizer CLI{Colors.ENDC}
Securely scan, sanitize, and restore sensitive data.
Supports ENV, JSON, YAML, and CSV files.""",
        epilog=f"""{Colors.DIM}
Examples:
  filesan scan ./configs
  filesan sanitize secrets.json --partial
  filesan undo secrets.json
{Colors.ENDC}""",
        formatter_class=AestheticHelpFormatter
    )

    parser.add_argument("command", choices=["scan", "sanitize", "undo"])
    parser.add_argument("path", help="File or directory path")

    parser.add_argument("--rules", help="Path to custom rules.json")
    parser.add_argument("--mask", default="***", help="Mask string for sensitive values")
    parser.add_argument("--partial", action="store_true", help="Use partial masking")
    parser.add_argument("--hash", action="store_true", help="Use SHA-256 hashing")

    parser.add_argument("--remove-nan", action="store_true", help="CSV only: remove NaN rows")
    parser.add_argument("--delete-col", help="CSV only: delete column by name")
    parser.add_argument("--drop-duplicates", action="store_true", help="CSV only: drop duplicates")

    parser.add_argument("--report", help="Write scan report to JSON file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if args.report and args.command != "scan":
        parser.error("--report can only be used with 'scan'")

    if args.command != "sanitize" and (
        args.remove_nan or args.delete_col or args.drop_duplicates
    ):
        parser.error("CSV options are only valid with 'sanitize'")

    path = Path(args.path)
    if not path.exists():
        cprint(f"❌ Path does not exist: {path}", Colors.FAIL)
        sys.exit(1)

    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.*"))
        if not files:
            cprint("ℹ️ No supported files found in directory.", Colors.INFO)
            return

    results = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            cprint(f"⚠️ Skipping {f} — unreadable file", Colors.WARN)
            continue

        ftype = detect_file_type(content, str(f))
        if not ftype:
            continue

        sanitizer = choose_sanitizer(ftype, args.rules)
        if not sanitizer:
            continue

        if args.command == "scan":
            results.append(sanitizer.scan(str(f)))
        elif args.command == "sanitize":
            results.append(
                sanitizer.sanitize(
                    str(f),
                    mask=args.mask,
                    partial=args.partial,
                    backup=True,
                    hash_values=args.hash,
                    remove_nan=args.remove_nan,
                    delete_col=args.delete_col,
                    drop_duplicates=args.drop_duplicates,
                )
            )
        elif args.command == "undo":
            results.append({"file": str(f), "restored": sanitizer.undo(str(f))})

    # Output handling
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.command == "scan":
        json_data = json.dumps(results, indent=2, ensure_ascii=False)
        beautiful_text = generate_beautiful_report_text(results)

        try:
            if args.report:
                # User-specified path → save only JSON (as expected)
                report_path = Path(args.report).resolve()
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json_data, encoding="utf-8")
                cprint(f"\n📄 Scan report saved to: {report_path}", Colors.INFO)
            else:
                # Auto-save both JSON and TXT in ./reports/
                reports_dir = Path("reports")
                reports_dir.mkdir(exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                
                json_path = reports_dir / f"scan_{timestamp}.json"
                txt_path = reports_dir / f"scan_{timestamp}.txt"
                
                json_path.write_text(json_data, encoding="utf-8")
                txt_path.write_text(beautiful_text, encoding="utf-8")
                
                cprint(f"\n📄 Reports saved to:", Colors.INFO)
                cprint(f"   JSON : {json_path}", Colors.DIM)
                cprint(f"   TXT  : {txt_path}", Colors.DIM)
                
        except Exception as e:
            cprint(f"❌ Failed to write report: {e}", Colors.FAIL)
            sys.exit(1)
            # Do NOT print scan results to terminal (silent by design)
            
            try:
                report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
                cprint(f"\n📄 Scan report saved to: {report_path}", Colors.INFO)
            except Exception as e:
                cprint(f"❌ Failed to write report: {e}", Colors.FAIL)
                sys.exit(1)

        #print_scan_results(results)
    elif args.command == "sanitize":
        print_sanitize_results(results)
    elif args.command == "undo":
        print_undo_results(results)


if __name__ == "__main__":
    main()