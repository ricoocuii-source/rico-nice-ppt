#!/usr/bin/env python3
"""按英文关键词在离线 Lucide 索引里找图标。

用法：python3 scripts/find_icon.py tea risk "supply chain"
名字命中优先，其次官方 tags。索引 assets/icons/lucide.json 由本地 lucide-react 的
path 数据 + 官方 tags.json 合成，1711 个图标，离线可用。
"""
import json
import sys
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "assets" / "icons" / "lucide.json"


def find(query: str, limit: int = 14) -> tuple[list[str], list[str]]:
    d = json.load(open(INDEX))
    q = query.lower().strip()
    by_name = [n for n in d if q in n]
    by_tag = [
        n for n, v in d.items()
        if n not in by_name and any(q == t or q in t.split() for t in v["tags"])
    ]
    return by_name[:limit], by_tag[:limit]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for q in sys.argv[1:]:
        names, tags = find(q)
        print(f"## {q}\n  name: {', '.join(names) or '—'}\n  tags: {', '.join(tags) or '—'}")
