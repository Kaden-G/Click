#!/usr/bin/env python3
"""Turn documentation into Click study cards with your configured model.

    python3 generate.py --set acme --name "Acme Platform" docs/*.md notes.txt
    python3 build.py

Writes content/private/<set>.json. That folder is git-ignored so work material
never lands in a personal repo. Re-running merges new cards into the set and
keeps existing card ids, so your review history stays attached.
"""
import argparse, html, json, pathlib, re, sys
import llm

ROOT = pathlib.Path(__file__).parent
PROMPT = """You are writing study cards to help an engineer learn a product from its own documentation. Use ONLY the text below. Do not add outside facts or guess.

Write up to {n} cards. Each card is one idea worth remembering: how something works, why it's designed that way, a limit or default, a dependency, an interface, or a common mistake. Skip boilerplate, legal text, tables of contents and changelog noise. If nothing here is worth a card, reply [].

Each card is a JSON object:
  "t": a question the learner should be able to answer, under 15 words, that doesn't give the answer away
  "b": the answer in plain words, 40 to 80 words, specific to this product
  "y": one concrete action to apply or check it, under 20 words
  "cat": a short topic label, 1 to 3 words

Reply with only a JSON array of cards.

SOURCE: {source}
TEXT:
{text}"""


def read_text(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm"):
        raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"[ \t]+", " ", raw)


def chunks(text, limit):
    heading, buf, out = "", [], []
    for para in re.split(r"\n\s*\n", text):
        h = re.match(r"\s*#{1,4}\s+(.+)", para)
        if h:
            heading = h.group(1).strip()[:80]
        if buf and sum(len(p) for p in buf) + len(para) > limit:
            out.append(("\n\n".join(buf), heading))
            buf = []
        buf.append(para[:limit])
    if buf:
        out.append(("\n\n".join(buf), heading))
    return out


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "card"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", required=True, help="short id, e.g. acme (letters, numbers, hyphens)")
    ap.add_argument("--name", required=True, help="name shown in the feed, e.g. 'Acme Platform'")
    ap.add_argument("--per-chunk", type=int, default=5)
    ap.add_argument("--chunk-chars", type=int, default=6000)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,30}", a.set):
        sys.exit("--set must be lowercase letters, numbers and hyphens.")
    cfg = llm.load_config()
    out = ROOT / "content/private" / f"{a.set}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(out.read_text()) if out.exists() else {"id": a.set, "name": a.name, "cards": []}
    data["name"] = a.name
    seen = {c["t"].strip().lower() for c in data["cards"]}
    ids = {c["id"] for c in data["cards"]}
    added = 0
    for f in a.files:
        path = pathlib.Path(f)
        if not path.is_file():
            print(f"skip {f}: not a file"); continue
        for i, (text, heading) in enumerate(chunks(read_text(path), a.chunk_chars)):
            source = path.name + (f" · {heading}" if heading else "")
            try:
                cards = llm.parse_json(llm.complete(PROMPT.format(n=a.per_chunk, source=source, text=text), cfg))
            except llm.LLMError as e:
                print(f"  {source}: {e}"); continue
            for c in cards if isinstance(cards, list) else []:
                if not all(isinstance(c.get(k), str) and c[k].strip() for k in ("t", "b", "y")):
                    continue
                if c["t"].strip().lower() in seen:
                    continue
                cid, n = slug(c["t"]), 2
                while cid in ids:
                    cid, n = f"{slug(c['t'])}-{n}", n + 1
                ids.add(cid); seen.add(c["t"].strip().lower())
                data["cards"].append({"id": cid, "cat": str(c.get("cat", "")).strip()[:40], "source": source,
                                      "t": c["t"].strip(), "b": c["b"].strip(), "y": c["y"].strip()})
                added += 1
            print(f"  {source}: {len(data['cards'])} cards so far")
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {added} cards to {out.relative_to(ROOT)} ({len(data['cards'])} total). Now run: python3 build.py")


if __name__ == "__main__":
    main()
