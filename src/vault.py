#!/usr/bin/env python3
"""
ZEUS OPS Encrypted Vault
Session-based secure key storage using Fernet (AES-128-CBC + HMAC).

All secrets are encrypted at rest. Decrypted only in memory for the session.
Never writes plaintext to disk.

Usage:
    from vault import Vault
    
    v = Vault()
    v.unlock()  # Prompts for master password once
    
    key = v.get("census_api_key")
    v.set("census_api_key", "abc123")
    v.save()
"""

import os
import json
import getpass
import hashlib
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_PATH = Path(__file__).parent.parent.parent / "sierra-vault.enc"
SALT_PATH = Path(__file__).parent.parent.parent / ".vault-salt"


class Vault:
    """Encrypted secrets vault. Decrypted in memory only."""
    
    def __init__(self, vault_path=None):
        self.vault_path = Path(vault_path) if vault_path else VAULT_PATH
        self.salt_path = SALT_PATH
        self._cache = None
        self._fernet = None
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive Fernet key from password + salt via PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _get_or_create_salt(self) -> bytes:
        """Load existing salt or generate a new one."""
        if self.salt_path.exists():
            return self.salt_path.read_bytes()
        salt = os.urandom(16)
        self.salt_path.write_bytes(salt)
        # Protect salt file
        os.chmod(self.salt_path, 0o600)
        return salt
    
    def unlock(self, password=None):
        """Unlock the vault with master password. Prompts if not provided."""
        if self._cache is not None:
            return True  # Already unlocked
        
        if password is None:
            password = os.environ.get("VAULT_PASSWORD")
        if password is None:
            password = getpass.getpass("🔐 Vault master password: ")
        
        salt = self._get_or_create_salt()
        key = self._derive_key(password, salt)
        self._fernet = Fernet(key)
        
        if self.vault_path.exists():
            try:
                encrypted = self.vault_path.read_bytes()
                decrypted = self._fernet.decrypt(encrypted)
                self._cache = json.loads(decrypted.decode())
            except Exception:
                print("❌ Wrong password or corrupted vault.")
                self._fernet = None
                return False
        else:
            # New vault
            self._cache = {}
        
        return True
    
    def get(self, key: str, default=None):
        """Get a secret. Auto-unlocks if needed."""
        if self._cache is None:
            if not self.unlock():
                return default
        return self._cache.get(key, default)
    
    def set(self, key: str, value: str):
        """Set a secret in memory cache."""
        if self._cache is None:
            raise RuntimeError("Vault is locked. Call unlock() first.")
        self._cache[key] = value
    
    def remove(self, key: str):
        """Remove a secret."""
        if self._cache is None:
            raise RuntimeError("Vault is locked. Call unlock() first.")
        self._cache.pop(key, None)
    
    def list_keys(self):
        """List all stored keys (values hidden)."""
        if self._cache is None:
            return []
        return list(self._cache.keys())
    
    def save(self):
        """Encrypt and save vault to disk."""
        if self._cache is None or self._fernet is None:
            raise RuntimeError("Vault is locked. Call unlock() first.")
        
        plaintext = json.dumps(self._cache, indent=2).encode()
        encrypted = self._fernet.encrypt(plaintext)
        self.vault_path.write_bytes(encrypted)
        os.chmod(self.vault_path, 0o600)
        print(f"🔒 Vault saved ({len(self._cache)} keys)")
    
    def status(self):
        """Show vault status."""
        exists = self.vault_path.exists()
        locked = self._cache is None
        return {
            "vault_file": str(self.vault_path),
            "exists": exists,
            "locked": locked,
            "keys_count": len(self._cache) if self._cache else 0,
        }
    
    def import_from_json(self, json_path: str, password=None):
        """Migrate an existing plaintext JSON into the encrypted vault."""
        if not self.unlock(password):
            return False
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # Skip non-secret metadata
        skip = {"created_at", "updated_at", "note"}
        for k, v in data.items():
            if k not in skip and isinstance(v, str) and not v.startswith("PASTE_"):
                self._cache[k] = v
        
        self.save()
        print(f"✅ Migrated {len(self._cache)} keys from {json_path}")
        return True


def main():
    """CLI for vault management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZEUS OPS Encrypted Vault")
    sub = parser.add_subparsers(dest="cmd")
    
    # init
    sub.add_parser("init", help="Create new vault")
    
    # status
    sub.add_parser("status", help="Show vault status")
    
    # list
    sub.add_parser("list", help="List all keys")
    
    # get
    get_p = sub.add_parser("get", help="Get a key")
    get_p.add_argument("key")
    
    # set
    set_p = sub.add_parser("set", help="Set a key")
    set_p.add_argument("key")
    set_p.add_argument("value")
    
    # remove
    rm_p = sub.add_parser("remove", help="Remove a key")
    rm_p.add_argument("key")
    
    # import
    imp_p = sub.add_parser("import", help="Import from JSON file")
    imp_p.add_argument("path")
    
    # export
    sub.add_parser("export", help="Export all keys as shell env vars")
    
    args = parser.parse_args()
    v = Vault()
    
    if args.cmd == "init":
        if v.vault_path.exists():
            print("⚠️  Vault already exists. Use 'set' to add keys.")
            return
        if not v.unlock():
            return
        v.save()
        print("🔐 New vault created.")
    
    elif args.cmd == "status":
        s = v.status()
        print(f"Vault:     {s['vault_file']}")
        print(f"Exists:    {'✅ Yes' if s['exists'] else '❌ No'}")
        print(f"Locked:    {'🔒 Yes' if s['locked'] else '🔓 Unlocked'}")
        print(f"Keys:      {s['keys_count']}")
    
    elif args.cmd == "list":
        if not v.unlock():
            return
        keys = v.list_keys()
        print(f"Keys ({len(keys)}):")
        for k in keys:
            val = v.get(k, "")
            status = "✅ Set" if val and not val.startswith("PASTE_") else "⚠️  Placeholder"
            print(f"  {k}: {status}")
    
    elif args.cmd == "get":
        if not v.unlock():
            return
        val = v.get(args.key)
        if val:
            # Show first/last 4 chars only
            masked = val[:4] + "..." + val[-4:] if len(val) > 12 else "***"
            print(f"{args.key}: {masked}")
        else:
            print(f"{args.key}: (not set)")
    
    elif args.cmd == "set":
        if not v.unlock():
            return
        v.set(args.key, args.value)
        v.save()
        print(f"✅ Set {args.key}")
    
    elif args.cmd == "remove":
        if not v.unlock():
            return
        v.remove(args.key)
        v.save()
        print(f"✅ Removed {args.key}")
    
    elif args.cmd == "import":
        v.import_from_json(args.path)
    
    elif args.cmd == "export":
        if not v.unlock():
            return
        print("# Run these in your shell to export vault keys as env vars:")
        print("# eval $(python3 vault.py export)")
        for k in v.list_keys():
            val = v.get(k)
            if val and not val.startswith("PASTE_"):
                print(f"export {k.upper()}='{val}'")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
