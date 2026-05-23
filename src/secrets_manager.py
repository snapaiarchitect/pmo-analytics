#!/usr/bin/env python3
"""
ZEUS OPS Secrets Manager v2 — Encrypted Vault Integration

Reads from:
  1. Encrypted vault (sierra-vault.enc) — PRIMARY, most secure
  2. Plaintext sierra-secrets.json — FALLBACK, legacy
  3. Environment variable — OVERRIDE, highest priority

Never hardcode keys in source code.

Usage:
    from secrets_manager import get_secret, require_secret
    
    census_key = get_secret("census_api_key")
    usaspending_key = get_secret("usaspending_api_key")  # None if not set
"""

import json
import os
from pathlib import Path

# Try to load encrypted vault
VAULT_AVAILABLE = False
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from vault import Vault
    VAULT_AVAILABLE = True
except ImportError:
    pass

SECRETS_PATH = Path(__file__).parent.parent.parent / "sierra-secrets.json"


def _load_plaintext() -> dict:
    """Load from legacy sierra-secrets.json."""
    if not SECRETS_PATH.exists():
        return {}
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def get_secret(key: str, default=None):
    """
    Get a secret by key.
    Priority: 1) Environment variable, 2) Encrypted vault, 3) Plaintext JSON, 4) default
    """
    # 1. Environment variable (highest priority)
    env_val = os.environ.get(key.upper())
    if env_val:
        return env_val
    
    # 2. Encrypted vault (preferred secure storage)
    if VAULT_AVAILABLE:
        try:
            v = Vault()
            val = v.get(key)
            if val and not val.startswith("PASTE_"):
                return val
        except Exception:
            pass  # Vault locked or corrupted, fall through
    
    # 3. Plaintext JSON (legacy fallback)
    secrets = _load_plaintext()
    if key in secrets and secrets[key] and not secrets[key].startswith("PASTE_"):
        return secrets[key]
    
    # 4. Default fallback
    return default


def require_secret(key: str) -> str:
    """
    Get a secret or raise an error with setup instructions.
    Use for keys that MUST be present for the fetcher to work.
    """
    val = get_secret(key)
    if not val:
        raise RuntimeError(
            f"Missing required secret: '{key}'\n"
            f"Add it to the encrypted vault:\n"
            f"  cd sierra-pmo-analytics/src && python3 vault.py set {key} YOUR_KEY\n"
            f"Or set environment variable: {key.upper()}=your_key_here"
        )
    return val


def list_secrets() -> list[str]:
    """List all available secret keys from all sources."""
    keys = set()
    
    if VAULT_AVAILABLE:
        try:
            v = Vault()
            keys.update(v.list_keys())
        except Exception:
            pass
    
    secrets = _load_plaintext()
    keys.update(k for k in secrets.keys() if not k.startswith("_"))
    
    return sorted(keys)


if __name__ == "__main__":
    print("=== ZEUS OPS Secrets Manager v2 ===")
    print(f"Vault:    {'✅ Available' if VAULT_AVAILABLE else '❌ Not available'}")
    print(f"JSON:     {'✅ Found' if SECRETS_PATH.exists() else '❌ Not found'}")
    print(f"Path:     {SECRETS_PATH}")
    
    keys = list_secrets()
    print(f"\nAvailable keys ({len(keys)}):")
    for k in keys:
        val = get_secret(k)
        status = "✅ Set" if val else "❌ Missing / Placeholder"
        print(f"  {k}: {status}")
