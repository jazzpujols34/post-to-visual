# AGENTS.md

Guidance for AI coding agents (Claude Code, Cursor, and others) working in this repo. Humans:
read [`README.md`](README.md) first. This file follows the [agents.md](https://agents.md)
convention.

## What this repo is

A pipeline + toolkit that turns an article into a single self-contained, illustrated HTML page
(圖文好讀版). Not a template — you compose each page per its content. The full build procedure is
in [`SKILL.md`](SKILL.md); read it before building a page.

## Map

| Path | Use it to |
|------|-----------|
| `SKILL.md` | Follow the build pipeline (read → structure → visualize → assemble → verify) |
| `scripts/verify.py` | Check a page. **Run before you call any page done.** `--json` for parsing |
| `scripts/gen_palette.py` | Make a contrast-safe palette from one hex |
| `scripts/gen_illustrations.py` | Optional AI images (needs `GEMINI_API_KEY`) |
| `scripts/cli.py` | `p2v` — scaffold / palette / images / verify / gallery / serve |
| `assets/svg-recipes/recipes.html` | Copy a diagram pattern (read the file's source) |
| `assets/themes.css` | Palette token blocks to paste into a page |
| `assets/components/components.html` | Optional interactive widgets |
| `knowledge/*.md` | Writing rules + single-file-HTML structure rules |
| `examples/` | A correct reference build to imitate |

## Golden rules — do not break these

1. **Verify before done.** Run `python3 scripts/verify.py <page.html>` and fix every `FAIL`.
   Use `--json` if you're parsing the result. A page is not finished until it passes.
2. **`nav a`, never `.nav a`.** The element is a `<nav>` tag; a `.nav a` class rule styles
   nothing and nav links fall back to blue underlines.
3. **White-text boxes use a `--*-solid` token.** A solid `fill="var(--green)"` (etc.) with white
   text becomes unreadable in dark mode, because the plain accent flips light. Use
   `var(--green-solid)`. `verify.py` flags violations.
4. **Favicon + absolute Open Graph are mandatory.** `og:image` and `og:url` must be `https://…`.
   Relative paths → blank social preview.
5. **Don't templatize.** Re-decide structure per post. Pick image vs diagram vs prose per
   section. Pure-prose sections stay prose — not every section needs a visual.
6. **Gloss the jargon.** Expand every acronym at first use; add a glossary (名詞小抄) when the
   piece is jargon-dense. The audience may be non-specialists.
7. **SVG-only is first-class.** No image key, or a prose piece? Skip image generation and carry
   the page on `assets/svg-recipes/` + typography. Don't treat it as degraded.
8. **One self-contained HTML file.** Light + dark via `prefers-color-scheme`; sticky nav whose
   links match section `id`s; tables wrapped to scroll on mobile; even card count per row.

## Common tasks

- **Add a diagram** → open `assets/svg-recipes/recipes.html`, find the right pattern with its
  "which chart when" guide, copy the SVG, adapt the labels. Give each SVG its own marker `id`s.
- **New palette** → `python3 scripts/gen_palette.py "#7C3AED"` → paste the `:root` block and the
  `@media (prefers-color-scheme: dark)` block into the page.
- **AI images** → write a `<slug>.spec.json` (see `SKILL.md` step 2), run
  `python3 scripts/gen_illustrations.py <slug>.spec.json`, then open each image to confirm no
  garbled text. Reference the `.jpg` files (the model returns JPEG).
- **Start a page from scratch** → `python3 scripts/cli.py new <slug> --palette editorial`.

## Definition of done

- `verify.py` reports **0 FAIL**.
- The page was rendered and eyeballed in **both light and dark** (the checker can't judge
  composition — text collisions, crowding, whether the visual reads).
- Every acronym is glossed; the prose follows `knowledge/anti-ai-writing.md` (be specific; cut
  significance-puffery and rule-of-three filler).
