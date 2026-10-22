// Smoke-test real compiled product apps, including shared-origin storage and SW scope.
const {chromium} = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');

async function main() {
  const root = path.resolve(__dirname, '../../apps/game/build/products');
  const products = (process.env.PRODUCT_IDS || (await fs.readdir(root)).join(',')).split(',').filter(Boolean);
  assert(products.length, 'No built product apps to test');
  const mime = {'.js':'text/javascript','.json':'application/json','.wasm':'application/wasm','.html':'text/html','.png':'image/png','.ttf':'font/ttf'};
  const server = http.createServer(async (req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      assert(pathname.startsWith('/Pixelhub/'));
      const rest = pathname.slice('/Pixelhub/'.length).split('/');
      const product = products.includes(rest[0]) && rest[0] !== 'pixelhub' ? rest.shift() : 'pixelhub';
      assert(products.includes(product));
      const relative = rest.join('/') || 'index.html';
      const file = path.resolve(root, product, relative);
      assert(file.startsWith(path.resolve(root, product) + path.sep));
      const stat = await fs.stat(file);
      const actual = stat.isDirectory() ? path.join(file, 'index.html') : file;
      res.writeHead(200, {'content-type': mime[path.extname(actual)] || 'application/octet-stream'});
      res.end(await fs.readFile(actual));
    } catch (_) { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/Pixelhub/`;
  let browser;
  const errors = [];
  try {
    browser = await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH || undefined,args:['--no-sandbox','--enable-unsafe-swiftshader']});
    const context = await browser.newContext({viewport:{width:390,height:900}});
    // Seed the original scope and confirm other products do not erase it.
    let first = await context.newPage();
    await first.goto(base + (products.includes('pixelhub') ? '' : products[0] + '/'));
    await first.evaluate(() => localStorage.setItem('flutter.pixelhub.language', JSON.stringify('en')));
    await first.close();
    for (const id of products) {
      const config = JSON.parse(await fs.readFile(path.resolve(__dirname, `../../products/${id}.yaml`), 'utf8'));
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(`${id}: ${error.message}`));
      const url = base + (id === 'pixelhub' ? '' : id + '/');
      await page.goto(url);
      await page.waitForFunction(() => !document.getElementById('bootstrap-status'), undefined, {timeout:60000});
      const activation = page.locator('flt-semantics-placeholder');
      if (await activation.count()) await activation.evaluate(e => e.click());
      const start = page.getByRole('button', {name:/شروع.*رنگ‌آمیزی|ادامه نقاشی|Start.*coloring|Continue painting|View result|دیدن نتیجه/}).first();
      await start.waitFor({timeout:30000});
      if (id !== 'pixelhub') {
        await page.getByText(config.identity.display_name_fa, {exact:true}).waitFor();
        assert.equal(await page.getByText(/سکه‌های من|My coins/).count(), 0);
      }
      await page.screenshot({path:path.join(__dirname, 'artifacts', `${id}-home.png`), fullPage:true});
      await start.click();
      await page.locator('[flt-semantics-identifier="painting-board"]').waitFor({timeout:30000});
      if (!config.features.coins) assert.equal(await page.getByText(/سکه‌های من|My coins/).count(), 0);
      await page.setViewportSize({width:740,height:390});
      await page.screenshot({path:path.join(__dirname, 'artifacts', `${id}-landscape.png`)});
      const keys = await page.evaluate(() => Object.keys(localStorage));
      assert(keys.some(k => k.includes('pixelhub.language')), 'Legacy key was lost');
      console.log(`PASS ${id}: home, painting navigation, narrow/landscape layouts and shared-origin storage`);
      await page.close();
    }
    assert.deepEqual(errors, []);
    await context.close();
  } finally { if (browser) await browser.close(); await new Promise(resolve => server.close(resolve)); }
}
fs.mkdir(path.join(__dirname, 'artifacts'), {recursive:true}).then(main).catch(error => { console.error(error); process.exitCode=1; });
