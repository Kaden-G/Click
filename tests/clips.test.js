// Validates every Scene Script and renders each beat at several points in every phase.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + require('path').resolve(__dirname, '../dist/index.html'));
  const res = await p.evaluate(() => {
    const out = [], all = { [EXAMPLE.id]: EXAMPLE, ...CLIPS };
    const keys = new Set(window.clickCards.all.map(c => c.key));
    for (const k in all) {
      const s = all[k], v = validate(s), tot = s.beats.reduce((a, x) => a + x.dur, 0);
      let bad = null;
      for (const beat of s.beats) for (const pr of [0, 0.3, 0.6, 1]) for (const ph of ['ask', 'wait', 'answer']) {
        const svg = PRIM[beat.primitive](beat.data || {}, pr, ph);
        if (/NaN|undefined/.test(svg)) bad = beat.primitive;
      }
      const last = s.beats[s.beats.length - 1].primitive;
      out.push({ k, v, tot, bad, recall: last === 'recall', card: k === EXAMPLE.id || keys.has(k) });
    }
    return out;
  });
  let fail = 0;
  for (const r of res) {
    const probs = [r.v, r.bad && 'render ' + r.bad, !r.recall && 'no closing recall', !r.card && 'no matching card'].filter(Boolean);
    if (probs.length) fail++;
    console.log((probs.length ? 'FAIL ' : 'ok   ') + r.k.padEnd(22) + String(r.tot).padStart(4) + 's ' + probs.join('; '));
  }
  console.log(`${res.length} clips, ${fail} failing · errors: ${JSON.stringify(errs)}`);
  await b.close(); process.exit(fail || errs.length ? 1 : 0);
})();
