#!/usr/bin/env python3
"""Patch two Omarchy system files so notification toasts and popup panels
account for this bar's floatGap instead of assuming a flush, marginless bar.

Both files read `shell.bar.floatGap` when present and fall back to 0 for
any other bar, so this is a no-op for anyone not using this plugin. Idempotent
and safe to re-run: skips files already patched, and refuses to touch a file
whose expected original snippet isn't found (e.g. a newer Omarchy release
changed it) rather than guessing.

Must run as root, since both files live under /usr/share/omarchy/. Run:
  sudo python3 patches/apply.py
"""

import os
import stat
import sys
import tempfile

PATCHES = [
    {
        "path": "/usr/share/omarchy/shell/plugins/notifications/Service.qml",
        "marker": "barEdgeMargin",
        "old": (
            "  readonly property int liveBarSize: shell && shell.bar && "
            "!shell.bar.barHidden ? Math.max(0, shell.bar.barSize) : defaultBarSize\n"
            "  readonly property int barClearance: liveBarSize + Style.gapsOut\n"
        ),
        "new": (
            "  readonly property int liveBarSize: shell && shell.bar && "
            "!shell.bar.barHidden ? Math.max(0, shell.bar.barSize) : defaultBarSize\n"
            "  // Bars that float away from the screen edge (e.g. charlieras262.floating-bar)\n"
            "  // expose their own edge margin as `floatGap`. Stock/other bars don't define\n"
            "  // it, so this stays 0 for them and behaves exactly as before.\n"
            "  readonly property real barEdgeMargin: shell && shell.bar && shell.bar.barHidden !== undefined\n"
            "    && shell.bar.floatGap !== undefined ? Math.max(0, Number(shell.bar.floatGap) || 0) : 0\n"
            "  readonly property int barClearance: liveBarSize + barEdgeMargin + Style.gapsOut\n"
        ),
    },
    {
        "path": "/usr/share/omarchy/shell/Ui/KeyboardPanel.qml",
        "marker": "barEdgeMargin",
        "old": (
            "  property bool open: false\n"
            "  property int gap: Style.gapsOut  // distance between bar edge and panel\n"
        ),
        "new": (
            "  property bool open: false\n"
            "  // Bars that float away from the screen edge (e.g. a floating-bar plugin)\n"
            "  // expose their own edge margin as `floatGap`. Stock/other bars don't\n"
            "  // define it, so this stays 0 for them and behaves exactly as before.\n"
            "  readonly property real barEdgeMargin: bar && bar.floatGap !== undefined\n"
            "    ? Math.max(0, Number(bar.floatGap) || 0) : 0\n"
            "  property int gap: Style.gapsOut + barEdgeMargin  // distance between bar edge and panel\n"
        ),
    },
]


def refuse_symlink(path: str) -> None:
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(st.st_mode):
        raise OSError("refusing symlink: %s" % path)


def apply_one(spec: dict) -> None:
    path = spec["path"]
    if not os.path.isfile(path):
        print(f"skip (not found): {path}")
        return
    refuse_symlink(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if spec["marker"] in text:
        print(f"already patched: {path}")
        return
    if spec["old"] not in text:
        print(
            f"WARNING: expected snippet not found, leaving untouched "
            f"(Omarchy may have changed this file since this patch was written): {path}",
            file=sys.stderr,
        )
        return

    backup = path + ".pre-floating-bar-patch.bak"
    if not os.path.exists(backup):
        with open(backup, "w", encoding="utf-8") as f:
            f.write(text)

    patched = text.replace(spec["old"], spec["new"], 1)
    parent = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=".patch.", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(patched)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print(f"patched: {path}")


def main() -> int:
    if os.geteuid() != 0:
        print("Run with sudo: sudo python3 patches/apply.py", file=sys.stderr)
        return 1
    for spec in PATCHES:
        apply_one(spec)
    print("Done. Run: omarchy restart shell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
