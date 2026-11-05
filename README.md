# Click

Ideas that click, and stick. A personal learning feed: bite-sized idea cards, short narrated explainer clips, spaced review, and a five-minute AI interview with feedback. The learning design follows *Make It Stick* (Brown, Roediger & McDaniel, 2014).

## Layout

| Path | What it is |
|---|---|
| `src/index.html` | The app: clip renderer, feed, review, interview |
| `content/books.json` | 50 clicks from 10 books (2016–2024) |
| `content/myths.json` | 20 clicks testing 10 common beliefs, each with an evidence-strength rating |
| `content/wrong.json` | 20 things people commonly get wrong: government, numbers and money, tech and everyday |
| `clips/*.json` | One Scene Script per clip (29) |
| `spec/scene-script.md` | The Scene Script format and its rules |
| `build.py` | Inlines content and clips into `dist/index.html` |
| `tests/` | Headless browser checks for the feed and the interview |

## Build and test

```sh
python3 build.py              # writes dist/index.html
node tests/feed.test.js       # predict, reveal, review, grade, clip recall
node tests/interview.test.js  # offline and simulated-AI interviews
node tests/clips.test.js      # every Scene Script validates and renders
```

Tests need Node and Playwright with Chromium.

## Where the value lives

The model is rented and swappable: it writes Scene Scripts and runs the interview. The corpus (`content/`, `clips/`), the renderer, and your review history are what Click owns.

## Known limits

- Review progress lives in browser storage, per device. Moving it to SQLite is the next infrastructure step.
- Interview questions are generated up front; there are no adaptive follow-ups yet.
- Reflection, the one *Make It Stick* principle not yet covered, is planned as a weekly prompt.
