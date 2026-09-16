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
DERIVED_DEFAULTS = {
    "--c-hairline": ("#6a7690", "hairline"),
    "--c-accent-text": ("var(--c-accent)", "accent_text"),
    "--c-accent-fill": ("var(--c-accent)", "accent_fill"),
    "--c-fill": ("#7c88a0", "fill"),
    "--c-fill-2": ("#5e6a80", "fill_2"),
    "--c-ink2": ("var(--c-accent-text)", "ink2"),
    "--c-band-1": ("#55617a", "band_1"),
    "--c-band-2": ("#4a566e", "band_2"),
    "--c-band-3": ("#404c63", "band_3"),
    "--c-band-4": ("#384358", "band_4"),
    "--c-band-5": ("#313c50", "band_5"),
}


def apply_derived(html: str, c: dict) -> str:
    for var, (placeholder, key) in DERIVED_DEFAULTS.items():
        needle = f"{var}: {placeholder};"
        if needle not in html:
            raise SystemExit(f"chassis is missing the placeholder for {var}")
        html = html.replace(needle, f"{var}: {c[key]};", 1)
    return html


def apply_dna(html: str, dna: dict, font_rel: str) -> str:
    c = derive(dna["colors"])
    f = dna["fonts"]
    html = strip_google_fonts(html)
    html = html.replace('<html lang="zh-CN">', f'<html lang="zh-CN" data-dna="{dna["slug"]}">')
    html = html.replace("<title>Deck Template</title>", f"<title>{dna['title_suffix']} · 样张</title>")
    html = html.replace("var(--c-fg-light-2)", "var(--c-fg-2)")
    html = html.replace("var(--c-fg-light-3)", "var(--c-fg-3)")
    html = html.replace("var(--c-fg-light)", "var(--c-fg)")
    html = html.replace("var(--c-bg-light-alt)", "var(--c-bg-alt)")
    html = html.replace("var(--c-bg-light)", "var(--c-bg)")
    html = html.replace("var(--c-border-light)", "var(--c-border)")
    html = html.replace("--c-bg: #1c2644", f"--c-bg: {c['bg']}")
    html = html.replace("--c-bg-alt: #232f55", f"--c-bg-alt: {c['bg_alt']}")
    html = html.replace("--c-bg-light: #f0ece3", f"--c-bg-light: {c['bg_light']}")
    html = html.replace("--c-bg-light-alt: #e6e0d4", f"--c-bg-light-alt: {c['bg_light_alt']}")
    html = html.replace("--c-fg: #e2dcd0", f"--c-fg: {c['fg']}")
    html = html.replace("--c-fg-2: #8a96a8", f"--c-fg-2: {c['fg_2']}")
    html = html.replace("--c-fg-3: #4e5a6e", f"--c-fg-3: {c['fg_3']}")
    html = html.replace("--c-fg-light: #1a2030", f"--c-fg-light: {c['fg_light']}")
    html = html.replace("--c-fg-light-2: #5a6270", f"--c-fg-light-2: {c['fg_light_2']}")
    html = html.replace("--c-fg-light-3: #9aa0a8", f"--c-fg-light-3: {c['fg_light_3']}")
    html = html.replace("--c-accent: #c8a870", f"--c-accent: {c['accent']}")
    html = html.replace("--c-accent-dark: #c8a870", f"--c-accent-dark: {c.get('accent_dark', c['accent'])}")
    html = html.replace("--c-accent-light: #c8a870", f"--c-accent-light: {c.get('accent_light', c['accent'])}")
    html = html.replace("--c-border: #2e3d5c", f"--c-border: {c['border']}")
    html = html.replace("--c-border-light: #cac4b4", f"--c-border-light: {c['border_light']}")
    html = apply_derived(html, c)
    html = html.replace(
        '--f-display: "Source Serif 4", "Noto Serif SC", Georgia, serif;',
        f"--f-display: {f['display']};",
    )
    html = html.replace(
        '--f-heading: "Source Serif 4", "Noto Serif SC", Georgia, serif;',
        f"--f-heading: {f['heading']};",
    )
    html = html.replace(
        '--f-body: "DM Sans", "Noto Sans SC", system-ui, sans-serif;',
        f"--f-body: {f['body']};",
    )
    html = html.replace(
        '--f-mono: "IBM Plex Mono", "JetBrains Mono", monospace;',
        f"--f-mono: {f['mono']};",
    )
    html = html.replace("<style>", "<style>\n      " + faces_css(dna, font_rel), 1)
    if "googleapis.com" in html or "gstatic.com" in html:
        raise SystemExit("产出 deck 仍残留在线字体请求")
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
    # first left `Stanford HAI · [Period]` in fifteen slide footers. Sweep the
    # tokens that can survive that.
    for token, value in (
        ("[Period]", "2025"),
        ("[Year]", "2025"),
        ("[Organization]", "Stanford HAI"),
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
            # two apart: "Sources: Stanford HAI AI Index 2025" has none.
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


def build(slug: str, out: Path, font_rel: str = "assets/fonts") -> Path:
    dna = json.loads((DNAS / f"{slug}.json").read_text())
    html = CHASSIS.read_text()
    html = apply_dna(html, dna, font_rel)
    html = fill_sample(html)
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
    print("wrote", build(slug, out))
    if args.out:
        print("vendor", ensure_vendor_copy(out.resolve()))
        print("fonts", ensure_fonts_copy(out.resolve()))


if __name__ == "__main__":
    main()
