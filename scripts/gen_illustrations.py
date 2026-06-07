#!/usr/bin/env python3
"""
Generate editorial illustrations via Gemini (nano banana) from a JSON spec.

Reusable across any post-to-visual job. You write the spec, this handles the
env-loading, streaming, timeout, and file-writing boilerplate.

Spec file (JSON):
{
  "out_dir": "path/to/images",        # optional; defaults to ./images next to spec
  "palette": "Limited flat palette ... no text, no letters.",  # appended to every prompt
  "temperature": 0.7,                  # optional
  "jobs": {
    "hero": "A wide 16:9 isometric illustration of ...",
    "diptych": "A split-scene ..."
  }
}

Run with an interpreter that has google-genai installed. On Jazz's machine:
  Jazz-Gallery/backend/venv/bin/python3 gen_illustrations.py spec.json

GEMINI_API_KEY is read from the environment, or from --env <file>, or auto-discovered
from common .env locations (see ENV_CANDIDATES below).
"""

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit(
        "Missing deps. Use a Python with google-genai + python-dotenv installed:\n"
        "  pip install google-genai python-dotenv\n"
        "  (on the author's machine: Jazz-Gallery/backend/venv/bin/python3)"
    )

MODEL = os.environ.get("NANO_BANANA_MODEL", "gemini-3.1-flash-image-preview")  # do NOT downgrade to 2.0
TIMEOUT_S = 150


def env_candidates(spec_path: Path) -> list[Path]:
    """Where to look for the API key's .env, in priority order. Portable: searches
    the spec's own folder and up to 4 parents (repo root), the cwd, and a user config
    dir — so it works on any machine, not just the author's. The legacy author path
    stays last as a harmless fallback."""
    cands: list[Path] = []
    d = spec_path.parent.resolve()
    for _ in range(5):
        cands.append(d / ".env")
        if d.parent == d:
            break
        d = d.parent
    cands.append(Path.cwd() / ".env")
    cands.append(Path.home() / ".config/post-to-visual/.env")
    # legacy author location (ignored if absent on other machines)
    cands.append(Path.home() / "Desktop/jazz/0_GitHub/Repositories/17_ultimate_Claude/Jazz-Gallery/scripts/.env")
    return cands


def load_key(env_arg: str | None, spec_path: Path) -> str:
    """Resolve the image-provider key. Order: existing env var, --env file, then the
    discovered .env candidates. No key -> exit with the SVG-only fallback explained."""
    if env_arg:
        load_dotenv(env_arg)
    if not os.environ.get("GEMINI_API_KEY"):
        for cand in env_candidates(spec_path):
            if cand.exists():
                load_dotenv(cand)
                if os.environ.get("GEMINI_API_KEY"):
                    break
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit(
            "No GEMINI_API_KEY found.\n"
            "  Set it:   export GEMINI_API_KEY=...   (or pass --env path/to/.env)\n"
            "  No key?   Skip image generation and run SVG-ONLY: carry the page on the\n"
            "            assets/svg-recipes diagrams + strong typography. A post-to-visual\n"
            "            page is fully valid with zero AI images — see SKILL.md step 2."
        )
    return key


def _timeout(signum, frame):
    raise TimeoutError("timed out")


def generate(client, name: str, prompt: str, out_dir: Path, temperature: float) -> bool:
    print(f"[{name}] generating...", flush=True)
    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(TIMEOUT_S)
    try:
        for chunk in client.models.generate_content_stream(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_modalities=["IMAGE", "TEXT"],
            ),
        ):
            if chunk.parts is None:
                continue
            for part in chunk.parts:
                if part.inline_data and part.inline_data.data:
                    # Extension MUST match the real bytes. Nano banana returns JPEG,
                    # so a hardcoded ".png" produces a JPEG-named-.png that strict
                    # crawlers (LINE!) refuse to decode as an OG image. Derive from mime.
                    mime = (part.inline_data.mime_type or "").lower()
                    ext = "jpg" if "jpeg" in mime or "jpg" in mime else ("png" if "png" in mime else "jpg")
                    fp = out_dir / f"{name}.{ext}"
                    fp.write_bytes(part.inline_data.data)
                    print(f"[{name}] OK ({len(part.inline_data.data)//1024}KB, {mime or '?'}) -> {fp}", flush=True)
                    raise StopIteration
    except StopIteration:
        return True
    except Exception as e:  # noqa: BLE001 - report and continue to next job
        print(f"[{name}] FAILED: {e}", flush=True)
        return False
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    print(f"[{name}] no image returned", flush=True)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="path to JSON spec")
    ap.add_argument("--env", help="path to a .env file holding the provider key")
    ap.add_argument("--provider", help="image provider (default: spec 'provider' or 'gemini')")
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())
    jobs = spec.get("jobs") or {}
    if not jobs:
        sys.exit("spec has no 'jobs'")

    # Provider seam. Only gemini ships today; to add one (OpenAI, Flux, local), implement
    # a generate(client, name, prompt, out_dir, temperature)->bool and register it here.
    provider = (args.provider or spec.get("provider") or "gemini").lower()
    if provider != "gemini":
        sys.exit(f"provider '{provider}' not implemented — only 'gemini' ships today. "
                 "Add an adapter in gen_illustrations.py, or run SVG-only (no images).")

    palette = spec.get("palette", "")
    temperature = float(spec.get("temperature", 0.7))
    # Resolve out_dir relative to the SPEC FILE (not the shell CWD), so running
    # the script from anywhere lands images next to the spec as intended.
    out_spec = spec.get("out_dir")
    out_dir = (spec_path.parent / out_spec) if out_spec else (spec_path.parent / "images")
    out_dir.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=load_key(args.env, spec_path))

    ok = 0
    items = list(jobs.items())
    for i, (name, prompt) in enumerate(items):
        full = f"{prompt}\n\n{palette}".strip() if palette else prompt
        if generate(client, name, full, out_dir, temperature):
            ok += 1
        if i < len(items) - 1:
            time.sleep(2)

    print(f"done: {ok}/{len(items)} generated -> {out_dir}")


if __name__ == "__main__":
    main()
