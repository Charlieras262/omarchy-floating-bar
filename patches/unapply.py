#!/usr/bin/env python3
"""Restore the Omarchy system files patched by apply.py from their backups.

Run:
  sudo python3 patches/unapply.py
"""

import os
import sys

PATHS = [
    "/usr/share/omarchy/shell/plugins/notifications/Service.qml",
    "/usr/share/omarchy/shell/Ui/KeyboardPanel.qml",
]


def main() -> int:
    if os.geteuid() != 0:
        print("Run with sudo: sudo python3 patches/unapply.py", file=sys.stderr)
        return 1
    for path in PATHS:
        backup = path + ".pre-floating-bar-patch.bak"
        if not os.path.isfile(backup):
            print(f"no backup, skipping: {path}")
            continue
        os.replace(backup, path)
        print(f"restored: {path}")
    print("Done. Run: omarchy restart shell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
