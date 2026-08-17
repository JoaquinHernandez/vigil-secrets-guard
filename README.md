# vigil-secrets-guard
# 🛡️ Vigil-Guard: Pre-Commit Secret Scanner & Entropy Radar

An ultra-fast, zero-dependency pre-commit credential detector designed to prevent accidental exposures of AWS keys, database passwords, private certificates, and high-entropy API tokens into public GitHub repositories.

---

## ✨ Features
- **Dual-Engine Detection**: Combines deterministic signature matching with **Shannon Entropy mathematical analysis** to catch arbitrary custom API tokens and hex keys.
- **Git Hook Ready**: Returns standard POSIX exit codes (`0` for clean, `1` for leak detected) to natively block `git commit` actions.
- **Zero Third-Party Dependencies**: Pure Python standard library implementation (`re`, `math`, `json`, `sys`).

---

## 🚀 Quick Start

### 1. Test Against the Included Vulnerable Sample
```bash
python3 vigil_guard.py sample_code_test.py

Scan Any File on Your System
Bash
python3 vigil_guard.py /path/to/your/code.py
3. Integrate as an Automatic Git Pre-Commit Hook
Prevent accidental leaks across any local repository by adding this single line into your .git/hooks/pre-commit file:

Bash
python3 /path/to/vigil_guard.py staged_files
