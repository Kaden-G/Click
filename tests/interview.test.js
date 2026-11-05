const { chromium } = require('playwright');
const fake = () => {
  const s = async () => ({ text: "x" });
  let call = 0;
  s.json = async (input) => {
    call++;
    if (call === 1) return [
      { type: "explain", q: "In your own words, why do tiny daily gains matter?", keys: ["compounding", "results lag"], cards: ["atomic-1"] },
      { type: "apply", q: "How would you turn a goal at work into a system?", keys: ["daily process", "you control it"], cards: ["atomic-2"] },
      { type: "limits", q: "When might the two-minute rule fail?", keys: ["complex skills"], cards: ["atomic-5"] },
      { type: "connect", q: "How do identity votes relate to the four laws?", keys: ["evidence", "levers"], cards: ["atomic-3", "atomic-4"] },
      { type: "scenario", q: "Your team keeps missing standups. What would you change?", keys: ["make it easy", "cue"], cards: ["bogus-9"] }];
    return { summary: "Solid grasp of compounding; thinner on limits.", sustain: ["Concrete examples", "Clear cause and effect"], improve: ["Name when an idea breaks", "Link ideas explicitly"],
      items: [{ i: 1, rating: "strong", feedback: "Good.", next: "Add a number." }, { i: 2, rating: "partial", feedback: "Missing control.", next: "Say who owns it." },
              { i: 3, rating: "missed", feedback: "No answer.", next: "Try one case." }, { i: 4, rating: "strong", feedback: "Nice link." }, { i: 5, rating: "partial", feedback: "Half there." }] };
  };
  window.claude = { use: async n => n === "sample" ? s : null };
};
(async () => {
  const b = await chromium.launch();
  for (const ai of [false, true]) {
    const p = await b.newPage({ viewport: { width: 400, height: 900 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    if (ai) await p.addInitScript(fake);
    await p.goto('file://' + require('path').resolve(__dirname, '../dist/index.html'));
    await p.waitForTimeout(300);
    await p.selectOption('#ivTopic', 'atomic');
    await p.click('#ivStart');
    await p.waitForSelector('#ivQ:not([hidden])');
    console.log(ai ? 'AI' : 'OFFLINE', '| mode:', (await p.textContent('#ivMode')).slice(0, 40), '| prog:', await p.textContent('#ivProg'), '| timer:', await p.textContent('#ivTimer'));
    await p.fill('#ivAns', 'Small gains compound over time and results lag.');
    await p.click('#ivNext');
    await p.fill('#ivAns', 'Make a daily process.');
    await p.click('#ivEnd');
    await p.waitForSelector('#ivResult:not([hidden])');
    const r = await p.innerText('#ivResult');
    console.log('  result head:', r.split('\n').slice(0, 4).join(' / '));
    await p.click('#ivQueue');
    console.log('  queue:', await p.textContent('#ivQNote'), '| stats:', await p.textContent('#stats'));
    if (ai) await p.screenshot({ path: require('os').tmpdir() + '/click-iv.png', fullPage: false, clip: { x: 0, y: await p.$eval('#ivResult', el => el.getBoundingClientRect().top + scrollY - 10), width: 400, height: 900 } }).catch(async () => p.screenshot({ path: require('os').tmpdir() + '/click-iv.png' }));
    console.log('  errors:', errs);
  }
  await b.close();
})();
