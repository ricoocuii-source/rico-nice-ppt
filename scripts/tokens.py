#!/usr/bin/env python3
"""Derive the secondary colour ramp from a DNA's three source colours.

A DNA only has to declare `bg`, `fg` and `accent`. Everything a slide needs
below that — muted body text, mono labels, hairlines, chart fills, pyramid
bands — is solved for here against a contrast target instead of being picked
by hand, so no skin can ship an invisible caption again.
"""
from __future__ import annotations

# ── Targets, as WCAG contrast ratios against the paper colour ──────────────
# Slides are read from across a room and often through a washed-out projector,
# so the floors sit above the web minimums.
TARGETS = {
    "fg": 7.0,  # headlines, bullets, primary body
    "fg_2": 6.0,  # muted body: dense columns, flow/cycle/timeline descriptions
    # Mono chrome sits at 11px, so it gets the full small-text floor rather
    # than the 4.0 it used to carry — measured on screen, 4.0 rendered at
    # 3.6–3.9 once antialiasing thinned the strokes.
    "fg_3": 4.5,  # kickers, captions, axis labels, stamps, stat notes
    "accent_text": 4.6,  # accent used at body/label size
    "accent_fill": 3.0,  # accent as a block of colour (bars, swatches, rules)
    "fill": 3.2,  # neutral chart bars and donut segments
    "border": 2.1,  # hairlines and panel dividers
    "bg_alt": 1.12,  # secondary paper surface
}


def _srgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join("%02x" % max(0, min(255, round(c * 255))) for c in rgb)


def luminance(h: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in _srgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """t=0 → a, t=1 → b. Mixed in sRGB to match CSS color-mix(in srgb, …)."""
    ra, rb = _srgb(a), _srgb(b)
    return _hex(tuple(ra[i] * (1 - t) + rb[i] * t for i in range(3)))


def toward(ink: str, paper: str, target: float) -> str:
    """Fade `ink` toward `paper` as far as `target` contrast allows.

    Keeps the hue of the ink — a muted label stays the same colour family as
    the headline, it just steps back. If the ink cannot reach the target even
    undiluted, it is returned unfaded rather than silently failing.
    """
    if contrast(ink, paper) <= target:
        return ink
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if contrast(mix(ink, paper, mid), paper) >= target:
            lo = mid
        else:
            hi = mid
    return mix(ink, paper, lo)


def deepen(ink: str, paper: str, target: float) -> str:
    """Push `ink` away from `paper` (toward black or white) until it clears
    `target`. Used when a brand accent is too pale to carry small text."""
    if contrast(ink, paper) >= target:
        return ink
    anchor = "#000000" if luminance(paper) > 0.18 else "#ffffff"
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if contrast(mix(ink, anchor, mid), paper) >= target:
            hi = mid
        else:
            lo = mid
    return mix(ink, anchor, hi)


def shift_surface(paper: str, ink: str) -> str:
    """The alternate paper: a nudge of ink into the paper, enough to read as a
    distinct surface without becoming a second background colour."""
    return toward(ink, paper, TARGETS["bg_alt"])


def derive(colors: dict) -> dict:
    """Return `colors` with every derived slot filled in.

    Any slot already present and explicitly pinned by the DNA is preserved, so
    a skin can still override a single value when the derivation is wrong for
    it. Pinning is opt-in via a `pin` list.
    """
    bg = colors["bg"]
    fg = colors["fg"]
    accent = colors.get("accent", fg)
    pinned = set(colors.get("pin", []))

    out = dict(colors)

    def put(key: str, value: str) -> None:
        if key not in pinned:
            out[key] = value

    put("bg_alt", shift_surface(bg, fg))
    put("fg_2", toward(fg, bg, TARGETS["fg_2"]))
    put("fg_3", toward(fg, bg, TARGETS["fg_3"]))
    put("border", toward(fg, bg, TARGETS["border"]))
    put("hairline", toward(fg, bg, TARGETS["border"]))

    # Accent gets two forms: the brand colour as-is for large display type and
    # blocks of fill, and a deepened form for anything at label or body size.
    put("accent_fill", deepen(accent, bg, TARGETS["accent_fill"]))
    put("accent_text", deepen(accent, bg, TARGETS["accent_text"]))

    # Neutral chart ink — the non-highlighted bars and donut segments.
    put("fill", toward(fg, bg, TARGETS["fill"]))
    put("fill_2", toward(fg, bg, 2.2))

    # Pyramid / band ramp. The ceiling is set by what keeps the label on the
    # band readable: primary ink sits at ≥7:1 on paper, so a band capped at
    # 1.55:1 still leaves that label ≥4.5:1 against the band it covers. The
    # floor used to fade to 1.17, where the widest band dissolved into the
    # paper and the pyramid appeared to lose its base; the ramp is compressed
    # so the last step still reads, and every band is outlined besides.
    for i, ratio in enumerate((1.55, 1.48, 1.42, 1.36, 1.30), start=1):
        put(f"band_{i}", toward(fg, bg, ratio))

    # Light-surface aliases. This chassis uses one paper per deck, so the
    # `light` variants simply mirror the dark ones.
    for src, dst in (
        ("bg", "bg_light"),
        ("bg_alt", "bg_light_alt"),
        ("fg", "fg_light"),
        ("fg_2", "fg_light_2"),
        ("fg_3", "fg_light_3"),
        ("border", "border_light"),
    ):
        put(dst, out[src])
    put("accent_dark", accent)
    put("accent_light", accent)
    put("ink2", out.get("ink2", out["accent_text"]))

    out.pop("pin", None)
    return out


def report(slug: str, colors: dict) -> list[tuple[str, float, float, bool]]:
    """Measured contrast for every slot that carries meaning, for the gate."""
    bg = colors["bg"]
    checks = [
        ("fg", colors["fg"], TARGETS["fg"]),
        ("fg_2", colors["fg_2"], TARGETS["fg_2"]),
        ("fg_3", colors["fg_3"], TARGETS["fg_3"]),
        ("accent_text", colors["accent_text"], TARGETS["accent_text"]),
        ("accent_fill", colors["accent_fill"], TARGETS["accent_fill"]),
        ("fill", colors["fill"], TARGETS["fill"]),
        ("border", colors["border"], TARGETS["border"]),
        ("band_1", colors["band_1"], 1.45),
    ]
    rows = []
    for name, value, target in checks:
        got = contrast(value, bg)
        rows.append((name, got, target, got >= target - 0.02))
    # The pyramid label rides on the widest band, so check it there too.
    on_band = contrast(colors["fg"], colors["band_1"])
    rows.append(("fg/band_1", on_band, 4.5, on_band >= 4.48))
    return rows
