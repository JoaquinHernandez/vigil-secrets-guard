import os
import requests

# Normal safe application configuration
APP_NAME = "E-Commerce-Backend"
DEBUG_MODE = True

# --- CRITICAL ACCIDENTAL LEAKS BELOW (TEST PAYLOADS) ---
# 1. Leaked AWS IAM Token
AWS_CREDENTIAL_KEY = "AKIAIOSFODNN7EXAMPLE"

# 2. Leaked GitHub API Secret Token
GITHUB_SYNC_TOKEN = "ghp_99xAbCdef1234567890abcdefABCDEF1234"

# 3. Leaked Mongo Cloud Database Connection
DATABASE_URL = "mongodb://admin:SuperSecretPass99@cluster0.mongodb.net:27017/prod"

# 4. High-Entropy Custom API Key (Caught by mathematical randomness engine)
CUSTOM_VENDOR_HMAC = "f8a7c29b4e1d3056a9c8b7e6d5a43210feeb"

def fetch_data():
    print(f"Connecting using {APP_NAME}...")
