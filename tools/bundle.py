#!/usr/bin/env python3
"""Pack the repo's tracked source files into click-bundle.txt, a plain-text file
that is also a Python script: `python3 click-bundle.txt` unpacks it.
dist/ is left out; build.py recreates it."""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = "===== FILE: "

HEADER = '''#!/usr/bin/env python3
# Click bundle: a personal learning feed (cards, clips, spaced review, AI interview)
#
# This text file is also a Python script. To unpack it on a Mac:
#
#   1. Save it as click-bundle.txt, for example in ~/Downloads.
#   2. Open Terminal and run:
#        cd ~/Downloads
#        python3 click-bundle.txt
#      That creates a "click" folder next to this file and builds the app.
#   3. Follow README.md in that folder, section "Run it with your work models".
#
# Everything below is readable source. Review it before running if you like.
# Nothing here contacts the network until you configure a model yourself.

import pathlib, subprocess, sys

PAYLOAD = r\'\'\'
'''

FOOTER = '''\'\'\'


def main():
    out = pathlib.Path(__file__).resolve().parent / "click"
    if out.exists() and "--force" not in sys.argv:
        sys.exit(f"{out} already exists. Move it, or rerun with --force to overwrite matching files.")
    count = 0
    for block in PAYLOAD.split("\\n''' + MARK + '''")[1:]:
        head, _, body = block.partition("\\n")
        rel = head.rstrip(" =")
        path = out / rel
        if ".." in pathlib.PurePosixPath(rel).parts:
            sys.exit(f"Refusing unsafe path: {rel}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body[:-1] if body.endswith("\\n") else body, encoding="utf-8")
        count += 1
    print(f"Unpacked {count} files into {out}")
    subprocess.run([sys.executable, "build.py"], cwd=out, check=False)
    print("Next: open README.md and follow 'Run it with your work models'.")


if __name__ == "__main__":
    main()
'''


def main():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in files if not f.startswith("dist/") and f != "tools/bundle.py"]
    parts = []
    for f in sorted(files):
        text = (ROOT / f).read_text(encoding="utf-8")
        if "\'\'\'" in text or MARK in text:
            sys.exit(f"{f} contains a bundle delimiter; can't pack it safely.")
        if text.endswith("\\"):
            sys.exit(f"{f} ends with a backslash; can't pack it safely.")
        parts.append(f"{MARK}{f} =====\n{text}\n")
    out = ROOT / "click-bundle.txt"
    out.write_text(HEADER + "\n".join(parts) + FOOTER, encoding="utf-8")
    print(f"Wrote {out.name}: {len(parts)} files, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
