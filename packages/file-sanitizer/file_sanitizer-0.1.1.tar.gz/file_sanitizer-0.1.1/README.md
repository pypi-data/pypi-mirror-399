# 🔐 File Sanitizer

*Prevent secret leaks. Sanitize configs safely. Ship with confidence.*

**File Sanitizer** is a secure, developer-first CLI tool that **detects, masks, hashes, cleans, and restores** sensitive data across configuration files — **100% offline, audit-ready,** and **CI-friendly.**

Built for **developers, DevOps engineers, and security teams.**

---

## ✨ Why File Sanitizer?

🚨 Secrets in repositories are one of the top security risks.\
📤 Configs are constantly shared with teams, vendors, and auditors.\
❌ Manual redaction is error-prone and irreversible.

✔ Zero network calls.\
✔ Safe .bak backups\
✔ Human-readable + machine-readable reports\
✔ Works locally and in CI/CD pipelines

---

## 🌟 Key Features

| Feature                              | Description                                                                 |
| ------------------------------------ | --------------------------------------------------------------------------- |
| 🔍 **Smart Secret Detection**        | Detects secrets in keys **and embedded inside values** (URLs, tokens, DSNs) |
| 🎨 **Aesthetic CLI Output**          | Colorized, emoji-enhanced, human-friendly output                            |
| 📁 **Auto-Generated Reports**        | Creates `.json` (CI/automation) and `.txt` (audit-ready) reports            |
| 🧹 **Multiple Redaction Strategies** | Full mask, partial mask, or irreversible SHA-256 hashing                    |
| 🔁 **One-Click Undo**                | Restore originals from `.bak` backups                                       |
| 📊 **Format-Aware Intelligence**     | `.env`, `.json`, `.yaml`, `.csv` handled correctly                          |
| 🛠️ **Custom Rules**                 | Extend detection via `rules.json`                                           |
| 🔒 **100% Offline & Safe**           | No uploads, no telemetry, no tracking                                       |

---

## 📁 Supported File Types

| Format                 | Capabilities                         |
| ---------------------- | ------------------------------------ |
| `.env`, `.env.example` | URL-aware secret masking             |
| `.json`                | Deep nested traversal                |
| `.yaml`, `.yml`        | Recursive scan, formatting preserved |
| `.csv`                 | Column-aware redaction & cleanup     |

---

## 🚀 Installation
```bash
pip install file-sanitizer
```

---

## 🧾 Global CLI Syntax
```bash
filesan <command> <path> [options]
```

---

## Commands
| Command    | Description         |
| ---------- | ------------------- |
| `scan`     | Detect secrets      |
| `sanitize` | Redact / clean data |
| `undo`     | Restore originals   |

✔ PATH can be a file or directory

---

## 🔍 Scan (Detect Secrets)
```bash
filesan scan ./config/
```

## 📁 Auto-Generated Reports
```bash
./reports/
├── scan_YYYY-MM-DD_HH-MM-SS.json
└── scan_YYYY-MM-DD_HH-MM-SS.txt
```
✔ JSON → CI / automation\
✔ TXT → audit-ready, human-readable

## 📄 Sample TXT Report
```bash
🔥 FILE SANITIZER — SCAN REPORT
============================================================

📄 config.env
   • DB_PASSWORD  → supersecret123 (line 3)
   • API_KEY      → sk-abc123 (line 4)
   • DB_URL       → postgresql://user:***@host (line 5)

============================================================
⚠️  3 potential secret(s) detected.
============================================================
```
---
## 🧹 Sanitize (Redact Secrets)
🔸 **Full Mask (default)**
```bash
filesan sanitize config.env
filesan sanitize config.env --mask "[REDACTED]"
```

🔸 **Partial Mask**
```bash
filesan sanitize config.env --partial
```
🔸 **SHA-256 Hash (Irreversible)**
```bash
filesan sanitize secrets.yaml --hash
```

## 🔁 Undo (Restore Originals)
```bash
filesan undo config.env
```
✔ Restores from config.env.bak\
✔ Safe and instant

---
## 🔐 What Gets Sanitized?
**Default Sensitive Keywords**

Case-insensitive detection for:
```bash

password, passwd, pwd, secret, token, api_key, apikey,
access_key, client_secret, private_key, connection_string,
credential, auth, otp, key, db_url, dsn
```
---

## 🔍 Embedded Secret Detection (ENV Only)
```bash
DATABASE_URL=postgresql://admin:MyPass123@localhost/db
```

➡ Automatically becomes:
```bash

DATABASE_URL=postgresql://admin:***@localhost/db
```

✔ No extra flags required

---

## 🧩 Custom Rules

Create `rules.json`:
```bash
{
  "sensitive_keys": ["license_key", "jwt", "encryption_key"]
}
```

Use it:
```bash
filesan sanitize config.yaml --rules rules.json --partial
```

⚠️ `"sensitive_keys"` must be the top-level key

---

## 🔹 File-Type Specific Commands
### 1️⃣ ENV Files (.env, .env.example)
**✅ Commands**

`scan`, `sanitize`, `undo`

**⚙️ Valid Options**
| Flag            | Description        |
| --------------- | ------------------ |
| `--rules PATH`  | Custom rules       |
| `--mask STRING` | Full mask          |
| `--partial`     | Partial mask       |
| `--hash`        | SHA-256 hash       |
| `--json`        | Raw JSON output    |
| `--report PATH` | Custom JSON report |


**❌ Ignored:**
`--remove-nan`, `--delete-col`, `--drop-duplicates`

**📋 Examples**
```bash
filesan scan config.env
filesan scan config.env --report audit.json
filesan scan config.env --json

filesan sanitize config.env
filesan sanitize config.env --partial
filesan sanitize config.env --hash
filesan sanitize config.env --rules rules.json --partial

filesan undo config.env
```

---

## 2️⃣ JSON Files (.json)

Same behavior as `.env`
```bash
filesan scan app.json
filesan sanitize app.json --hash
filesan sanitize app.json --rules custom.json --partial
filesan undo app.json
```

---

## 3️⃣ YAML Files (.yaml, .yml)

Same behavior as `.env`
```bash
filesan scan k8s.yaml --report k8s_audit.json
filesan sanitize k8s.yaml --partial
filesan sanitize k8s.yaml --hash --rules prod.json
filesan undo k8s.yaml
```

---
## 4️⃣ CSV Files (.csv)
**⚙️ Valid Options**
| Flag                | Effect             |
| ------------------- | ------------------ |
| `--rules PATH`      | Sensitive columns  |
| `--mask STRING`     | Mask values        |
| `--partial`         | Partial mask       |
| `--hash`            | Hash values        |
| `--remove-nan`      | Drop empty rows    |
| `--delete-col NAME` | Remove column      |
| `--drop-duplicates` | Remove duplicates  |
| `--json`            | Raw JSON output    |
| `--report PATH`     | Custom JSON report |


⚠️ Cleanup flags are only valid with `sanitize`

**📋 Examples**
```bash
filesan scan users.csv
filesan scan users.csv --report users.json

filesan sanitize users.csv
filesan sanitize users.csv --partial
filesan sanitize users.csv --hash --rules pii.json
filesan sanitize users.csv --delete-col "ssn"
filesan sanitize users.csv --remove-nan --drop-duplicates

filesan sanitize users.csv \
  --partial \
  --delete-col "password" \
  --remove-nan \
  --drop-duplicates

filesan undo users.csv
```

## 📂 Directory Processing (Recursive)
```bash
filesan scan ./config/
filesan sanitize ./config/ --partial
filesan undo ./config/
```

✔ Skips unsupported files\
✔ Applies correct logic per file type\
✔ One consolidated report per scan\

---

## 📤 Output & Reporting Behavior
### 📝 Custom Report
```bash
filesan scan . --report out.json
```

✔ Saves JSON only\
❌ No TXT file

### 🖨️ Raw JSON Output
```bash
filesan scan . --json
filesan scan . --report out.json --json
```

---

## 🎯 Masking Priority (Sanitize)

Only *one* strategy is applied:
```bash
--hash     (highest)
--partial
--mask     (lowest)
```

Example:
```bash
filesan sanitize x.env --hash --partial --mask "XXX"
```

➡ Uses **HASHING**

---

## 🚫 Invalid Flag Combinations
| Command        | Invalid Flags                                       |
| -------------- | --------------------------------------------------- |
| `scan`, `undo` | `--remove-nan`, `--delete-col`, `--drop-duplicates` |


Error:
```bash
"only valid with sanitize"
```

---

## 🏢 Real-World Use Cases
### 🔐 Pre-Commit Secret Prevention
```bash
filesan scan .
# Fail commit if report contains ⚠️
```

### 📋 Compliance & Auditing

✔ SOC 2\
✔ ISO 27001\
✔ GDPR\

Human-readable `.txt` reports — no parsing required.

### ☁️ Cloud Migration
```bash
filesan scan terraform/
filesan sanitize terraform/ --hash
```
### 👥 Safe Cross-Team Sharing

Sanitize before sharing with **QA, support, vendors**\
Restore anytime with `filesan undo`

## 🧑‍💻 Development Setup
```bash
git clone https://github.com/your-username/file-sanitizer.git
cd file-sanitizer
pip install -e .
```
```bash
filesan scan manual_tests/
filesan sanitize manual_tests/test.env --partial
```

---

## ⚠️ Warning

This tool greatly reduces risk but manual review is always recommended before sharing sanitized files.

---

## 📜 License

MIT — free for commercial and personal use.

---

## 🙌 Built With

PyYAML — YAML parsing\
pandas — CSV intelligence\
hashlib — SHA-256 hashing\
Python Standard Library

🚫 No external APIs\
🚫 No telemetry\
🔒 100% Offline

---


## Author

- [V. Arvindh Kumar](https://github.com/arvindhvetri)

