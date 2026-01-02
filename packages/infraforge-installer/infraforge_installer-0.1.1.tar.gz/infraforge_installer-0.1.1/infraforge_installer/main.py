#!/usr/bin/env python3
"""
InfraForge Installer (Artifact-based via GitHub Tags)
Free · Local · Open · Forever

Usage:
  infraforge-installer v0.9.2

Features:
- Downloads InfraForge release archive by tag
- Installs to /usr/local/InfraForge
- Forces executable permissions
- Creates /usr/local/bin/infraforge
- Auto-creates /usr/local/bin/infraforge-installer (one-time)
- Fully offline runtime
"""

import os
import sys
import subprocess
import tempfile
import urllib.request
from pathlib import Path

# ---------------- CONFIG ----------------

ORG = "InfraForgeLabs"
REPO = "InfraForge"

INSTALL_DIR = Path("/usr/local/InfraForge")
BIN_LINK = Path("/usr/local/bin/infraforge")
SELF_LINK = Path("/usr/local/bin/infraforge-installer")

REQUIRED_PATHS = [
    "bin/infraforge",
    "lib/core/common.sh",
    "lib/scripts",
]

# ---------------- UTILS ----------------

def info(msg: str):
    print(f"✔ {msg}")

def fatal(msg: str):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)

def require_root():
    if os.geteuid() != 0:
        fatal("Run as root: sudo infraforge-installer <tag>")

# ---------------- SELF SYMLINK ----------------

def ensure_self_symlink():
    """
    If running as root and installer is not available system-wide,
    create /usr/local/bin/infraforge-installer automatically.
    """
    try:
        if os.geteuid() != 0:
            return

        invoked_path = Path(sys.argv[0]).resolve()

        if SELF_LINK.exists():
            return

        if invoked_path.exists():
            os.symlink(invoked_path, SELF_LINK)
            info("Created system-wide installer symlink: /usr/local/bin/infraforge-installer")
    except Exception:
        # Non-fatal: installer must continue even if this fails
        pass

# ---------------- VALIDATION ----------------

def find_runtime_root(extracted_root: Path) -> Path:
    """
    Handles GitHub archive layouts:
      InfraForge-0.9.2/
      InfraForge-0.9.2/InfraForge/
    """
    if all((extracted_root / p).exists() for p in REQUIRED_PATHS):
        return extracted_root

    nested = extracted_root / REPO
    if nested.exists() and all((nested / p).exists() for p in REQUIRED_PATHS):
        return nested

    fatal("Invalid InfraForge artifact: runtime root not found")

# ---------------- CORE ----------------

def download_release(tag: str, dest: Path):
    url = f"https://github.com/{ORG}/{REPO}/archive/refs/tags/{tag}.tar.gz"
    info(f"Downloading InfraForge release {tag}")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        fatal(f"Failed to download release archive: {e}")

def main():
    require_root()
    ensure_self_symlink()

    if len(sys.argv) != 2:
        fatal("Usage: infraforge-installer <tag>   (example: v0.9.2)")

    tag = sys.argv[1]

    if INSTALL_DIR.exists():
        fatal(
            "InfraForge already installed at /usr/local/InfraForge\n"
            "Remove it first to reinstall."
        )

    with tempfile.TemporaryDirectory(prefix=".infraforge-tmp-", dir="/usr/local") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "infraforge.tar.gz"

        # 1️⃣ Download
        download_release(tag, archive)

        # 2️⃣ Extract
        info("Extracting InfraForge")
        subprocess.run(
            ["tar", "xzf", str(archive), "-C", str(tmp_path)],
            check=True
        )

        # 3️⃣ Locate extracted directory
        extracted_dirs = list(tmp_path.glob(f"{REPO}-*"))
        if len(extracted_dirs) != 1:
            fatal("Unexpected archive layout")

        extracted_root = extracted_dirs[0]
        runtime_root = find_runtime_root(extracted_root)

        # 4️⃣ Install
        info("Finalizing install")
        runtime_root.rename(INSTALL_DIR)

    # 5️⃣ FORCE EXECUTABLE PERMISSIONS (CRITICAL)
    subprocess.run(
        ["chmod", "+x", str(INSTALL_DIR / "bin/infraforge")],
        check=True
    )
    subprocess.run(
        ["chmod", "-R", "755", str(INSTALL_DIR / "bin")],
        check=True
    )

    # 6️⃣ Create infraforge symlink LAST
    if BIN_LINK.exists() or BIN_LINK.is_symlink():
        BIN_LINK.unlink()

    os.symlink(INSTALL_DIR / "bin/infraforge", BIN_LINK)

    info("InfraForge installed successfully")
    info("Run: infraforge --help")
    info("All generators run fully offline")

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    main()
