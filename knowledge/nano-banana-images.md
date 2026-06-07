# Knowledge: Nano Banana (Gemini) Editorial Illustrations

> How to generate clean editorial illustrations for HTML pages / posts / decks.
> Read before generating any non-gallery illustration. For Jazz-Gallery / Kotori
> art batches, use the `generate-gallery-art` skill instead (that one also handles
> GCS upload + Firestore queue).

## The env recipe (the part you forget)

- **Model:** `gemini-3.1-flash-image-preview` ("nano banana"). Never downgrade to 2.0.
- **Interpreter:** base anaconda does NOT have `google.genai`. Use a venv that does:
  `Jazz-Gallery/backend/venv/bin/python3` (verified working). Check with
  `<py> -c "import google.genai"`.
- **API key:** `GEMINI_API_KEY` lives in `Jazz-Gallery/scripts/.env`. The reusable
  script (`.claude/skills/post-to-visual/scripts/gen_illustrations.py`) auto-discovers it.
- **Call shape:** `client.models.generate_content_stream(model=..., contents=prompt,
  config=types.GenerateContentConfig(temperature=0.7, response_modalities=["IMAGE","TEXT"]))`,
  then read `chunk.parts[].inline_data.data` (PNG bytes). Wrap in a SIGALRM timeout
  (~150s) — it occasionally hangs.

## Prompt patterns that actually worked

These produced clean, on-brand results for the Software Factory page (2026-06):

1. **"Absolutely no text, no letters, no numbers, no labels anywhere in the image."**
   This is the single most important line. Nano banana garbles any text it tries to
   render. Convey meaning with icon-shapes (a pen, a magnifying glass, a shield, a
   rocket), not words.
2. **Pin the palette.** Give 3-5 named hexes + "flat editorial vector illustration,
   subtle paper grain, thin clean linework, generous negative space, no gradients,
   no glow." Repeat the palette block on every job so a multi-image set stays cohesive.
3. **State the aspect + composition in words** ("a wide 16:9 isometric illustration
   of ..."). There's no reliable aspect-ratio flag; describe it.
4. **Isometric + flat vector** reads as "editorial tech explainer" and matches the
   v2-standalone HTML look. Good default for concept/metaphor images.
5. **One scene per job.** For a before/after, ask for a single split-scene with a
   vertical divider ("LEFT HALF: ... RIGHT HALF: ...") rather than two images.
6. **Concept > literal.** "five-step ascending staircase, a lone human with hand
   tools at the bottom, progressively more robots and fewer humans climbing up" beats
   any literal diagram — and for literal data, use the `svg-diagram` skill instead.

## Division of labor: image vs SVG

- **Nano banana** → atmospheric / metaphor / hero illustrations. Not data, not text.
- **`svg-diagram` skill** → anything with labels, real numbers, matrices, flows.
  Crisp, themeable (light/dark via CSS vars), editable. The Software Factory page used
  AI images for the hero/metaphor and hand-built SVG for the level matrix and spectrum.

## Gotchas

- **Nano banana returns JPEG bytes, not PNG.** If you save them as `*.png`, the file is a JPEG-named-`.png`. Browsers tolerate it, but strict OG crawlers — **LINE especially** — try to decode it as PNG, fail, and drop the social-preview image (favicon shows, hero doesn't). `gen_illustrations.py` now derives the extension from `inline_data.mime_type` (→ `.jpg`), so reference `.jpg` in your HTML (`og:image`, `twitter:image`, `<img src>`). If you ever hand-save, run `file *.png` to check the real bytes. Fix for already-shipped pages: rename `hero.png`→`hero.jpg`, update the 3 refs; the OG URL still matches, CF then serves `image/jpeg`. On LINE, bust its cache by sharing with a `?v=2` suffix (no re-scrape tool there).
- Base anaconda python fails with `ModuleNotFoundError: google.genai`. Use the backend venv.
- Images come back as PNG bytes in a streamed chunk; if `chunk.parts is None`, skip it.
- Aspect ratio is a suggestion, not a guarantee. The model targets ~16:9 but crops
  vary; `object-fit:cover` on the `<img>` absorbs the difference.
- If text sneaks into an image anyway, regenerate — don't ship garbled glyphs.
- Browse/QA over `file://` is blocked by gstack-browse; serve with
  `python3 -m http.server` and hit `localhost` to screenshot-verify.
