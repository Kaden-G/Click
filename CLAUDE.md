# Click

A personal learning feed: idea cards, narrated Scene Script clips, spaced review, and a five-minute AI interview. Learning design follows *Make It Stick* (Brown, Roediger & McDaniel, 2014). See README.md for layout and spec/scene-script.md for the clip format.

## Change loop

1. Edit content in `content/*.json`, clips in `clips/*.json`, or the app in `src/index.html`. Never edit `dist/index.html` by hand.
2. `python3 build.py`
3. `node tests/feed.test.js`, `node tests/interview.test.js` and `node tests/clips.test.js`; all must report no errors and no failing clips.
4. Commit, then push to `origin main`. After pushing, regenerate the portable bundle with `python3 tools/bundle.py` if it's needed.
5. Republish `dist/index.html` to the existing artifact (https://claude.ai/artifact/2MVxPh4Q35i8eAhgqKR2XA) rather than creating a new one. It declares the `sample` capability; omit `capabilities` on republish to keep it.

## Content rules

- Cards are written in our own words. No quotes from books beyond a few words.
- Every card ends with a `y` ("Try") line: one concrete action.
- Research claims carry a source. Contested findings get a `flag` on the card; myth-style items carry `strength`: Strong, Moderate, or Weak.
- Don't overstate. If evidence is mixed, the card says so.
- New topic batches go in `content/sets/<id>.json` (`id`, `name`, optional `prompt`, `cards[]` with `id`, `t`, `b`, `y`, optional `cat` and `source`). Each set gets its own chip and interview topic and is interleaved into Mixed. Card keys are `<set-id>-<card-id>`.
- Never commit `content/private/` or `click.config.json`; they hold work material and endpoint settings.
- Figures that change over time (budgets, debt, trust funds) name their source and date on the card.
- Government and politics content sticks to how things work, sourced to official or nonpartisan data, and debunks myths from across the spectrum.

## Clip rules

- One idea per clip, 1 to 8 beats, 4 to 20 seconds each, under 120 seconds total.
- Every clip ends with a `recall` beat.
- No invented numbers. If a `compare` would need made-up heights, use `split`.
- Anything not drawn to scale says so on screen (`note`).
- Clips about research findings set `strength`; the player shows it the whole time.
- The clip `id` matches its filename and, when tied to a card, the card key (`<book-or-set-id>-<n>`), so clip grades feed the review queue.

## Design guardrails

- The model is rented and swappable (Scene Script writing, interview). Value lives in the corpus, the renderer, and review data. Don't add features that only resell a model call.
- Learning features follow the research: generation before reveal, retrieval over rereading, spacing, interleaving, calibration, feedback.
- Keep the page self-contained: CDN allowlist only, theme tokens for every color, works at 400px wide.
