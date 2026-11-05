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
    sets, set_ids = [], {b["id"] for b in books} | {"myth"}
    for folder in ("content/private", "content/sets"):
        for f in sorted((ROOT / folder).glob("*.json")):
            s = json.loads(f.read_text(encoding="utf-8"))
            if not s.get("id") or not s.get("name") or not isinstance(s.get("cards"), list):
                sys.exit(f"{f}: a set needs id, name and a cards list")
            if s["id"] in set_ids:
                sys.exit(f"{f}: set id {s['id']!r} is already used")
            set_ids.add(s["id"])
            card_ids = set()
            for c in s["cards"]:
                if not all(isinstance(c.get(k), str) and c[k] for k in ("id", "t", "b", "y")):
                    sys.exit(f"{f}: every card needs id, t, b and y")
                if c["id"] in card_ids:
                    sys.exit(f"{f}: duplicate card id {c['id']!r}")
                card_ids.add(c["id"])
            sets.append(s)
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
        "/*@MYTHS*/[]": myths, "/*@SETS*/[]": sets, "/*@BOOKS*/[]": books,
    }.items():
        if html.count(token) != 1:
            sys.exit(f"src/index.html: expected one {token}")
        html = html.replace(token, js(value))
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/index.html").write_text(html, encoding="utf-8")
    cards = sum(len(b["clicks"]) for b in books) + sum(len(m["clicks"]) for m in myths) + sum(len(s["cards"]) for s in sets)
    print(f"dist/index.html: {cards} cards in {len(sets)} sets plus books and myths, {len(clips) + 1} clips")


if __name__ == "__main__":
    main()
