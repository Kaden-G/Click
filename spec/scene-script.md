# Scene Script v0

A clip is a small JSON file. A model (or a person) writes it; Click's renderer performs it with motion, captions, and an on-device voice. The script supplies numbers and labels; the renderer owns every coordinate, color, and easing curve.

```json
{
  "id": "atomic-1",
  "title": "Tiny gains compound",
  "strength": "Strong",
  "beats": [
    { "primitive": "title", "dur": 5, "say": "Narration and captions.", "data": { "kicker": "Atomic Habits", "lines": ["Tiny gains", "compound"] } }
  ]
}
```

`id` must match the file name. `strength` (`Strong`, `Moderate`, `Weak`) is required for clips about a research finding and stays on screen for the whole clip.

## Primitives

| Primitive | Shows | Data |
|---|---|---|
| `title` | Opening hook | `kicker`, `lines[]` |
| `curve` | A value decaying over days, with resets | `reviews[]` in days, `ghost` |
| `growth` | Compounding, straight lines, and S-curves | `title`, `points`, `series[{label, fn, rate, tone}]`, `note` |
| `intervals` | Bars to scale, revealed in order | `title`, `max`, `unit`, `items[{label, value}]` |
| `compare` | Two or three bars of one measured quantity | `title`, `items[{label, value, tone}]`, `note[]` |
| `split` | Two sides contrasted trait by trait | `title`, `left{label, rows[]}`, `right{label, rows[]}` |
| `grid` | A whole as countable dots | `title`, `total`, `cols`, `filled`, `highlight[]`, `legend[]` |
| `network` | Layered nodes and links, chokepoints lit | `title`, `nodes[{id, label, layer}]`, `links[[a, b]]`, `choke[]` |
| `flow` | A short process, lit step by step | `steps[{t, s}]` |
| `recall` | Pauses for the viewer to answer, then reveals | `question`, `answer` |

## Rules

1. One idea per clip, ending with a `recall` beat.
2. 1 to 8 beats, 4 to 20 seconds each, under 120 seconds total.
3. `say` is both narration and captions, so write it to be heard.
4. Data holds numbers and labels only, never positions.
5. Anything not drawn to scale says so on screen.
6. If you would have to invent the numbers for a `compare`, use `split`.
7. A beat waits for the voice to finish, so long lines stretch the beat.
