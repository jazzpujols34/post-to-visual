#!/usr/bin/env python3
"""
verify.py — mechanical pre-ship checks for a post-to-visual HTML page.

Turns the manual step-7 / step-8 eyeball pass into a pass/fail report so the
model spends attention on content, not bookkeeping. Pure standard library —
no deps, runs anywhere. Rendered checks (console errors) run only if a gstack
browse binary is found; otherwise they're skipped, never required.

Usage:
  python3 verify.py path/to/page.html [more.html ...]
  python3 verify.py --serve path/to/page.html   # also run headless console check if gstack is present
  python3 verify.py --json  path/to/page.html   # machine-readable result for AI agents / CI

Exit code: 0 if no FAILs, 1 if any FAIL. WARNs never fail the build.

What it catches (and why it exists):
  FAIL  unbalanced block tags ............ broken markup
  FAIL  nav href="#x" with no id="x" ..... dead in-page anchor
  FAIL  og:image / og:url not absolute ... blank social preview (the #1 OG mistake)
  FAIL  missing favicon .................. bare <head> looks fake when shared
  FAIL  <img src> file missing ........... broken image on the page
  FAIL  JPEG bytes in a .png file ........ LINE drops the OG image
  FAIL  duplicate SVG <marker> id ........ document-global ids silently break arrows
  WARN  ".nav a{" selector ............... matches a <nav> tag never -> blue underlined links
  WARN  white text on a non-*-solid fill . unreadable in dark mode (the contrast trap)
  WARN  <table> not wrapped in overflow .. clips on mobile
  WARN  diagram <svg> without min-width .. squishes instead of scrolling on mobile
"""

import os
import re
import sys
from pathlib import Path

# ---- tiny reporter ---------------------------------------------------------

C = {"FAIL": "\033[31m", "WARN": "\033[33m", "PASS": "\033[32m", "z": "\033[0m", "dim": "\033[2m"}
if not sys.stdout.isatty():
    C = {k: "" for k in C}


class Report:
    def __init__(self, name):
        self.name = name
        self.items = []  # (level, msg)

    def fail(self, msg): self.items.append(("FAIL", msg))
    def warn(self, msg): self.items.append(("WARN", msg))

    @property
    def fails(self): return sum(1 for lv, _ in self.items if lv == "FAIL")
    @property
    def warns(self): return sum(1 for lv, _ in self.items if lv == "WARN")

    def print(self):
        head = f"{C['dim']}── {self.name}{C['z']}"
        if not self.items:
            print(f"{head}  {C['PASS']}PASS{C['z']}  all checks clean")
            return
        print(head)
        for lv, msg in self.items:
            print(f"   {C[lv]}{lv}{C['z']}  {msg}")
        print(f"   {C['dim']}{self.fails} fail · {self.warns} warn{C['z']}")


# ---- helpers ---------------------------------------------------------------

VOID = {"img", "br", "hr", "meta", "link", "input", "rect", "circle", "line",
        "path", "polygon", "polyline", "ellipse", "use", "stop", "marker", "text",
        "tspan", "source", "col", "area", "base", "wbr", "track", "embed", "param"}


def strip_code(html: str) -> str:
    """Remove <pre>...</pre> and <code>...</code> bodies so doc samples don't
    register as real markup (e.g. an href="#id" shown inside a code block)."""
    html = re.sub(r"<pre\b[^>]*>.*?</pre>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<code\b[^>]*>.*?</code>", " ", html, flags=re.S | re.I)
    return html


def check_tag_balance(html, rep):
    for tag in ("div", "section", "figure", "nav", "table", "pre", "svg", "ul", "header"):
        opens = len(re.findall(rf"<{tag}[\s>]", html, re.I))
        closes = len(re.findall(rf"</{tag}>", html, re.I))
        if opens != closes:
            rep.fail(f"<{tag}> unbalanced: {opens} open vs {closes} close")


def check_nav_anchors(html, rep):
    code_free = strip_code(html)
    hrefs = set(re.findall(r'href="#([A-Za-z][\w-]*)"', code_free))
    ids = set(re.findall(r'\sid="([A-Za-z][\w-]*)"', html))
    missing = hrefs - ids
    for m in sorted(missing):
        rep.fail(f'nav/link href="#{m}" has no matching id')


def check_og(html, rep):
    head = html
    def content(prop, attr="property"):
        m = re.search(rf'<meta\s+{attr}="{re.escape(prop)}"\s+content="([^"]*)"', head, re.I)
        if not m:  # attribute order varies
            m = re.search(rf'<meta\s+content="([^"]*)"\s+{attr}="{re.escape(prop)}"', head, re.I)
        return m.group(1) if m else None

    for prop in ("og:image", "og:url"):
        val = content(prop)
        if val is None:
            rep.warn(f"missing {prop} meta")
        elif not val.startswith("https://"):
            rep.fail(f'{prop} is not absolute https:// -> blank social preview ("{val[:48]}")')
    tw = content("twitter:image", attr="name")
    if tw and not tw.startswith("https://"):
        rep.fail(f'twitter:image not absolute https:// ("{tw[:48]}")')


def check_favicon(html, rep):
    if not re.search(r'<link[^>]+rel="(?:icon|shortcut icon)"', html, re.I):
        rep.fail("no favicon <link rel=\"icon\"> in <head> (bare head looks fake when shared)")


def _is_jpeg(b): return b[:3] == b"\xff\xd8\xff"
def _is_png(b):  return b[:8] == b"\x89PNG\r\n\x1a\n"


def check_images(html, base: Path, rep):
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html, re.I):
        if src.startswith(("http://", "https://", "data:")):
            continue
        p = (base / src).resolve()
        if not p.exists():
            rep.fail(f"<img src> file missing: {src}")
            continue
        head = p.read_bytes()[:16]
        ext = p.suffix.lower()
        if ext == ".png" and _is_jpeg(head):
            rep.fail(f"JPEG bytes in a .png file ({src}) -> LINE drops the OG image; rename to .jpg")
        if ext in (".jpg", ".jpeg") and _is_png(head):
            rep.warn(f"PNG bytes in a .jpg file ({src}); rename to .png")


def check_marker_ids(html, rep):
    ids = re.findall(r'<marker\s+id="([^"]+)"', html, re.I)
    seen, dupes = set(), set()
    for i in ids:
        (dupes if i in seen else seen).add(i)
    for d in sorted(dupes):
        rep.fail(f'duplicate <marker id="{d}"> -> arrowheads silently break (ids are document-global)')


def check_nav_selector(html, rep):
    # The element is <nav> (a tag); a ".nav a" rule matches class="nav" and styles nothing.
    if re.search(r'\.nav\s+a\s*[:{]', html) and not re.search(r'(^|[^.])\bnav\s+a\s*\{', html):
        rep.warn('CSS uses ".nav a" but the element is <nav> -> links fall back to blue/underlined. Use "nav a".')


def check_dark_contrast(html, rep):
    """Heuristic for the dark-mode trap: a solid-filled box carrying white text.
    Accent vars flip *light* in dark mode, so fill="var(--green)" + fill="#fff"
    text = white-on-light. Filled boxes with white text must use a --*-solid token."""
    for m in re.finditer(r'<rect[^>]*fill="var\(--(green|teal|coral|indigo|amber)\)"[^>]*>', html, re.I):
        window = html[m.end():m.end() + 320]
        if re.search(r'fill="#fff"', window, re.I) or re.search(r'fill="#ffffff"', window, re.I):
            accent = m.group(1)
            rep.warn(f'rect fill="var(--{accent})" with white text nearby -> use var(--{accent}-solid) so dark mode stays readable')


def check_tables_and_svg(html, rep):
    # tables should sit in an overflow-x container
    for m in re.finditer(r'<table\b', html, re.I):
        before = html[max(0, m.start() - 220):m.start()]
        if "overflow-x" not in before and "tbl-wrap" not in before:
            rep.warn("a <table> may not be wrapped in an overflow-x:auto container (clips on mobile)")
            break
    # diagram svgs should declare a min-width so they scroll instead of squish
    for m in re.finditer(r'<svg\b[^>]*>', html, re.I):
        tag = m.group(0)
        if 'viewBox' in tag and 'min-width' not in tag and 'width="100%"' in tag:
            rep.warn("a full-width <svg> has no min-width -> squishes instead of scrolling on mobile")
            break


# ---- optional rendered check (only if gstack browse is present) ------------

def find_browse():
    # Optional headless-render check. Point P2V_BROWSE at any compatible
    # browse binary; otherwise fall back to a gstack install if present.
    cands = []
    env = os.environ.get("P2V_BROWSE")
    if env:
        cands.append(Path(env))
    cands += [
        Path.cwd() / ".claude/skills/gstack/browse/dist/browse",
        Path.home() / ".claude/skills/gstack/browse/dist/browse",
    ]
    for c in cands:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)
    return None


def rendered_console_check(path: Path, rep):
    import http.server, socketserver, subprocess, threading, functools
    browse = find_browse()
    if not browse:
        print(f"   {C['dim']}(rendered checks skipped — set P2V_BROWSE to a browse binary to enable){C['z']}")
        return
    root = path.parent
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        url = f"http://127.0.0.1:{port}/{path.name}"
        subprocess.run([browse, "goto", url], capture_output=True, timeout=30)
        out = subprocess.run([browse, "console", "--errors"], capture_output=True, text=True, timeout=20).stdout
        if "(no console errors)" not in out:
            errs = [l for l in out.splitlines() if l.strip() and "UNTRUSTED" not in l]
            if errs:
                rep.warn(f"console errors on render: {errs[:3]}")
    finally:
        httpd.shutdown()


# ---- main ------------------------------------------------------------------

def verify(path_str, do_render):
    path = Path(path_str).resolve()
    rep = Report(path.name)
    if not path.exists():
        rep.fail("file not found")
        return rep
    html = path.read_text(encoding="utf-8", errors="replace")
    check_tag_balance(html, rep)
    check_nav_anchors(html, rep)
    check_og(html, rep)
    check_favicon(html, rep)
    check_images(html, path.parent, rep)
    check_marker_ids(html, rep)
    check_nav_selector(html, rep)
    check_dark_contrast(html, rep)
    check_tables_and_svg(html, rep)
    if do_render:
        rendered_console_check(path, rep)
    return rep


def main():
    args = sys.argv[1:]
    do_render = "--serve" in args
    as_json = "--json" in args  # machine-readable output for AI agents / CI
    files = [a for a in args if not a.startswith("--")]
    if not files:
        print("usage: python3 verify.py [--serve] [--json] page.html [more.html ...]")
        sys.exit(2)
    reps = [verify(f, do_render) for f in files]
    total_fail = sum(r.fails for r in reps)
    total_warn = sum(r.warns for r in reps)

    if as_json:
        import json
        out = {
            "ok": total_fail == 0,
            "fail": total_fail, "warn": total_warn,
            "files": [{"file": r.name, "fail": r.fails, "warn": r.warns,
                       "items": [{"level": lv, "msg": m} for lv, m in r.items]} for r in reps],
        }
        print(json.dumps(out, indent=2))
        sys.exit(1 if total_fail else 0)

    for r in reps:
        r.print()
    print()
    verdict = f"{C['FAIL']}FAIL{C['z']}" if total_fail else (f"{C['WARN']}PASS (with warnings){C['z']}" if total_warn else f"{C['PASS']}PASS{C['z']}")
    print(f"{verdict}  {total_fail} fail · {total_warn} warn across {len(files)} file(s)")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
