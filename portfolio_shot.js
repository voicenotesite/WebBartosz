const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto('https://voicenotesite.github.io/WebBartosz/', { waitUntil: 'load' });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'screenshots/portfolio.png' });
  await browser.close();
})();
