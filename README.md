# Click

Ideas that click, and stick. A personal learning feed: bite-sized idea cards, short narrated explainer clips, spaced review, and a five-minute AI interview with feedback. The learning design follows *Make It Stick* (Brown, Roediger & McDaniel, 2014).

## Layout

| Path | What it is |
|---|---|
| `src/index.html` | The app: clip renderer, feed, review, interview |
| `content/books.json` | 50 clicks from 10 books (2016–2024) |
| `content/myths.json` | 20 clicks testing 10 common beliefs, each with an evidence-strength rating |
| `clips/*.json` | One Scene Script per clip (29) |
| `spec/scene-script.md` | The Scene Script format and its rules |
| `content/sets/*.json` | Card sets in a simple format (`id`, `name`, `cards[]`); "Things people get wrong" lives here |
| `content/private/` | Your own sets, e.g. generated from product docs. Git-ignored |
| `build.py` | Inlines content and clips into `dist/index.html` |
| `llm.py` | Model adapter: OpenAI-compatible, Azure OpenAI, or Anthropic endpoints |
| `serve.py` | Local server for Click that routes AI calls to your configured model |
| `generate.py` | Turns documentation into study cards with your model |
| `tools/bundle.py` | Packs the repo into `click-bundle.txt` for moving to another machine |
| `tests/` | Headless browser checks for the feed and the interview |

## Build and test

```sh
python3 build.py              # writes dist/index.html
node tests/feed.test.js       # predict, reveal, review, grade, clip recall
node tests/interview.test.js  # offline and simulated-AI interviews
node tests/clips.test.js      # every Scene Script validates and renders
```

Tests need Node and Playwright with Chromium.

## Run it with your work models

Use only models and endpoints your organization has approved, and only put material into Click that you're allowed to send to them.

1. **Unpack** (if you came from `click-bundle.txt`): `python3 click-bundle.txt`, then `cd click`.
2. **Configure the model:** `cp click.config.example.json click.config.json`, then edit it.
   - `provider`: `openai` for any OpenAI-compatible endpoint (most AI gateways, LiteLLM, vLLM), `azure` for Azure OpenAI, `anthropic` for the Anthropic API.
   - `base_url`: for `openai`, the URL ending in `/v1`; for `azure`, the full deployment URL including `?api-version=...`; for `anthropic`, the API host.
   - `model`: the model name your gateway expects.
   - `api_key_env`: the environment variable that holds your key. Leave it empty if your gateway needs no key.
   - `extra_headers`: any headers your gateway requires.
   - `ca_bundle`: path to your company's certificate bundle if HTTPS fails with a certificate error.
   - Newer OpenAI models may need `"max_tokens_field": "max_completion_tokens"`.
3. **Set your key** for this Terminal session: `export CLICK_API_KEY=...`
4. **Make cards from your product docs** (Markdown, text or HTML):
   `python3 generate.py --set myproduct --name "My Product" path/to/docs/*.md`
   Cards are written to `content/private/myproduct.json`. Read through them and delete or fix any that are wrong; the model only drafts them.
5. **Build and run:** `python3 build.py`, then `python3 serve.py --open`.
6. Your set appears as its own chip in the feed and as an interview topic. The interview runs on your configured model.

Opening `dist/index.html` directly also works, but without AI: the interview falls back to offline mode.

**Keep work content out of personal accounts.** `content/private/` and `click.config.json` are git-ignored. Don't copy generated sets back to a personal machine or repo.

## Where the value lives

The model is rented and swappable: it writes Scene Scripts and runs the interview. The corpus (`content/`, `clips/`), the renderer, and your review history are what Click owns.

## Known limits

- Review progress lives in browser storage, per device. Moving it to SQLite is the next infrastructure step.
- Interview questions are generated up front; there are no adaptive follow-ups yet.
- Reflection, the one *Make It Stick* principle not yet covered, is planned as a weekly prompt.
