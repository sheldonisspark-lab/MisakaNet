#!/usr/bin/env python3
"""Enhanced DCO validation script for MisakaNet.

This script validates commit messages for proper DCO sign-off format.
It fixes 2 false negatives found in the original check_dco regex:

1. Multiple Signed-off-by on a single line (TC1b)
2. Email containing spaces (TC2c)

Based on DCO benchmark whitepaper findings.
"""
from __future__ import annotations

import re
import sys
from collections.abc import Sequence

# Enhanced regex: fix TC1b (name excludes '<') and TC2c (email excludes spaces)
SIGNOFF_RE = re.compile(
    r'^Signed-off-by: (?P<name>[^<]+?) <(?P<email>[^\s>]+)>$',
    re.MULTILINE,
)


def check_message(message: str) -> tuple[bool, list[str]]:
    """Check a commit message string for valid DCO sign-off.

    Returns (passed, error_messages).
    """
    errors: list[str] = []

    if not message.strip():
        errors.append('check-dco: commit message is empty')
        return False, errors

    signoffs = SIGNOFF_RE.findall(message)

    if not signoffs:
        # Also check for malformed attempts
        for i, line in enumerate(message.splitlines(), start=1):
            stripped = line.strip()
            if stripped.lower().startswith('signed-off-by'):
                if not SIGNOFF_RE.match(line):
                    errors.append(
                        f'check-dco: line {i}: malformed Signed-off-by — '
                        f'expected "Signed-off-by: Name <email>" '
                        f'got: {stripped!r}'
                    )
        if not errors:
            errors.append(
                'check-dco: missing required Signed-off-by line. '
                'Use git commit -s to add one automatically.'
            )
        return False, errors

    return True, []


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print('check-dco: missing commit message filename', file=sys.stderr)
        return 1

    filename = argv[0]
    try:
        with open(filename, encoding='utf-8') as f:
            message = f.read()
    except OSError as e:
        print(f'check-dco: cannot read {filename}: {e}', file=sys.stderr)
        return 1

    passed, errors = check_message(message)

    if not passed:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
