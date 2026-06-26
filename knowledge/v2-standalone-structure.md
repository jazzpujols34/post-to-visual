# V2 Standalone HTML Reference Page

> How to build single-file HTML reference pages.
> These render standalone in a browser AND can be ported into a React app as JSX.

## When to reach for this

Default output format for non-trivial artifacts (see root `CLAUDE.md` → "Output Format Defaults"). Specifically:

- Specs, plans, research reports, explainers, dashboards
- Multi-option exploration (6 design directions in a grid)
- Code review writeups (rendered diffs + annotations)
- Design mockups & prototypes (with sliders/knobs and copy-export buttons)
- Custom one-off editors (drag/click UI + JSON export back to Claude Code)

Skip this format and use Markdown only for: short utility files (HANDOVER.md, CHANGELOG, READMEs), PR bodies, anything that must be reviewed line-by-line in git.

## Core idea

One self-contained HTML file. No external deps. Own CSS with light + dark mode. Two contexts:
1. **Standalone** — opened in browser, full page with nav
2. **Embedded in an app** — converted to JSX components, nav/header stripped, the parent app provides the theme

Design for standalone first. Every decision must survive the conversion into an app.

## Layout

- Container: `max-width: 1400px`, padding `32px 40px`
- Card grid: `repeat(2, 1fr)`, gap `20px`
- Below 900px: single column. Below 700px: tighter padding.
- **Card count rule:** Regular cards per section must be EVEN. Odd count = ugly gap in 2-col grid. Fix by promoting the orphan to `card-full`.

## Cards

| Class | Behavior |
|-------|----------|
| `.card` | Takes 1 grid column |
| `.card.card-full` | Spans both columns (`grid-column: 1 / -1`) |
| `.card.card-diagram` | Full-width, contains SVG, `overflow-x: auto` |

Each section: 1 diagram card (always first) + N content cards.

## CSS colors

Define BOTH light and dark themes. Required tokens:
- Accents (bg + text pairs): purple, teal, coral, blue, green, amber, red
- Base: `--bg-primary`, `--bg-secondary`, `--bg-card`, `--bg-code`, `--bg-nav`
- Text: `--text-primary`, `--text-secondary`, `--text-tertiary`
- Border: `--border-default`, `--border-light`

Standalone uses `prefers-color-scheme`. An embedding app typically uses a `data-theme` attribute on `<html>`.

If you add a new CSS variable in standalone, add it to the app's stylesheet too.

## SVG diagrams

```html
<svg width="100%" viewBox="0 0 920 H" xmlns="http://www.w3.org/2000/svg"
     style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
```

**Rules that prevent the most common failures:**

1. **Font-family must be inline** on `<svg>` — an embedding app won't inherit parent fonts
2. **All colors use CSS variables** — no hardcoded hex, or dark mode breaks
3. **Each diagram gets a unique arrow marker ID** (`a1`, `a2`, `a3`...) — IDs are document-global, duplicates silently break
4. **Never put label + description side-by-side on same line** — always stack as two lines (label bold, desc smaller below). Min rect height: 52px for two-line content
5. **Text must not touch edges** — right edge ≤ 900, left edge ≥ 20
6. **viewBox height** = lowest element's (y + height) + 20px. Calculate it, don't guess
7. **Min-width 700px** on diagram container so it scrolls on mobile

## Tables

Every `<table>` must be wrapped in `overflow-x: auto` container. Set `min-width: 480px` on the table.

## HTML → JSX conversion

- `class` → `className`
- Inline styles use camelCase (`max-width` → `maxWidth`)
- Copy card titles verbatim — don't paraphrase
- Keep card widths from source (full stays full, regular stays regular)
- SVG font-family stays inline
- Each diagram keeps its own `<defs>` with unique marker ID

## QA checklist

- [ ] Tag counts balanced (`<div>` == `</div>`, `<svg>` == `</svg>`)
- [ ] Nav links match section IDs
- [ ] Card count per section is even (regular cards only)
- [ ] All tables wrapped in scrollable container
- [ ] SVG: no text overlap, no text clipping, colors use variables
- [ ] Dark mode works both standalone and when embedded in an app
