#!/usr/bin/env python3
"""Contrast gate for every DNA. Fails if any skin ships unreadable ink.

    python3 scripts/check_contrast.py          # all skins
    python3 scripts/check_contrast.py ink      # one skin
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tokens import derive, report  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DNAS = ROOT / "dnas"


def main() -> int:
    slugs = sys.argv[1:] or sorted(p.stem for p in DNAS.glob("*.json"))
    slots = None
    failures = []

    for slug in slugs:
        colors = derive(json.loads((DNAS / f"{slug}.json").read_text())["colors"])
        rows = report(slug, colors)
        if slots is None:
            slots = [r[0] for r in rows]
            print(f"{'skin':<17}" + "".join(f"{s:>13}" for s in slots))
        line = f"{slug:<17}"
        for name, got, target, ok in rows:
            line += f"{got:>12.2f}{'' if ok else '!'}"
            if not ok:
                failures.append(f"{slug}.{name}: {got:.2f} < {target}")
        print(line)

    if failures:
        print("\nFAIL — below contrast floor:")
        for f in failures:
            print("  " + f)
        return 1
    print("\nOK — all slots clear their contrast floor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
