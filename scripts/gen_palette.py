#!/usr/bin/env python3
"""
gen_palette.py — build a contrast-safe post-to-visual palette from one accent hex.

Give it your primary accent colour; it derives a full light + dark token set that drops
straight into a page's `:root{}` / dark block, or into assets/themes.css as a named palette.
Pure standard library (colorsys). No deps.

  python3 gen_palette.py "#7C3AED"
  python3 gen_palette.py "#7C3AED" --secondary "#0EA5A4" --neutral cool --name violet
  python3 gen_palette.py "#7C3AED" --format themes >> ../assets/themes.css

What it does and doesn't touch:
  - DERIVES the primary slot (`--indigo`) and secondary slot (`--teal`) from your hue(s),
    plus their `-bg` tints and `-solid` (white-text-safe in BOTH modes).
  - KEEPS amber / coral / green as semantic constants (warn / bad / good) so meaning holds.
  - Neutrals come from a `warm` (default) or `cool` preset.
The `-solid` tokens are auto-darkened until white text clears a 4:1 contrast ratio, so the
dark-mode contrast trap can't sneak in.
"""

import argparse
import colorsys
import sys

WHITE = "#FFFFFF"


# ---- colour helpers --------------------------------------------------------

def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def hls_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return rgb2hex((r * 255, g * 255, b * 255))


def hex_hls(hx):
    r, g, b = (c / 255 for c in hex2rgb(hx))
    return colorsys.rgb_to_hls(r, g, b)  # (h, l, s)


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hx):
    r, g, b = hex2rgb(hx)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def solid(h, s, target=4.0, start_l=0.45):
    """A mid-dark fill that white text clears `target` contrast on — in either theme."""
    l = start_l
    for _ in range(40):
        hx = hls_hex(h, l, max(s, 0.55))
        if contrast(hx, WHITE) >= target:
            return hx
        l -= 0.02
    return hls_hex(h, max(l, 0.10), max(s, 0.55))


# ---- neutral presets (from the shipped editorial / slate palettes) ---------

NEUTRALS = {
    "warm": {
        "light": dict(bg_primary="#FAFAF8", bg_secondary="#F2F1EC", bg_card="#FFFFFF", bg_code="#F4F3EF",
                      bg_nav="rgba(250,250,248,.85)", text_primary="#1A1A18", text_secondary="#52514C",
                      text_tertiary="#8A887F", border_default="#E3E1DA", border_light="#EDEBE4"),
        "dark": dict(bg_primary="#15140F", bg_secondary="#1D1C16", bg_card="#23211A", bg_code="#1A1914",
                     bg_nav="rgba(21,20,15,.85)", text_primary="#F1EFE6", text_secondary="#BFBCB0",
                     text_tertiary="#85827A", border_default="#34322A", border_light="#2A281F"),
    },
    "cool": {
        "light": dict(bg_primary="#FBFCFD", bg_secondary="#F1F3F6", bg_card="#FFFFFF", bg_code="#F1F4F8",
                      bg_nav="rgba(251,252,253,.85)", text_primary="#0F1722", text_secondary="#475063",
                      text_tertiary="#8A93A3", border_default="#E1E5EC", border_light="#EBEEF3"),
        "dark": dict(bg_primary="#0D1117", bg_secondary="#151B23", bg_card="#1A212B", bg_code="#12181F",
                     bg_nav="rgba(13,17,23,.85)", text_primary="#EAEEF4", text_secondary="#AEB7C4",
                     text_tertiary="#7C8696", border_default="#2A323D", border_light="#222933"),
    },
}

# semantic anchors (warn / bad / good) — kept constant so meaning is stable
SEMANTIC = {
    "light": dict(amber="#B45309", amber_bg="#FBF1E3", coral="#DC2626", coral_bg="#FCE9E9",
                  green="#15803D", green_bg="#E6F3EA", amber_solid="#B45309", coral_solid="#DC2626",
                  green_solid="#15803D"),
    "dark": dict(amber="#E8A34A", amber_bg="#3A2C12", coral="#F08A8A", coral_bg="#3A1818",
                 green="#6FD08C", green_bg="#16331F", amber_solid="#9A6310", coral_solid="#C23B3B",
                 green_solid="#1C7A40"),
}


def accent_block(hp, sp, hs, ss, mode):
    """primary (--indigo slot) + secondary (--teal slot) for one theme."""
    if mode == "light":
        return dict(
            indigo=hls_hex(hp, 0.47, max(sp, 0.55)), indigo_bg=hls_hex(hp, 0.93, 0.42),
            indigo_solid=solid(hp, sp, start_l=0.45),
            teal=hls_hex(hs, 0.40, max(ss, 0.5)), teal_bg=hls_hex(hs, 0.92, 0.40),
            teal_solid=solid(hs, ss, start_l=0.42),
        )
    return dict(
        indigo=hls_hex(hp, 0.72, min(max(sp, 0.5), 0.85)), indigo_bg=hls_hex(hp, 0.20, 0.45),
        indigo_solid=solid(hp, sp, start_l=0.42),
        teal=hls_hex(hs, 0.70, min(max(ss, 0.5), 0.82)), teal_bg=hls_hex(hs, 0.18, 0.45),
        teal_solid=solid(hs, ss, start_l=0.40),
    )


ORDER = [
    ("bg-primary", "bg_primary"), ("bg-secondary", "bg_secondary"), ("bg-card", "bg_card"),
    ("bg-code", "bg_code"), ("bg-nav", "bg_nav"),
    ("text-primary", "text_primary"), ("text-secondary", "text_secondary"), ("text-tertiary", "text_tertiary"),
    ("border-default", "border_default"), ("border-light", "border_light"),
    ("indigo", "indigo"), ("indigo-bg", "indigo_bg"), ("teal", "teal"), ("teal-bg", "teal_bg"),
    ("amber", "amber"), ("amber-bg", "amber_bg"), ("coral", "coral"), ("coral-bg", "coral_bg"),
    ("green", "green"), ("green-bg", "green_bg"),
    ("coral-solid", "coral_solid"), ("teal-solid", "teal_solid"), ("green-solid", "green_solid"),
    ("indigo-solid", "indigo_solid"), ("amber-solid", "amber_solid"),
]


def tokens(mode, neutral, hp, sp, hs, ss):
    t = {}
    t.update(NEUTRALS[neutral][mode])
    t.update(SEMANTIC[mode])
    t.update(accent_block(hp, sp, hs, ss, mode))
    return t


def render(tok, indent="  "):
    return "\n".join(f"{indent}--{css}:{tok[key]};" for css, key in ORDER)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("primary", help="primary accent hex, e.g. '#7C3AED'")
    ap.add_argument("--secondary", help="secondary accent hex (default: derived split-complement)")
    ap.add_argument("--neutral", choices=["warm", "cool"], default="warm")
    ap.add_argument("--name", default="custom", help="palette name for the themes.css form")
    ap.add_argument("--format", choices=["root", "themes"], default="root",
                    help="root = paste into a page; themes = [data-palette] block for themes.css")
    args = ap.parse_args()

    hp, _, sp = hex_hls(args.primary)
    if args.secondary:
        hs, _, ss = hex_hls(args.secondary)
    else:
        hs, ss = (hp + 0.42) % 1.0, max(sp, 0.5)  # split-complement

    light = tokens("light", args.neutral, hp, sp, hs, ss)
    dark = tokens("dark", args.neutral, hp, sp, hs, ss)

    # contrast report (stderr) — solids must clear ~4:1 for white text
    def rep(name, tk):
        return " ".join(f"{k}={contrast(tk[k], WHITE):.1f}:1"
                        for k in ("indigo_solid", "teal_solid", "green_solid", "coral_solid"))
    print(f"/* white-text contrast on solids — light: {rep('light', light)} */", file=sys.stderr)
    print(f"/* white-text contrast on solids — dark:  {rep('dark', dark)} */", file=sys.stderr)

    head = (f"/* post-to-visual palette '{args.name}' — primary {args.primary.upper()}"
            f"{' secondary ' + args.secondary.upper() if args.secondary else ''} · {args.neutral} neutrals\n"
            f"   generated by gen_palette.py · amber/coral/green kept as semantic anchors */")
    print(head)
    if args.format == "themes":
        print(f'[data-palette="{args.name}"]{{')
        print(render(light))
        print("}")
        print(f'[data-palette="{args.name}"][data-theme="dark"]{{')
        print(render(dark))
        print("}")
    else:
        print(":root{")
        print(render(light))
        print("}")
        print("@media (prefers-color-scheme: dark){ :root{")
        print(render(dark))
        print("}}")


if __name__ == "__main__":
    main()
