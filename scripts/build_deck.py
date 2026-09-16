#!/usr/bin/env python3
"""Build a rico-nice-ppt deck: chassis + one DNA (5 colour pairs x dark/light + 2 specials)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHASSIS = ROOT / "chassis" / "deck.html"
DNAS = ROOT / "dnas"
ICON_INDEX = ROOT / "assets" / "icons" / "lucide.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tokens import derive  # noqa: E402

# Import GEM sample fills from the previous builder if present.
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from content_fills import REPLACES as GEM_FILLS
except Exception:
    GEM_FILLS = []

# 产出 deck 必须离线可开：字体全部走本地 @font-face，不留任何在线字体请求。
# 以前这里是一段字面量替换，chassis 的注释一改就静默失配，产出仍在线加载
# Google Fonts。改成按 href 域名匹配，注释怎么改都不影响。
GFONT_HOST_RE = re.compile(
    r"[ \t]*<link\b[^>]*?(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*?/?>[ \t]*\n",
    re.S,
)
# 上面那段 link 之间夹着一条说明注释，一并清掉。
GFONT_NOTE_RE = re.compile(r"[ \t]*<!--\s*\n(?:[^\n]*font[^\n]*\n|[^\n]*\d\.[^\n]*\n)+[ \t]*-->[ \t]*\n")


def strip_google_fonts(html: str) -> str:
    head, sep, rest = html.partition("<style>")
    head = GFONT_HOST_RE.sub("", head)
    head = GFONT_NOTE_RE.sub("", head)
    return head + sep + rest


def faces_css(dna: dict, font_rel: str) -> str:
    chunks = []
    for f in dna["faces"]:
        chunks.append(
            f'@font-face{{font-family:"{f["family"]}";src:url("{font_rel}/{f["file"]}") format("woff2");font-weight:{f["weight"]};font-display:swap}}'
        )
    extra = dna.get("extra_css") or ""
    return "\n      ".join(chunks) + ("\n      " + extra if extra else "")


# The chassis ships a placeholder value for each derived slot so it still
# renders standalone; the build swaps each one for the solved colour.
DERIVED_SLOTS = {
    "--c-hairline": "hairline",
    "--c-accent-text": "accent_text",
    "--c-accent-fill": "accent_fill",
    "--c-fill": "fill",
    "--c-fill-2": "fill_2",
    "--c-ink2": "ink2",
    "--c-band-1": "band_1",
    "--c-band-2": "band_2",
    "--c-band-3": "band_3",
    "--c-band-4": "band_4",
    "--c-band-5": "band_5",
}

# 底盘预览用的本地 @font-face 块：build 时整块移除，换成该 DNA 自己的 faces。
CHASSIS_FACES_RE = re.compile(
    r"[ \t]*/\* chassis-faces:start \*/.*?/\* chassis-faces:end \*/[ \t]*\n",
    re.S,
)


def set_var(html: str, name: str, value: str) -> str:
    """按变量名替换 token 值。底盘默认值随便改，这里永不失配。"""
    pat = re.compile(r"(%s:\s*)[^;]+;" % re.escape(name))
    html, n = pat.subn(lambda m: m.group(1) + value + ";", html, count=1)
    if n == 0:
        raise SystemExit(f"chassis token missing: {name}")
    return html


def apply_dna(html: str, dna: dict, font_rel: str) -> str:
    c = derive(dna["colors"])
    f = dna["fonts"]
    html = strip_google_fonts(html)
    html = CHASSIS_FACES_RE.sub("", html)
    html = html.replace('<html lang="zh-CN">', f'<html lang="zh-CN" data-dna="{dna["slug"]}">')
    html = re.sub(r"<title>[^<]*</title>", f"<title>{dna['title_suffix']} · 样张</title>", html, count=1)
    html = html.replace("var(--c-fg-light-2)", "var(--c-fg-2)")
    html = html.replace("var(--c-fg-light-3)", "var(--c-fg-3)")
    html = html.replace("var(--c-fg-light)", "var(--c-fg)")
    html = html.replace("var(--c-bg-light-alt)", "var(--c-bg-alt)")
    html = html.replace("var(--c-bg-light)", "var(--c-bg)")
    html = html.replace("var(--c-border-light)", "var(--c-border)")
    for name, key in (
        ("--c-bg", "bg"), ("--c-bg-alt", "bg_alt"),
        ("--c-bg-light", "bg_light"), ("--c-bg-light-alt", "bg_light_alt"),
        ("--c-fg", "fg"), ("--c-fg-2", "fg_2"), ("--c-fg-3", "fg_3"),
        ("--c-fg-light", "fg_light"), ("--c-fg-light-2", "fg_light_2"),
        ("--c-fg-light-3", "fg_light_3"),
        ("--c-border", "border"), ("--c-border-light", "border_light"),
    ):
        html = set_var(html, name, c[key])
    html = set_var(html, "--c-accent", c["accent"])
    html = set_var(html, "--c-accent-dark", c.get("accent_dark", c["accent"]))
    html = set_var(html, "--c-accent-light", c.get("accent_light", c["accent"]))
    for name, key in DERIVED_SLOTS.items():
        html = set_var(html, name, c[key])
    for name, key in (
        ("--f-display", "display"), ("--f-heading", "heading"),
        ("--f-body", "body"), ("--f-mono", "mono"),
    ):
        html = set_var(html, name, f[key])
    html = html.replace("<style>", "<style>\n      " + faces_css(dna, font_rel), 1)
    if "googleapis.com" in html or "gstatic.com" in html:
        raise SystemExit("产出 deck 仍残留在线字体请求")
    return html


# ── Lucide 图标内联 ─────────────────────────────────────────────────────────
# markup 只写 <i class="ico ico--item" data-icon="store"></i>；这里把 path 数据
# 内联成 <svg>，产出仍是单文件离线。未知图标名直接报错，不静默留空。
ICON_TAG_RE = re.compile(r'<i\b((?:(?!>).)*?\bdata-icon="([\w-]+)"(?:(?!>).)*?)>\s*</i>')
_ICONS: dict | None = None


def inline_icons(html: str) -> str:
    global _ICONS
    if 'data-icon="' not in html:
        return html
    if _ICONS is None:
        _ICONS = json.loads(ICON_INDEX.read_text())

    def rep(m: re.Match) -> str:
        attrs, name = m.group(1), m.group(2)
        if name not in _ICONS:
            raise SystemExit(f"未知图标：{name}（用 scripts/find_icon.py 查名字）")
        return (
            f'<i{attrs}><svg viewBox="0 0 24 24" aria-hidden="true">'
            f'{_ICONS[name]["svg"]}</svg></i>'
        )

    return ICON_TAG_RE.sub(rep, html)


def inject_content(html: str, content: Path, title: str | None) -> str:
    """把手写的 slides_content.html 换进 #deck。开头的 <style> 块并进 <head>。"""
    body = content.read_text()
    style = ""
    if body.lstrip().startswith("<style>"):
        i = body.index("</style>") + len("</style>")
        style, body = body[:i], body[i:]
    start = html.index('<div id="deck">') + len('<div id="deck">')
    end = html.index("<!-- /deck -->")
    end = html.rindex("</div>", start, end)
    html = html[:start] + "\n" + body + "\n    " + html[end:]
    if style:
        html = html.replace("</head>", "    " + style + "\n  </head>", 1)
    if title:
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1)
    return html


def fill_sample(html: str) -> str:
    """Apply the sample copy.

    Matching ignores how the chassis happens to wrap and indent a run of text.
    An exact-string match silently left English placeholder copy in the deck
    the moment the markup was reformatted; `audit_copy` catches what survives.
    """
    for item in GEM_FILLS:
        needle, value = item[0], item[1]
        limit = item[2] if len(item) > 2 else 0
        pattern = re.compile(r"\s+".join(re.escape(w) for w in needle.split()))
        html = pattern.sub(lambda _m: value, html, count=limit)
    # Fills run in declaration order, so a broad needle can consume the token a
    # later, more specific pair was waiting for — `[Organization]` resolving
    # first left "样张 · [Period]" in fifteen slide footers. Sweep the
    # tokens that can survive that.
    for token, value in (
        ("[Period]", "2025"),
        ("[Year]", "2025"),
        ("[Organization]", "样张"),
    ):
        html = html.replace(token, value)
    return html


# Copy that must never reach a rendered slide.
BODY_RE = re.compile(r"<(?:div|p|li|h\d|span|figcaption)\b[^>]*>([^<]{12,})<", re.S)
PLACEHOLDER_RE = re.compile(r"\[[A-Z][a-z]+\]|Lorem ipsum|TODO|Image Placeholder|报告页")


def audit_copy(html: str) -> list[str]:
    """Residual English or bracket placeholder copy in visible slide text."""
    body = html.split("<body>", 1)[-1]
    found = []
    for m in BODY_RE.finditer(body):
        text = " ".join(m.group(1).split())
        if not text:
            continue
        if PLACEHOLDER_RE.search(text):
            found.append(text[:70])
        elif not re.search(r"[\u4e00-\u9fff]", text):
            # English prose in a Chinese deck is leftover sample copy. Source
            # citations are proper nouns, so count lowercase words to tell the
            # two apart: e.g. "Sources: 门禁脚本" has none.
            prose = [w for w in text.split() if w[:1].islower()]
            if len(prose) >= 3:
                found.append(text[:70])
    return sorted(set(found))


# 5 colour pairs: the same two hexes, swapped between paper and ink.
# dark = dark paper, light = light paper. Plus 2 specials that do not pair.
PAIRS = {
    "ink": {"dark": "ink", "light": "butter-ink"},
    "blue": {"dark": "cobalt", "light": "butter-blue"},
    "olive": {"dark": "olive-orange", "light": "orange-olive"},
    "purple": {"dark": "purple-yellow", "light": "yellow-purple"},
    "plum": {"dark": "plum-lilac", "light": "lilac-plum"},
}
SPECIALS = ["newspaper-front", "risograph"]


def resolve_slug(pair: str | None, mode: str | None, dna: str | None) -> str:
    if dna:
        return dna
    if not pair:
        raise SystemExit("need --dna <slug>, or --pair <id> --mode dark|light")
    if pair in SPECIALS:
        return pair
    if pair not in PAIRS:
        raise SystemExit(f"unknown pair {pair!r}; pairs: {', '.join(PAIRS)}; specials: {', '.join(SPECIALS)}")
    if mode not in ("dark", "light"):
        raise SystemExit(f"--pair {pair} needs --mode dark|light")
    return PAIRS[pair][mode]


def ensure_vendor_link(skin: Path) -> Path:
    """Ensure generated decks resolve assets/vendor without copying GSAP."""
    assets = skin / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    link = assets / "vendor"
    target = ROOT / "assets" / "vendor"
    relative_target = Path("../../../assets/vendor")

    if link.is_symlink():
        if link.resolve() != target.resolve():
            raise SystemExit(f"refusing to replace unexpected vendor symlink: {link}")
        return link
    if link.exists():
        raise SystemExit(f"refusing to replace existing vendor path: {link}")
    link.symlink_to(relative_target, target_is_directory=True)
    return link


def ensure_vendor_copy(out: Path) -> Path:
    """Copy GSAP next to an arbitrary --out deck so it stays offline-portable."""
    src = ROOT / "assets" / "vendor" / "gsap.min.js"
    dst = out.parent / "assets" / "vendor" / "gsap.min.js"
    if dst.resolve() == src.resolve():
        return dst
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    return dst


def ensure_fonts_copy(out: Path) -> Path:
    """Copy the font files next to an arbitrary --out deck (idempotent)."""
    src_dir = ROOT / "assets" / "fonts"
    dst_dir = out.parent / "assets" / "fonts"
    if dst_dir.resolve() == src_dir.resolve():
        return dst_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(src_dir.glob("*.woff2")):
        dst = dst_dir / src.name
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            continue
        dst.write_bytes(src.read_bytes())
    return dst_dir


def build(
    slug: str,
    out: Path,
    font_rel: str = "assets/fonts",
    content: Path | None = None,
    title: str | None = None,
) -> Path:
    dna = json.loads((DNAS / f"{slug}.json").read_text())
    html = CHASSIS.read_text()
    html = apply_dna(html, dna, font_rel)
    if content:
        html = inject_content(html, content, title)
    else:
        html = fill_sample(html)
    html = inline_icons(html)
    leftovers = audit_copy(html)
    if leftovers:
        print(f"  ! {slug}: placeholder copy still visible:")
        for line in leftovers:
            print(f"      {line}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dna", choices=[f.stem for f in DNAS.glob("*.json")], help="deck slug (direct)")
    p.add_argument("--pair", help="colour pair id: " + ", ".join(PAIRS) + "; or a special: " + ", ".join(SPECIALS))
    p.add_argument("--mode", choices=["dark", "light"], help="dark paper or light paper (with --pair)")
    p.add_argument("--out", help="output html path")
    p.add_argument("--content", help="手写的 slides_content.html，替换样张页（可带开头 <style> 块）")
    p.add_argument("--title", help="与 --content 搭配：<title>")
    p.add_argument("--all", action="store_true", help="build all twelve sample seeds")
    p.add_argument("--list", action="store_true", help="print pairs -> slugs and exit")
    args = p.parse_args()
    if args.list:
        for pid, m in PAIRS.items():
            print(f"{pid:8} dark={m['dark']:14} light={m['light']}")
        for sp in SPECIALS:
            print(f"{sp:8} (special, no pair)")
        return
    if args.all:
        for path_json in sorted(DNAS.glob("*.json")):
            slug = path_json.stem
            skin = ROOT / "skins" / slug
            (skin / "assets").mkdir(parents=True, exist_ok=True)
            fonts = skin / "assets" / "fonts"
            if not fonts.exists():
                fonts.symlink_to(ROOT / "assets" / "fonts")
            ensure_vendor_link(skin)
            path = skin / "seed.html"
            build(slug, path, font_rel="assets/fonts")
            print("wrote", path)
        return
    slug = resolve_slug(args.pair, args.mode, args.dna)
    out = Path(args.out) if args.out else ROOT / "skins" / slug / "seed.html"
    content = Path(args.content) if args.content else None
    print("wrote", build(slug, out, content=content, title=args.title))
    if args.out:
        print("vendor", ensure_vendor_copy(out.resolve()))
        print("fonts", ensure_fonts_copy(out.resolve()))


if __name__ == "__main__":
    main()
