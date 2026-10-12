const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

async function main() {
  const baseUrl = process.env.PIXELHUB_BASE_URL || 'http://127.0.0.1:8080/Pixelhub/';
  const output = process.env.PIXELHUB_SMOKE_OUTPUT || path.join(__dirname, 'artifacts');
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_PATH || undefined,
    args: ['--no-sandbox', '--enable-unsafe-swiftshader'],
  });
  const pageErrors = [];
  const failedRequests = [];
  const externalRequests = [];
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    page.on('pageerror', error => pageErrors.push(error.message));
    page.on('requestfailed', request => failedRequests.push(request.url()));
    page.on('request', request => {
      const url = new URL(request.url());
      if (url.protocol.startsWith('http') && url.origin !== new URL(baseUrl).origin) {
        externalRequests.push(url.origin);
      }
    });
    const openPreview = () => page.getByRole('button', { name: 'دیدن تصویر نمونه' });
    const backHome = () => page.getByRole('button', { name: 'بازگشت به خانه' });
    const waitForAccessibleApp = async () => {
      await page.waitForFunction(() => !document.getElementById('bootstrap-status'));
      await page.locator('flt-semantics-placeholder').evaluate(element => element.click());
      await openPreview().or(backHome()).first().waitFor();
    };

    await page.goto(baseUrl);
    await waitForAccessibleApp();
    await page.screenshot({ path: path.join(output, 'home-mobile.png') });
    await openPreview().click();
    await backHome().waitFor();
    assert.equal(new URL(page.url()).hash, '#/painting');
    await page.screenshot({ path: path.join(output, 'preview-mobile.png') });

    await page.goBack();
    await openPreview().waitFor();
    await page.goForward();
    await backHome().waitFor();
    await page.reload();
    await waitForAccessibleApp();
    const bounds = await backHome().boundingBox();
    assert(bounds && bounds.x >= 0 && bounds.x + bounds.width <= 390,
      'Refreshed route must render its Back button inside the viewport');
    await backHome().click();
    await openPreview().waitFor();

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(baseUrl);
    await waitForAccessibleApp();
    await page.screenshot({ path: path.join(output, 'home-desktop.png') });
    const actionBounds = await openPreview().boundingBox();
    assert(actionBounds && actionBounds.x >= (1440 - 430) / 2 &&
      actionBounds.x + actionBounds.width <= (1440 + 430) / 2,
      'Desktop actions must remain in the centered mobile frame');

    await page.setViewportSize({ width: 800, height: 360 });
    await page.goto(baseUrl);
    await waitForAccessibleApp();
    await page.mouse.move(400, 180);
    await page.mouse.wheel(0, 650);
    await openPreview().click();
    await backHome().click();
    await openPreview().waitFor();

    assert.deepEqual(pageErrors, [], 'JavaScript page errors');
    assert.deepEqual(failedRequests, [], 'Failed application asset requests');
    assert.deepEqual(externalRequests, [], 'The bundled preview must not require runtime CDNs');
    console.log(JSON.stringify({
      navigation: 'passed', browserBackForward: 'passed', hashRefresh: 'passed',
      desktopFrame: 'passed', shortHeight: 'passed', runtimeRequests: 'local only',
      pageErrors, screenshots: output,
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
