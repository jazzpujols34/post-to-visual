# post-to-visual

Turn an article, post, or dense note into a **圖文好讀版** — a single-file, illustrated,
easy-to-read HTML page with editorial illustrations and themeable SVG data-viz. Built as a
[Claude Code](https://claude.com/claude-code) skill, but the scripts and asset library work
standalone.

It is **not** an HTML template. It's a pipeline (read → structure → visualize → assemble →
verify) plus a toolkit the model composes per post. The value is in the visual decisions,
not in a fixed layout.

> Works with **zero API keys**. Image generation (Gemini) is optional — see [SVG-only mode](#svg-only-mode).

---

## What you get

| File | What it does |
|------|--------------|
| `SKILL.md` | The pipeline, step by step (the skill's brain) |
| `scripts/cli.py` (`p2v`) | Standalone CLI: scaffold a page, generate a palette/images, verify, preview — no Claude Code needed |
| `scripts/gen_illustrations.py` | Editorial illustrations from a JSON spec (Gemini "nano banana") — optional |
| `scripts/gen_palette.py` | Build a contrast-safe light+dark palette from one accent hex |
| `scripts/verify.py` | Dependency-free pre-ship checker (tags, anchors, OG, contrast, image bytes…) |
| `assets/svg-recipes/recipes.html` | 8 themeable, light/dark-safe SVG diagram recipes + a "which chart when" guide |
| `assets/themes.css` + `themes.html` | 3 vetted light+dark palettes (editorial / pine / slate) with a live preview |
| `assets/components/components.html` | 6 optional vanilla-JS widgets (quiz, before/after, copy-as-prompt, tabs, glossary, jargon toggle) |
| `knowledge/` | Bundled writing + structure references (anti-AI prose, single-file HTML rules, image recipe) |
| `examples/` | A runnable, no-key sample you can reproduce |

Open `recipes.html`, `themes.html`, and `components.html` in a browser — each is a live gallery
with copy buttons and a light/dark toggle.

---

## Quickstart

### With Claude Code (intended use)
Drop this folder in your skills directory and ask: *"make this readable"*, *"turn this post
into a 圖文版"*, or *"visualize this article"* with a URL or pasted text. The skill runs the
pipeline in `SKILL.md`.

### Standalone — the `p2v` CLI (no Claude Code, no deps)
For people not using Claude Code: scaffold and check pages yourself, bring your own LLM (or
hand) for the prose.
```bash
alias p2v='python3 /path/to/post-to-visual/scripts/cli.py'
p2v new my-post --palette pine --title "My Post"   # starter page + spec + assets dir
p2v palette "#7C3AED" --secondary "#0D9488"         # contrast-safe light+dark tokens
p2v gallery recipes                                  # open a gallery in the browser
p2v verify my-post.html                              # pre-ship checks
p2v serve .                                          # preview over localhost
```
The scaffold from `p2v new` is a minimal valid shell (favicon + absolute OG + your chosen
palette, passes `verify`) — fill in the sections; it is deliberately not a rich template.

### Verify any HTML page (zero install)
```bash
python3 scripts/verify.py path/to/page.html
```
Reports `FAIL` / `WARN` for the bugs that actually ship: unbalanced tags, dead `#anchors`,
relative `og:image`/`og:url` (blank social previews), missing favicon, missing images,
JPEG-bytes-in-a-.png (breaks LINE), duplicate SVG marker ids, the `.nav a` selector trap, and
white-text-on-a-non-`--*-solid` fill (unreadable in dark mode). Exit 1 on any FAIL.

### Generate illustrations (optional, needs a Gemini key)
```bash
pip install google-genai python-dotenv
export GEMINI_API_KEY=...                 # or put it in a .env (see Config)
python3 scripts/gen_illustrations.py path/to/spec.json
```

---

## SVG-only mode

You do **not** need an image API. A post-to-visual page is fully valid — often better — with
zero AI images: carry it on the SVG recipes + strong typography + pull-quotes. Pure-prose
essays in particular look more intentional without stock-feel illustrations. Just skip the
image step and lean on `assets/svg-recipes/`. The `examples/` page is built this way, so you
can reproduce it with no key.

---

## Config

- **API key** (only for image gen): `GEMINI_API_KEY` in the environment, or `--env path/to/.env`,
  or a `.env` auto-discovered in the spec's folder / up to the repo root / `~/.config/post-to-visual/.env`.
- **Palette**: pick `editorial` / `pine` / `slate` from `assets/themes.css` — copy its LIGHT
  token block into the page's `:root{}` and the DARK block into the `prefers-color-scheme: dark`
  block. Token names are accent *slots*, so the recipes keep working; only the hues change. Or
  generate your own from one hex: `p2v palette "#7C3AED"` (solids auto-checked for white-text
  contrast in both themes).
- **Open Graph base URL**: OG tags must be absolute, so pages need your public base URL. The
  page goes at `<base>/<slug>`, assets at `<base>/<slug>-assets/images/<name>`. Set your own base.
- **Image provider**: `"provider"` in the spec or `--provider`. Only `gemini` ships today;
  there's a documented seam in `gen_illustrations.py` to add OpenAI / Flux / local.

---

## How the output is structured

Per `knowledge/v2-standalone-structure.md`: one self-contained HTML file, light + dark via
`prefers-color-scheme`, sticky nav whose links match section ids, a 2-column card grid, tables
wrapped to scroll on mobile, and a mandatory favicon + Open Graph in the `<head>`. Prose follows
`knowledge/anti-ai-writing.md` (be specific, kill significance-puffery and rule-of-three filler).

---

## Notes & attribution

- **Image generation calls a paid API** (Google Gemini, model `gemini-3.1-flash-image-preview`,
  a.k.a. "nano banana"). You bring your own key; you pay for what you generate. SVG-only is free.
- Nano banana garbles any text it tries to render — every image prompt says "no text"; all
  labels live in HTML/SVG. It returns **JPEG bytes**, so generated files are `.jpg`.
- Web fonts in the sample pages load from Google Fonts; swap or self-host as you like.
- **License: [MIT](./LICENSE).** The bundled `knowledge/` files are the author's working
  notes — fine to read and adapt; review before redistributing verbatim.
- The skill assumes [Claude Code](https://claude.com/claude-code) for the full pipeline; the
  `scripts/` and `assets/` are useful on their own.
