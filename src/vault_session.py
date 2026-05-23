#!/usr/bin/env python3
"""
Vault Session Wrapper
Unlocks the encrypted vault, exports keys to environment variables,
then runs the target script with those env vars available.

Usage:
    python3 vault_session.py ../projects/executive-decision-support/src/download_census_exec.py

Or manually:
    eval $(python3 vault.py export)
    python3 download_census_exec.py
"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vault import Vault


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 vault_session.py <script.py> [args...]")
        print("Example: python3 vault_session.py ../projects/.../download_census_exec.py")
        sys.exit(1)
    
    script = Path(sys.argv[1]).resolve()
    script_args = sys.argv[2:]
    
    # Unlock vault
    v = Vault()
    if not v.unlock():
        print("❌ Vault unlock failed.")
        sys.exit(1)
    
    # Export keys to environment
    env = os.environ.copy()
    for k in v.list_keys():
        val = v.get(k)
        if val and not val.startswith("PASTE_"):
            env[k.upper()] = val
    
    print(f"🔓 Vault unlocked. Running: {script}")
    print(f"   Env vars set: {len(v.list_keys())} keys")
    
    # Run target script in its parent directory
    result = subprocess.run(
        [sys.executable, str(script)] + script_args,
        env=env,
        cwd=script.parent,
    )
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
