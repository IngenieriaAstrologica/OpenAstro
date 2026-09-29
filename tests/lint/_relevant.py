# -*- coding: utf-8 -*-
"""Does this hook payload concern a Python file in this project?

Reads the PostToolUse JSON on stdin, prints "yes" or "no". Used by
on_edit.sh so the hook stays out of quoting trouble, and so the decision can
be tested on its own:

    echo '{"tool_input":{"file_path":"C:\\\\x\\\\openastro"}}' \\
        | python3 tests/lint/_relevant.py /mnt/c/x

Anything it cannot parse is "no": a hook that guesses wrong in that
direction merely skips a check, while guessing wrong the other way runs the
lint against unrelated files and reports nonsense.
"""
import json
import os
import sys


def wsl_path(path):
    """C:\\a\\b -> /mnt/c/a/b, leaving POSIX paths alone."""
    if len(path) > 2 and path[1] == ":":
        return "/mnt/" + path[0].lower() + path[2:].replace("\\", "/")
    return path


def main():
    root = os.path.realpath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    try:
        data = json.load(sys.stdin)
    except Exception:
        return "no"
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path:
        return "no"
    path = os.path.realpath(wsl_path(path))
    if not (path == root or path.startswith(root + os.sep)):
        return "no"
    # the main script has no extension; everything else we lint is .py
    if path.endswith(".py") or os.path.basename(path) == "openastro":
        return "yes"
    return "no"


print(main())
