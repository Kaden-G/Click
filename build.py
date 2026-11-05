#!/usr/bin/env python3
"""Build dist/index.html: inline content/ and clips/ JSON into src/index.html.

The published artifact is dist/index.html. Edit content and clips as JSON,
edit the app in src/index.html, then run: python3 build.py
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
REQUIRED_CLIP = {"id", "title", "beats"}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def js(value):
    # Safe to inline inside a <script> element.
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def main():
    books, myths = load("content/books.json"), load("content/myths.json")
    clips = {}
    for f in sorted((ROOT / "clips").glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        missing = REQUIRED_CLIP - c.keys()
        if missing:
            sys.exit(f"{f.name}: missing {sorted(missing)}")
        if c["id"] != f.stem:
            sys.exit(f"{f.name}: id is {c['id']!r}, expected {f.stem!r}")
        clips[c["id"]] = c
    example = clips.pop("spaced-repetition-101")
    html = (ROOT / "src/index.html").read_text(encoding="utf-8")
    for token, value in {
        "/*@EXAMPLE*/null": example, "/*@CLIPS*/{}": clips,
        "/*@MYTHS*/[]": myths, "/*@BOOKS*/[]": books,
    }.items():
        if html.count(token) != 1:
            sys.exit(f"src/index.html: expected one {token}")
        html = html.replace(token, js(value))
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/index.html").write_text(html, encoding="utf-8")
    cards = sum(len(b["clicks"]) for b in books) + sum(len(m["clicks"]) for m in myths)
    print(f"dist/index.html: {cards} cards, {len(clips) + 1} clips")


if __name__ == "__main__":
    main()
