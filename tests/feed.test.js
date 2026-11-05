const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 400, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + require('path').resolve(__dirname, '../dist/index.html'));
  const txt = s => p.$eval(s, el => el.innerText);
  console.log('PROMPT:', (await txt('#card')).slice(0, 160).replace(/\n/g, ' | '));
  await p.fill('#guess', 'small habits add up');
  await p.click('#card [data-sure]');
  console.log('OPEN has You said:', (await txt('#card')).toLowerCase().includes('small habits add up'));
  await p.click('#save');
  await p.click('.chip[data-id="review"]');
  console.log('REVIEW:', (await txt('#card')).slice(0, 120).replace(/\n/g, ' | '));
  await p.click('#card [data-sure="1"]');
  await p.click('#card [data-got="1"]');
  console.log('NOTE:', await txt('.gnote'));
  console.log('STATS:', await txt('#stats'));
  await p.click('.chip[data-id="atomic"]');
  console.log('HINT visible:', await p.isVisible('#hint'));
  await p.click('.chip[data-id="all"]');
  if (await p.$('#card [data-sure]')) await p.click('#card [data-sure]');
  await p.click('#watch');
  await p.evaluate(() => { const s = CLIPS['atomic-1']; });
  // jump to recall beat
  await p.uncheck('#voice'); await p.click('#dots .dot:last-child'); await p.waitForTimeout(400);
  await p.waitForTimeout(6800);
  console.log('REVEAL visible:', await p.isVisible('#reveal'));
  if (await p.isVisible('#reveal')) { await p.click('#reveal'); await p.click('#cgrade .g-miss'); console.log('CLIP NOTE:', await txt('#cgrade')); }
  console.log('STATS2:', await txt('#stats'));
  console.log('ERRORS:', errs);
  await p.screenshot({ path: require('os').tmpdir() + '/click-shot.png', fullPage: false });
  await b.close();
})();
