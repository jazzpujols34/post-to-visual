---
name: post-to-visual
description: Turn an article, post, or long note into a 圖文好讀版 — a single-file, illustrated, easy-to-read HTML page with AI-generated editorial illustrations and SVG data-viz, optionally translated to 繁體中文. Use when the user wants to "make this readable", "turn this post into a nice page", "圖文版", "visualize this article", or share a writeup with a team. NOT for slide decks (use frontend-slides) or standalone images (use generate-gallery-art).
---

# Skill: Post → Visual (圖文好讀版)

> Orchestration checklist, not a template. The skill is the order you combine things in:
> the nano-banana image recipe, a themeable SVG recipe library, optional interactive widgets,
> a static verifier, and the bundled writing/structure knowledge — see "What ships" below.

## When to use

User has a post / article / dense note and wants a pretty, navigable HTML version to
re-read or share. Output is one self-contained HTML file + an `assets/images/` folder.

## What this skill is (and isn't)

- It **is** the pipeline order + the nano-banana recipe + a toolkit.
- It is **not** an HTML template. Per root CLAUDE.md: don't templatize HTML, decide what
  the artifact does and prompt for it. Structure each post on its own merits.

## What ships with the skill

- `scripts/gen_illustrations.py` — nano-banana (Gemini) editorial illustrations from a JSON spec (step 2).
- `assets/svg-recipes/recipes.html` — living catalog of 8 themeable, light/dark-safe SVG diagram
  recipes + a "which chart when" guide (step 3). Open it, copy a pattern, adapt.
- `assets/themes.css` + `assets/themes.html` — 3 vetted light+dark palettes (editorial / pine / slate),
  each pre-checked for the `--*-solid` white-text rule. Preview + switch in `themes.html` (step 4).
- `assets/components/components.html` — 6 optional, self-contained vanilla-JS widgets (self-assessment,
  before/after slider, copy-as-prompt, tabs, expandable glossary, jargon↔白話 toggle). Earn it, don't
  default to it (step 4). Copy = standalone block.
- `scripts/verify.py` — dependency-free static checker that catches the recurring ship bugs (step 7).
- `scripts/gen_palette.py` — build a contrast-safe light+dark palette from one accent hex
  (`p2v palette "#7C3AED"`); solids auto-darkened until white text clears 4:1.
- `scripts/cli.py` (`p2v`) — standalone CLI (new / palette / images / verify / gallery / serve)
  so non-Claude-Code users can scaffold + check pages. `README.md` has the quickstart; `LICENSE` is MIT.
- `knowledge/{nano-banana-images,v2-standalone-structure,anti-ai-writing}.md` — bundled so the
  skill is self-contained. In this monorepo they mirror `.claude/knowledge/`; if you edit the
  originals there, re-copy them here.
- `README.md` — quickstart + config. `examples/` — a runnable, no-API-key sample.

## The pipeline

### 1. Read + structure
Read the source. Break it into 4-8 sections. For each section decide: what's the ONE
visual that makes it click — a metaphor image, a data diagram, or a number tile? Most
sections need a diagram, not an image. Sections that are pure prose stay prose.

### 1.4 Source intake — can you actually retrieve it?
Before anything, decide how the source comes in:
- **Publicly retrievable** (TrendForce Substack, most blogs) → WebFetch the text + browse for
  figures (step 1.5).
- **Not retrievable** (paywalled, login-walled, or an X/Twitter article Claude can't open) →
  **don't guess from the URL.** Ask Jazz for a local file: he pastes the full article into an
  `.md` and attaches the images alongside it. Then the source of record IS that local md +
  its images — read those for both the text and the figure pass. (This is the standard path
  for X posts: Jazz copies the whole thread/article into md so it can be made visual.)

### 1.5 Read the source's own images — WebFetch is text-only
WebFetch converts the page to markdown and never *sees* images; charts, comparison
tables-rendered-as-images, and architecture diagrams are invisible to it. After the text
fetch, do an **image pass**: browse the live page (gstack-browse), **scroll to trigger
lazy-loaded images**, list every `<img>` with `naturalWidth >= ~300`, then screenshot +
Read the data-bearing ones (charts, tables, diagrams). Skip logos / avatars / hero photos.
Substack-CDN images 403 on bare `curl` — screenshot the rendered element instead
(`$B screenshot "#id"` after tagging via JS). Capture any number or relationship that
exists *only* in a figure into the provenance post before building. (Non-retrievable source?
Read the local md + attached images from step 1.4 instead of browsing.)

### 1.6 Web-search anything newer than your training
A post-to-visual source is often *news* — a just-announced product, a recent event, fresh
specs (e.g. a COMPUTEX-2026 part like BlueField-4 STX / HBM5 / AIM 3.0). The model was never
trained on those, so explaining them from memory = confident hallucination. **Before writing
the plain-language explanation of any term, product, or event that may post-date training,
web-search it** and base the gloss on what you find. Most fundamentals (what HBM is, what TSV
is) are already known and fine to explain directly — search the *novel* specifics, not the
textbook basics. When a fact can't be confirmed by search, say so rather than invent it.

### 2. Generate illustrations (the captured part) — OPTIONAL
For metaphor / hero / atmospheric visuals, generate with nano banana.
**Read `knowledge/nano-banana-images.md` first** — it has the env recipe (which
venv, model name, key location) and the prompt patterns (fixed palette, "no text"
constraint, isometric flat vector, one-scene-per-job).

**No key / no image budget? Run SVG-only — this is a first-class mode, not a degraded one.**
A post-to-visual page is fully valid with zero AI images: carry it on the `assets/svg-recipes`
diagrams + strong typography + pull-quotes. Pure-prose essays often look *better* without
stock-feel illustrations. Just skip this step and lean on step 3.

**The key is configurable** (no longer pinned to one machine): `gen_illustrations.py` reads
`GEMINI_API_KEY` from the env, or `--env path/to/.env`, or auto-discovers a `.env` in the
spec's folder / up to the repo root / `~/.config/post-to-visual/.env`. No key → it exits with
the SVG-only instructions above. Provider is pluggable (`"provider"` in the spec or `--provider`);
only `gemini` ships today, with a documented seam to add OpenAI/Flux/local later.

Write a JSON spec and run the reusable script (any Python with `google-genai` +
`python-dotenv`; on the author's machine that's `Jazz-Gallery/backend/venv/bin/python3`):
```bash
python3 scripts/gen_illustrations.py path/to/<slug>.spec.json
```
Spec shape (`jobs` = name → prompt; `palette` is appended to every job; `out_dir` is
relative to the spec file):
```json
{
  "out_dir": "<slug>-assets/images",
  "palette": "Limited flat palette: deep indigo (#4F46E5), teal (#0D9488), amber (#F59E0B), coral (#F87171), on off-white (#FAFAF8). Flat editorial vector, thin linework, generous negative space, no gradients. Absolutely no text, no letters, no numbers, no labels anywhere.",
  "jobs": { "hero": "A wide 16:9 isometric illustration of ...", "metaphor": "A split-scene ..." }
}
```
Generate to background if >2 images; build HTML while it runs. **View each PNG after**
(Read tool) to confirm no garbled text — regenerate if any slipped in.

### 3. Diagrams (data, labels, flows)
Anything with real numbers, labels, matrices, or flows → a themeable SVG, not an AI image.
**Start from `assets/svg-recipes/recipes.html`** — a living catalog of 8 vetted patterns,
each already light/dark-safe (CSS-var fills, `--*-solid` tokens for white-text boxes), with
the layout math baked in (unique marker ids, two-line labels, computed viewBox, `min-width`).

Pick with the "which chart when" guide at the top of that file:
- **numbers/data** → `tiles` (one/few hero stats) · `bar` (compare by length)
- **a sequence** → `flow` (linear steps) · `ladder` (levels that build on each other)
- **a trade-off / contrast** → `matrix-2x2` (two axes) · `branch` (one start → two outcomes) ·
  `panels` (N options side by side)
- **N inputs → one result** → `converge`
- **a pure idea, no data** → no chart; use a pull-quote + typography

Copy the recipe's SVG and adapt it — it's a recipe set, **not a template engine** (still
compose per post). For anything outside the 8, the `svg-diagram` skill has the raw layout
math. Open `recipes.html` and toggle its theme to confirm a diagram reads in BOTH modes
before shipping (catches the dark-mode contrast trap early).

### 4. Assemble the HTML page
**Follow `knowledge/v2-standalone-structure.md`**: single file, light+dark themes
via `prefers-color-scheme`, sticky nav whose links match section IDs, 2-col card grid
(even card count per section), tables wrapped in `overflow-x:auto`. Web fonts (Noto Sans
TC + a mono) are fine for a shareable page; keep a system fallback.
**Pick a palette from `assets/themes.css`** (editorial / pine / slate) — copy its LIGHT block
into `:root{}` and its DARK block into the `prefers-color-scheme: dark` block. The token names
are accent slots, so the svg-recipes keep working; only the hues change. Default to `editorial`
unless the piece wants a different feel. (`nav a`, not `.nav a` — verify.py lints this.)
Add interactivity where it earns its keep (e.g. a self-assessment quiz) — vanilla JS, no deps.

### 5. Head: favicon + Open Graph (never skip — a bare `<head>` looks fake)
Every page gets a favicon and social-share meta. Both go in `<head>`, right after `<title>`.

**Favicon — inline SVG data-URI** (self-contained, travels with the file; reuse the
article's nav-brand glyph on a rounded accent square):
```html
<link rel="icon" href="data:image/svg+xml,%3Csvg.../%3E">
```
URL-encode the SVG (`#`→`%23`, spaces→`%20`, `<`→`%3C`, `>`→`%3E`). Don't link to the
host site's `/favicon.svg` — that breaks when the file is opened off-domain.

**Open Graph + Twitter — point `og:image` at the first raster image of the page:**
```html
<meta name="description" content="<1-2 sentence summary>">
<meta property="og:type" content="article">
<meta property="og:title" content="<title>">
<meta property="og:description" content="<same summary>">
<meta property="og:url" content="<ABSOLUTE page url>">
<meta property="og:image" content="<ABSOLUTE url of first raster image>">
<meta property="og:image:width" content="<W>"><meta property="og:image:height" content="<H>">
<meta property="og:image:alt" content="<alt>">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="<same ABSOLUTE image url>">
```
Rules that make it actually work:
- **`og:image` and `og:url` MUST be absolute** (`https://…`). Crawlers (FB/LinkedIn/Slack/X)
  ignore relative paths → blank preview. Ask the user for their public base URL; build the
  URLs as `<base>/<slug>` for the page and `<base>/<slug>-assets/images/<name>` for assets.
  (Author's convention: base = `https://jazzlien.com/learn-files`.)
- **First _raster_ image**, not the first visual. An inline SVG diagram can't be an OG
  image. If the page leads with SVG and has no `<img>`, fall back to a site-default OG image.
- Set explicit `og:image:width/height` (read with `sips -g pixelWidth -g pixelHeight`) so
  previews render without the crawler fetching the file. Nano-banana heroes are ~1376×768,
  close enough to the ideal 1200×630 (platforms center-crop).

### 6. Translate (if requested)
Default English. If Jazz asks for 中文, write 繁體中文 and **read
`knowledge/anti-ai-writing.md` first** — no 三段排比, no 重要性膨脹, no AI vocab
clusters. Technical terms stay in English with Chinese parentheticals.

### 7. Verify
**First run the static checker — it catches the recurring bugs mechanically:**
```bash
python3 .claude/skills/post-to-visual/scripts/verify.py path/to/page.html
```
It checks tag balance, nav `href="#id"`→`id` resolution (ignoring code samples), absolute
`og:image`/`og:url`, favicon present, every `<img>` exists + extension matches real bytes
(the JPEG-named-.png / LINE trap), duplicate SVG marker ids, the `.nav a` selector bug, and
the white-text-on-non-`*-solid` dark-mode contrast trap. Exit 1 on any FAIL; WARNs never
block. Pure stdlib — runs anywhere. (`--serve` also runs a headless console-error check if a
gstack browse binary is present.) **Fix every FAIL before continuing.**

Then the eyeball pass: serve over HTTP (`python3 -m http.server`, then `localhost/...`) —
`file://` is blocked by gstack-browse. Screenshot the hero, each SVG, and any interactive
widget, in light AND forced-dark. The checker can't judge composition (text collisions,
crowding, whether the metaphor reads) — you still look.

### 8. Coverage + comprehension review (content gate)
Step 7 proves the page *renders*; step 8 proves it does its job. The page has two jobs and
both must pass: **capture everything the source says**, and **make it understandable to a
non-specialist**. Jazz reads these to build real tech judgment (he invests on it), so a
sentence he can't follow is a failure, not a nitpick. Follow root CLAUDE.md **"Review
discipline"**: ENUMERATE FIRST, check EACH, never "the main points".

**A. Completeness — did we drop anything from the source?**
1. Build the checklist from BOTH inputs — the text fetch AND the step-1.5 figure pass.
   Figure-only facts (rankings, spec tables, numbers that live only in a chart) are the
   easiest to silently drop, so they MUST be on the list. Use the provenance post as record.
2. Enumerate every checkable item — each company, product/model number, spec/number, named
   technology, named relationship, section. State the total: "N items to verify."
3. Mark each `COVERED` / `PARTIAL` / `MISSING` against the built HTML. No skipping. Add back
   every `MISSING`/`PARTIAL`, or note in one line why it's deliberately out of scope.

**B. Comprehension — can a non-specialist actually follow it?**
4. Walk every acronym / jargon term on the page. Each must be glossed in plain 白話 at first
   use (one parenthetical) AND appear in the 名詞小抄 glossary if the piece is jargon-dense.
   A naked acronym (TSV, D2D PHY, KV cache, TOPS…) is a dead end for a lay reader — expand it.
5. Re-read each section as if you don't work in semiconductors. Any sentence that needs prior
   domain knowledge to parse → add a plain-language line or analogy. **More explanation is the
   point; richer is better.** For any term/product/event that may be newer than training,
   **web-search it before writing the gloss** (step 1.6) — don't explain a just-announced part
   from memory.

**Accuracy note:** adding explanation and examples beyond the source is encouraged — that's
the whole value. The only rule on additions: any *fact* you add (a spec, a number) must be
correct, not invented. A wrong number is worse than a missing one — it poisons the learning.
If unsure, verify or leave it out. (No provenance-tagging needed — we don't care whether a
line came from the post, only that it's right and it helps Jazz understand.)

**Report.** Findings = (`MISSING` + `PARTIAL`) + (un-glossed terms) + (sentences a layperson
can't follow). Fix them all, then restate the final counts. "Looks thorough" is not a result.

## Reference implementation

`Reference-post/alex-lieberman-30-days-of-ai/pages/day1-software-factory.html` (+ its
`day1-software-factory-assets/`) — Alex Lieberman's "Software Factory" post turned into a
繁中 圖文好讀版 (hero + metaphor + ladder illustrations from nano banana; level-matrix +
climb + readiness-spectrum as SVG; interactive 5-question self-assessment; favicon + OG).
`day1-software-factory-assets/gen_images.py` is the original per-job script the reusable
`scripts/gen_illustrations.py` was generalized from. Series index + folder convention:
`Reference-post/alex-lieberman-30-days-of-ai/README.md` (posts/ + pages/, `dayN-<slug>` prefix).

## Gotchas

- Image gen needs `google-genai` + `python-dotenv` (`pip install google-genai python-dotenv`).
  On the author's machine base anaconda lacks them — use `Jazz-Gallery/backend/venv/bin/python3`.
- Nano banana garbles text — every image prompt MUST say "no text, no letters". Put
  labels in HTML/SVG, never in the image.
- Nano banana returns **JPEG bytes** — files come out `.jpg` (the script derives the
  extension from mime). Reference `.jpg` in `og:image`/`twitter:image`/`<img>`. A
  JPEG-named-`.png` makes **LINE drop the OG image**. Verify with `file <img>` if unsure.
- Don't reach for an AI image when the content is data. Diagram it (svg-diagram skill).
- Don't templatize the HTML. Re-structure per post; the value is in the visual decisions.
- Odd card count in a 2-col grid leaves an ugly gap — promote the orphan to `card-full`.
- `prefers-color-scheme` dark must define every accent token, or dark mode breaks.
- **Solid-fill SVG boxes with white text need a dedicated `*-solid` token.** Normal accent vars
  flip *light* in dark mode (`--green` #15803D → #6FD08C), so a `fill="var(--green)"` rect with
  white text becomes white-on-light = unreadable. Add `--coral-solid/--teal-solid/--green-solid`
  that stay dark enough for white text in BOTH themes, and use those on filled outcome/result
  boxes. Tinted nodes (`*-bg` fill + accent text) are fine — only solid-fill-plus-white-text
  breaks. Caught on the Figma "what-matters-when-anyone-can-build" essay (triad + branching SVGs);
  the light-mode screenshot looked perfect, only the forced-dark screenshot exposed it.
- **Nav links: style with `nav a`, NOT `.nav a`.** The element is `<nav>` (a tag), so a
  `.nav a` rule (class selector) matches nothing — links silently fall back to browser-default
  blue-underlined and the nav looks broken. This bug rode along from the day1 reference because
  the live KM/React build strips the standalone nav, so it never showed on jazzlien.com — but it
  IS visible whenever you open the standalone file (which is exactly how Jazz reviews). Use the
  bare tag selector. Same applies to the `:not(.nav-key)` mobile-collapse rule.
- **`.sec-num` ("01") must scale with the `h2`.** At a fixed 13px next to a 34px heading it reads
  like a stray subscript. Use `clamp(22px,3vw,30px)` + weight 700 so it sits as a real companion
  on the shared baseline (`.sec-head` is `align-items:baseline`).
- A page with no favicon / no OG looks unfinished and fake when shared. Step 5 is mandatory.
- **Gloss the jargon — Jazz's audience includes non-programmers.** Define every industry acronym
  at first use (one parenthetical) and add a compact 名詞小抄 glossary card for jargon-dense pieces
  (TSV, D2D PHY, TOPS, Fluxless, KV cache…). A naked acronym is a dead end for a lay reader. For
  tech-explainers: NO investment-disclaimer boilerplate (非投資建議／未獨立查證／DYOR) from
  computex-2026-memory onward — keep source attribution only; the hedging clutters an educational page.
- Relative `og:image` = blank social preview. Always absolute. This is the #1 OG mistake.
- **Pretty ≠ complete — run the coverage review (step 8).** The technical verify passes while
  whole figures are still missing. Two goals: capture everything from the source, and gloss
  every jargon term so a non-specialist follows it. On computex-2026-memory an
  enumerate-and-check audit caught real drops the text-only fetch never surfaced — the event
  dates (Jun 2–5) and Syntronix's WoW camera-module demo. Adding explanation/examples beyond
  the source is good (that's the point); just keep any added *fact* correct, not invented.
- **Don't explain new things from memory — web-search them.** These posts are usually news, so
  the headline products/specs/events are post-training-cutoff. Glossing a just-announced part
  from "knowledge" produces confident wrong explanations. Search the novel specifics (the basics
  like "what is HBM" are fine direct). If search can't confirm it, say so — never invent.
- **Source not retrievable? Get the local md, don't guess.** Paywalled / login-walled / X
  articles Claude can't open → Jazz pastes the full text into an `.md` with images attached;
  that file becomes the source of record for both the text and figure pass. Standard path for
  X posts.
- **WebFetch can't read figures.** It's text-only — charts / diagrams / tables-as-images are
  invisible. Always run the image pass (step 1.5). On the TrendForce inference-chip piece the
  text alone missed a 6-chip tokens/sec ranking, a Digital/Analog/Hybrid CIM taxonomy, and a
  full spec-comparison table — every one of them figure-only. Skipping the pass = silently
  dropping the article's hardest data.
- **`spec.json` must NOT live inside `*-assets/`.** Deploy does `cp -R <slug>-assets`, so a
  spec dropped in there ships your nano-banana prompts to prod (deploy agent caught + stripped
  it on Day 3/4). Store it one level up as `pages/<slug>.spec.json` with
  `"out_dir": "<slug>-assets/images"` — only `images/` should ride along to the live site.
- **Name the local asset folder with the live slug only — `<slug>-assets/`, NO `dayN-`
  prefix.** The page file/post keep the `dayN-` prefix (ordering), but the assets folder must
  match the live + OG path exactly so the in-page `<img src>`, the OG tags, and the deployed
  path all agree and the deploy step needs zero rename work. (Pre-2026-06 pages were
  day-prefixed and got renamed on deploy; Day 3/4 onward are slug-only at the source.)
