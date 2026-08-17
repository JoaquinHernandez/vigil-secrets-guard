import os
import sys
import re
import math
import json

# ANSI Color Codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[38;5;196m"
GREEN  = "\033[38;5;48m"
CYAN   = "\033[38;5;51m"
AMBER  = "\033[38;5;214m"
GRAY   = "\033[38;5;242m"

BANNER = f"""{CYAN}{BOLD}
 ██╗   ██╗██╗ ██████╗ ██╗██╗     ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ 
 ██║   ██║██║██╔════╝ ██║██║    ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
 ██║   ██║██║██║  ███╗██║██║    ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
 ╚██╗ ██╔╝██║██║   ██║██║██║    ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
  ╚████╔╝ ██║╚██████╔╝██║███████╗╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
   ╚═══╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
{RESET}{AMBER} » AUTOMATED PRE-COMMIT SECRET LEAK PREVENTION & ENTROPY RADAR «{RESET}
"""

class VigilSecretsGuard:
    def __init__(self, rules_path="rules_signatures.json"):
        if not os.path.exists(rules_path):
            print(f"{RED}[-] Error: Configuration rules '{rules_path}' not found.{RESET}")
            sys.exit(1)

        with open(rules_path, "r") as f:
            self.rules = json.load(f)

        self.signatures = self.rules.get("signatures", [])
        self.entropy_threshold = self.rules.get("entropy_threshold", 4.5)
        self.min_entropy_length = self.rules.get("min_entropy_length", 20)

    def calculate_shannon_entropy(self, text):
        """Calculates Shannon Entropy (randomness) of a string to detect custom API secrets."""
        if not text:
            return 0.0
        entropy = 0.0
        length = len(text)
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        for count in frequency.values():
            p_x = count / length
            entropy -= p_x * math.log2(p_x)
        return entropy

    def scan_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"{RED}[-] Target file '{file_path}' not found.{RESET}")
            sys.exit(1)

        print(BANNER)
        print(f"{BOLD}Target File Scanned:{RESET} {CYAN}{file_path}{RESET}")
        print("=" * 80)

        findings = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_idx, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#") or clean_line.startswith("//"):
                    continue

                # 1. Signature-Based Pattern Scans
                for sig in self.signatures:
                    match = re.search(sig["regex"], clean_line)
                    if match:
                        matched_val = match.group(0)
                        # Check prefix if rule enforces it (e.g. AKIA for AWS)
                        if sig.get("prefix_match") and not matched_val.startswith(sig["prefix_match"]):
                            continue
                        
                        findings.append({
                            "line": line_idx,
                            "name": sig["name"],
                            "severity": sig["severity"],
                            "leak_preview": matched_val[:6] + "..." + matched_val[-4:] if len(matched_val) > 10 else "***",
                            "detection_method": "Deterministic Regex Signature"
                        })

                # 2. Shannon Entropy String Scanning (Detects unformatted API keys & tokens)
                tokens = re.findall(r'[A-Za-z0-9_\-+/]{20,}', clean_line)
                for token in tokens:
                    entropy = self.calculate_shannon_entropy(token)
                    if entropy >= self.entropy_threshold:
                        # Avoid duplicates if signature already caught it
                        if not any(f["line"] == line_idx for f in findings):
                            findings.append({
                                "line": line_idx,
                                "name": "High-Entropy Secret / Custom Key",
                                "severity": "HIGH",
                                "leak_preview": token[:6] + "..." + token[-4:],
                                "detection_method": f"Shannon Entropy Analysis (Score: {entropy:.2f})"
                            })

        # Summary Display
        if not findings:
            print(f"{GREEN}{BOLD}[✓] SCAN CLEAN:{RESET} No unencrypted secrets, API tokens, or high-entropy credentials detected.")
            print(f"Git commit is safe to push upstream.\n")
            return 0
        else:
            print(f"{RED}{BOLD}[🚨 LEAKS PREVENTED] Blocked {len(findings)} secret exposure(s) before commit:{RESET}\n")
            for item in findings:
                print(f"  {RED}● Line {item['line']:<4}{RESET} [{BOLD}{item['severity']}{RESET}] {item['name']}")
                print(f"    {GRAY}├─ Detection: {item['detection_method']}{RESET}")
                print(f"    {GRAY}└─ Redacted Leaked Value:{RESET} {AMBER}{item['leak_preview']}{RESET}\n")
            
            print("=" * 80)
            print(f"{RED}{BOLD}[COMMIT REJECTED]{RESET} Remove or rotate the credentials above and use environment variables.")
            return 1

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "sample_code_test.py"
    scanner = VigilSecretsGuard()
    exit_code = scanner.scan_file(target)
    sys.exit(exit_code)
