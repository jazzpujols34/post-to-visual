#!/usr/bin/env python3
"""
p2v — the post-to-visual command line.

A thin dispatcher over the toolkit so people without Claude Code can still use the
deterministic parts: scaffold a page, generate a palette, generate images, verify, and
preview the galleries. The *writing* (read → structure → prose) is yours (or any LLM);
this handles the mechanical scaffolding and checks.

  p2v new my-post --palette pine --title "My Post"   scaffold a starter page + spec + assets
  p2v palette "#7C3AED" --secondary "#0D9488"         generate a contrast-safe palette
  p2v images path/to/spec.json                        nano-banana illustrations (needs a key)
  p2v verify page.html [--serve]                       run the pre-ship checks
  p2v gallery recipes|themes|components                open a gallery in the browser
  p2v serve [dir]                                      preview over http://localhost

Pure standard library. Make it runnable: chmod +x cli.py, or call `python3 cli.py ...`.
Tip: alias p2v='python3 /path/to/post-to-visual/scripts/cli.py'
"""

import argparse
import http.server
import os
import re
import socketserver
import subprocess
import sys
import webbrowser
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
ASSETS = SKILL / "assets"


def _run(script, *args):
    return subprocess.call([sys.executable, str(SCRIPTS / script), *map(str, args)])


# ---- new: scaffold a starter page -----------------------------------------

def extract_palette(name):
    """Pull a palette's light + dark token bodies out of assets/themes.css."""
    css = (ASSETS / "themes.css").read_text(encoding="utf-8")
    light = re.search(r'\[data-palette="%s"\]\s*\{(.*?)\}' % re.escape(name), css, re.S)
    dark = re.search(r'\[data-palette="%s"\]\[data-theme="dark"\]\s*\{(.*?)\}' % re.escape(name), css, re.S)
    if not light or not dark:
        sys.exit(f"palette '{name}' not found in themes.css (have: editorial, pine, slate)")
    fix = lambda b: "\n".join("  " + ln.strip() for ln in b.strip().splitlines() if ln.strip())
    return fix(light.group(1)), fix(dark.group(1))


STARTER = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="TODO: 1-2 sentence summary.">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Crect%20width='24'%20height='24'%20rx='5'%20fill='%234F46E5'/%3E%3Cg%20stroke='%23fff'%20stroke-width='1.7'%20fill='none'%20stroke-linecap='round'%3E%3Cpath%20d='M5%2017V9'/%3E%3Cpath%20d='M11%2017V6'/%3E%3Cpath%20d='M17%2017v-5'/%3E%3C/g%3E%3C/svg%3E">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="TODO: same summary.">
<meta property="og:url" content="{base}/{slug}">
<meta property="og:image" content="{base}/og-default.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{base}/og-default.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{
{light}
  --shadow:0 1px 2px rgba(0,0,0,.04),0 6px 20px rgba(0,0,0,.05);
}}
@media (prefers-color-scheme: dark){{ :root{{
{dark}
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.4);
}}}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg-primary);color:var(--text-primary);line-height:1.8;font-size:16px;-webkit-font-smoothing:antialiased}}
nav{{position:sticky;top:0;z-index:50;background:var(--bg-nav);backdrop-filter:blur(12px);border-bottom:1px solid var(--border-default)}}
.nav-inner{{max-width:1080px;margin:0 auto;padding:12px 32px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.nav-brand{{font-weight:900;font-size:15px;margin-right:auto}}
nav a{{color:var(--text-secondary);text-decoration:none;font-size:13px;font-weight:500;padding:5px 11px;border-radius:7px}}
nav a:hover{{background:var(--bg-secondary);color:var(--text-primary)}}
nav a.nav-key{{color:var(--indigo);font-weight:700}}
.wrap{{max-width:1080px;margin:0 auto;padding:32px 32px 96px}}
section{{padding-top:46px;scroll-margin-top:72px}}
.sec-head{{display:flex;align-items:baseline;gap:14px;margin-bottom:8px}}
.sec-num{{font-family:'JetBrains Mono',monospace;font-size:clamp(22px,3vw,30px);color:var(--indigo);font-weight:700;letter-spacing:-.02em}}
h2{{font-size:clamp(24px,3.4vw,33px);font-weight:900;letter-spacing:-.02em;line-height:1.2}}
.sec-lead{{color:var(--text-secondary);font-size:16px;max-width:780px;margin:10px 0 24px}}
.hero{{padding:54px 0 14px}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);font-weight:500}}
h1{{font-size:clamp(34px,6vw,58px);font-weight:900;letter-spacing:-.03em;line-height:1.06;margin:14px 0 18px}}
h1 .hl{{color:var(--indigo)}}
.hero-sub{{font-size:clamp(17px,2.2vw,21px);color:var(--text-secondary);max-width:740px;line-height:1.6}}
.tldr{{background:var(--indigo-bg);border-radius:14px;padding:22px 26px;margin-top:28px}}
.tldr h3{{color:var(--indigo);font-size:18px;margin-bottom:6px}}
.tldr p{{font-size:16px;color:var(--text-primary)}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
.card{{background:var(--bg-card);border:1px solid var(--border-default);border-radius:14px;padding:22px;box-shadow:var(--shadow)}}
.card h3{{font-size:17px;font-weight:700;margin-bottom:6px}}
.card p{{color:var(--text-secondary);font-size:14.5px}}
.foot{{margin-top:60px;padding-top:24px;border-top:1px solid var(--border-default);font-size:13px;color:var(--text-tertiary);text-align:center}}
@media (max-width:880px){{ .grid{{grid-template-columns:1fr}} .wrap{{padding:24px 18px 72px}} .nav-inner{{padding:10px 16px}} nav a:not(.nav-key){{display:none}} }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <span class="nav-brand">{title}</span>
    <a href="#one" class="nav-key">Section one</a>
    <a href="#two">Section two</a>
  </div>
</nav>
<div class="wrap">
  <header class="hero">
    <div class="eyebrow">TODO eyebrow</div>
    <h1>{title}<br><span class="hl">TODO subtitle</span></h1>
    <p class="hero-sub">TODO: the hook. One or two sentences a non-specialist can follow.</p>
    <div class="tldr"><h3>TL;DR</h3><p>TODO: the one-paragraph takeaway.</p></div>
  </header>

  <!-- TODO: 4-8 sections. For each, decide image vs SVG-recipe vs prose.
       Diagrams: copy from assets/svg-recipes/recipes.html (which-chart-when guide).
       Gloss every acronym; add a 名詞小抄 if jargon-dense. -->
  <section id="one">
    <div class="sec-head"><span class="sec-num">01</span><h2>Section one</h2></div>
    <p class="sec-lead">TODO lead.</p>
    <div class="grid">
      <div class="card"><h3>Card A</h3><p>TODO.</p></div>
      <div class="card"><h3>Card B</h3><p>TODO.</p></div>
    </div>
  </section>

  <section id="two">
    <div class="sec-head"><span class="sec-num">02</span><h2>Section two</h2></div>
    <p class="sec-lead">TODO lead.</p>
    <div class="grid">
      <div class="card"><h3>Card C</h3><p>TODO.</p></div>
      <div class="card"><h3>Card D</h3><p>TODO.</p></div>
    </div>
  </section>

  <div class="foot">TODO: source attribution.</div>
</div>
</body>
</html>
"""

SPEC = """{{
  "out_dir": "{slug}-assets/images",
  "palette": "Limited flat palette: deep indigo (#4F46E5), teal (#0D9488), amber (#F59E0B), coral (#F87171), on off-white (#FAFAF8). Flat editorial vector, thin linework, generous negative space, no gradients. Absolutely no text, no letters, no numbers, no labels anywhere.",
  "jobs": {{
    "hero": "A wide 16:9 isometric illustration of TODO."
  }}
}}
"""


def cmd_new(args):
    slug = args.slug
    out = Path(args.dir).resolve()
    page = out / f"{slug}.html"
    if page.exists() and not args.force:
        sys.exit(f"{page} exists (use --force to overwrite)")
    light, dark = extract_palette(args.palette)
    title = args.title or slug.replace("-", " ").title()
    page.write_text(STARTER.format(lang=args.lang, title=title, slug=slug, base=args.base_url,
                                   light=light, dark=dark), encoding="utf-8")
    (out / f"{slug}.spec.json").write_text(SPEC.format(slug=slug), encoding="utf-8")
    (out / f"{slug}-assets" / "images").mkdir(parents=True, exist_ok=True)
    print(f"scaffolded:\n  {page}\n  {out / (slug + '.spec.json')}\n  {out / (slug + '-assets/images')}/")
    print(f"palette: {args.palette} · next: fill the TODOs, then  p2v verify {page.name}")
    if args.serve:
        serve_dir(out, open_path=page.name)


# ---- gallery / serve -------------------------------------------------------

GALLERIES = {
    "recipes": ASSETS / "svg-recipes/recipes.html",
    "themes": ASSETS / "themes.html",
    "components": ASSETS / "components/components.html",
}


def serve_dir(directory: Path, open_path=None, port=0):
    import functools
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        p = httpd.server_address[1]
        url = f"http://127.0.0.1:{p}/" + (open_path or "")
        print(f"serving {directory} at {url}  (Ctrl-C to stop)")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


def cmd_gallery(args):
    g = GALLERIES.get(args.which)
    if not g or not g.exists():
        sys.exit(f"unknown gallery '{args.which}' (recipes | themes | components)")
    serve_dir(g.parent, open_path=g.name)


def cmd_serve(args):
    target = Path(args.path).resolve()
    if target.is_file():
        serve_dir(target.parent, open_path=target.name)
    else:
        serve_dir(target)


# ---- main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(prog="p2v", description="post-to-visual command line")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="scaffold a starter page + spec + assets dir")
    n.add_argument("slug")
    n.add_argument("--title")
    n.add_argument("--palette", default="editorial", choices=["editorial", "pine", "slate"])
    n.add_argument("--lang", default="en")
    n.add_argument("--base-url", default="https://example.com", help="public base for absolute OG urls")
    n.add_argument("--dir", default=".")
    n.add_argument("--serve", action="store_true", help="preview right after scaffolding")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)

    g = sub.add_parser("gallery", help="open a gallery in the browser")
    g.add_argument("which", choices=["recipes", "themes", "components"])
    g.set_defaults(fn=cmd_gallery)

    s = sub.add_parser("serve", help="serve a file or dir over http for preview")
    s.add_argument("path", nargs="?", default=".")
    s.set_defaults(fn=cmd_serve)

    # pass-throughs to the sibling scripts
    sub.add_parser("palette", help="generate a palette (see gen_palette.py -h)", add_help=False)
    sub.add_parser("images", help="generate illustrations (see gen_illustrations.py -h)", add_help=False)
    sub.add_parser("verify", help="run pre-ship checks (see verify.py -h)", add_help=False)

    # split argv so pass-throughs forward their own flags untouched
    argv = sys.argv[1:]
    if argv and argv[0] in ("palette", "images", "verify"):
        script = {"palette": "gen_palette.py", "images": "gen_illustrations.py", "verify": "verify.py"}[argv[0]]
        sys.exit(_run(script, *argv[1:]))

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
