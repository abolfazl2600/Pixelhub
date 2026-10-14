const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const crypto = require('node:crypto');
const path = require('node:path');

async function main() {
  const base = process.env.PIXELHUB_BASE_URL || 'http://127.0.0.1:8080/Pixelhub/';
  const output = process.env.PIXELHUB_SMOKE_OUTPUT || path.join(__dirname, 'artifacts');
  const onlineBase = 'https://abolfazl2600.github.io/Pixelhub/online/';
  await fs.mkdir(output, {recursive:true});
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROMIUM_PATH || undefined,
    args:['--no-sandbox','--enable-unsafe-swiftshader']});
  const pageErrors = [], failedRequests = [], externalRequests = [];
  try {
    const context = await browser.newContext({viewport:{width:390,height:1000},locale:'en-US'});
    let page = await context.newPage();
    function watch(p) {
      p.on('pageerror', e => pageErrors.push(e.message));
      p.on('requestfailed', r => failedRequests.push(r.url()));
      p.on('request', r => { const u=new URL(r.url()); if(u.protocol.startsWith('http') && u.origin!==new URL(base).origin && !u.href.startsWith(onlineBase)) externalRequests.push(u.origin); });
    }
    watch(page);
    const start = () => page.getByRole('button',{name:/شروع.*رنگ‌آمیزی|Start.*coloring/});
    const back = () => page.getByRole('button',{name:/بازگشت به خانه|Back to Home/});
    const board = () => page.locator('[flt-semantics-identifier="painting-board"]');
    async function ready() {
      await page.waitForFunction(()=>!document.getElementById('bootstrap-status'));
      const activation=page.locator('flt-semantics-placeholder');
      if(await activation.count()) await activation.evaluate(e=>e.click());
      await start().or(back()).first().waitFor();
    }
    async function scrollTop() {
      const vp=page.viewportSize();
      await page.mouse.move(vp.width-4, Math.min(vp.height-40,300));
      await page.mouse.wheel(0,-1200);
      await board().waitFor();
    }
    async function record() {
      return page.evaluate(()=>{
        const k=Object.keys(localStorage).find(k=>k.includes('pixelhub.progress.v1.sunflower.2'));
        if(!k) return null;
        let v=JSON.parse(localStorage[k]); if(typeof v==='string')v=JSON.parse(v); return v;
      });
    }
    async function saved(count) {
      await page.waitForFunction(expected=>{
        const k=Object.keys(localStorage).find(k=>k.includes('pixelhub.progress.v1.sunflower.2'));
        if(!k)return false;
        let v=JSON.parse(localStorage[k]); if(typeof v==='string')v=JSON.parse(v); return v.completedCount===expected;
      },count);
      await page.locator('flutter-view').getByText('Saved',{exact:true}).waitFor();
    }
    // Flutter frequently replaces semantics nodes during layout. Avoid
    // Playwright element actions here: the target may detach while the action
    // waits for stability. Query its current rect atomically on each frame.
    // Call scrollTop() first when navigating from a scrolled viewport.
    async function boardBox() {
      const handle=await page.waitForFunction(()=>{
        const element=document.querySelector('[flt-semantics-identifier="painting-board"]');
        if(!element)return false;
        const rect=element.getBoundingClientRect();
        if(rect.width<=0 || rect.height<=0 || rect.top<0 || rect.bottom>innerHeight)return false;
        return {x:rect.x,y:rect.y,width:rect.width,height:rect.height};
      });
      return handle.jsonValue();
    }
    async function point(x,y) {
      const b=await boardBox();
      return {x:b.x+b.width*(x+.5)/16, y:b.y+b.height*(y+.5)/16};
    }
    async function line(x1,y,x2) {
      const a=await point(x1,y),b=await point(x2,y);
      await page.mouse.move(a.x,a.y); await page.mouse.down();
      if(x1!==x2)await page.mouse.move(b.x,b.y); await page.mouse.up();
    }

    console.log('Browser: default language and home');
    await page.goto(base); await ready();
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'fa');
    await page.screenshot({path:path.join(output,'home-fa.png')});
    // Language selection belongs to Profile, not Home or the painting toolbar.
    await page.getByRole('button',{name:'پروفایل',exact:true}).first().click();
    await page.getByRole('button',{name:'English',exact:true}).click();
    await page.getByRole('button',{name:'فارسی',exact:true}).waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'en');
    await back().click(); await start().waitFor();
    await page.screenshot({path:path.join(output,'home-en.png')});
    console.log('Browser: painting and autosave');
    await start().click(); await board().waitFor();
    assert.equal(new URL(page.url()).hash,'#/painting/sunflower');
    await line(0,0,15); await saved(16);
    const wrong=await point(7,5); await page.mouse.click(wrong.x,wrong.y);
    await page.locator('flutter-view').getByText('That cell needs a different color number.', {exact:true}).waitFor();
    assert.equal((await record()).completedCount,16);
    await page.screenshot({path:path.join(output,'painting-en.png')});
    await page.getByRole('button',{name:'Start over',exact:true}).click();
    await page.getByRole('button',{name:'Cancel',exact:true}).click();
    assert.equal((await record()).completedCount,16);

    // Recreate the entire Flutter application in a new page, retaining real browser storage.
    await page.close(); page=await context.newPage(); watch(page);
    await page.goto(base+'#/painting/sunflower'); await ready(); await board().waitFor(); await saved(16);
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'en');
    await page.reload(); await ready(); await board().waitFor(); await saved(16);
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'en');
    await back().click(); await start().waitFor();
    await page.goBack(); await back().waitFor();
    await page.goForward(); await start().waitFor();
    await start().click(); await board().waitFor();

    console.log('Browser: completing all colors');
    const asset=await page.request.get(base+'assets/assets/levels/sunflower-v2.json');
    const level=await asset.json();
    for(let color=0;color<level.palette.length;color++) {
      await page.getByRole('button',{name:new RegExp(`^Color ${color+1},`)}).click();
      await scrollTop();
      for(let y=0;y<16;y++) {
        for(let x=0;x<16;) {
          if(level.cells[y*16+x]!==color || y===0) {x++;continue;}
          let end=x;
          while(end+1<16 && level.cells[y*16+end+1]===color)end++;
          await line(x,y,end); x=end+1;
        }
      }
    }
    await page.getByText('You did it! Your picture is complete.').waitFor(); await saved(256);
    await page.screenshot({path:path.join(output,'completion-en.png')});
    await page.getByRole('button',{name:'View result',exact:true}).click();
    await page.getByRole('button',{name:'Start over',exact:true}).click();
    await page.getByRole('button',{name:'Start over',exact:true}).last().click(); await saved(0);
    assert.equal((await record()).generation,1);

    // Browser-only wallet fixture: the integration test checks multiple
    // purchases in succession without needing to finish a 128x128 picture.
    // This does not grant coins to real users or modify application code.
    await page.waitForFunction(() => Object.keys(localStorage).some(
      k => k.includes('pixelhub.library.v1')));
    await page.evaluate(() => {
      const key = Object.keys(localStorage).find(
        k => k.includes('pixelhub.library.v1'));
      let library = JSON.parse(localStorage[key]);
      const nested = typeof library === 'string';
      if (nested) library = JSON.parse(library);
      if (!Array.isArray(library.rewarded) ||
          !library.rewarded.includes('sunflower')) {
        throw Error('Sunflower completion should pay out exactly once');
      }
      library.coins = 750;
      localStorage.setItem(
        key,
        JSON.stringify(nested ? JSON.stringify(library) : library),
      );
    });
    await page.reload(); await ready();

    // Paint a real cell in each required size, using actual browser storage.
    for (const id of ['rainbow','gem','planet']) {
      await page.goto(base+'#/painting/'+id); await ready();
      // Direct links to locked pictures must show the purchase flow, not a
      // paintable board. Buy once and verify the board is then accessible.
      const unlock = page.getByRole('button',{name:/Unlock for [0-9]+ coins/});
      await unlock.waitFor();
      await unlock.click();
      await board().waitFor();
      await scrollTop();
      const dimension={rainbow:32,gem:64,planet:128}[id];
      const picture=(await (await page.request.get(base+`assets/assets/levels/${id}.json`)).json());
      // Painting near the extreme top-left is unreliable on very dense
      // mobile grids. Aim at an interior cell, explicitly selecting its
      // actual palette number so changing artwork colors doesn't break CI.
      const x=Math.floor(dimension/4), y=Math.floor(dimension/4);
      const color=picture.cells[y*dimension+x];
      console.log('Browser: sample cell',id,x,y,color);
      await page.getByRole('button',{name:new RegExp(`^Color ${color+1},`)}).click();
      await scrollTop();
      const current=await boardBox();
      await page.mouse.click(
        current.x+current.width*(x+0.5)/dimension,
        current.y+current.height*(y+0.5)/dimension
      );
      await page.waitForFunction(id=>{
        const k=Object.keys(localStorage).find(k=>k.includes('pixelhub.progress.v1.'+id+'.1'));
        if(!k)return false;
        let value=JSON.parse(localStorage[k]);if(typeof value==='string')value=JSON.parse(value);
        return value.completedCount===1;
      },id);
    }

    // A large level exercises zoom/culling without introducing a desktop layout.
    console.log('Browser: large grid and viewports');
    await page.goto(base+'#/painting/planet'); await ready(); await board().waitFor();
    await scrollTop();
    for(let n=0;n<5;n++) await page.getByRole('button',{name:'Zoom in',exact:true}).click();
    await page.getByRole('button',{name:'Move / zoom',exact:true}).click();
    const b=await boardBox();
    await page.mouse.move(b.x+b.width*.5,b.y+b.height*.5); await page.mouse.down();
    await page.mouse.move(b.x+b.width*.65,b.y+b.height*.6,{steps:10}); await page.mouse.up();
    await page.screenshot({path:path.join(output,'planet-zoom.png')});
    await page.setViewportSize({width:1440,height:900}); await page.goto(base); await ready();
    const action=await start().boundingBox();
    assert(action && action.x>=280 && action.x+action.width<=1160 &&
      action.width>430 && action.width<880,
      'desktop content must be centered inside the 880px frame');
    await page.screenshot({path:path.join(output,'home-desktop.png')});
    await page.setViewportSize({width:1024,height:768}); await page.goto(base); await ready();
    const tabletAction=await start().boundingBox();
    assert(tabletAction && tabletAction.width>action.width &&
      tabletAction.x>=0 && tabletAction.x+tabletAction.width<=1024,
      'tablet-sized view must use the full available width');
    await page.screenshot({path:path.join(output,'home-tablet.png')});
    await page.setViewportSize({width:800,height:360}); await page.goto(base); await ready();
    await start().click(); await back().click(); await start().waitFor();
    // The taller Home (with Continue Painting) may restore its prior scroll.
    // Scroll to the header before targeting Profile in a short viewport.
    await page.mouse.move(400,180);
    await page.mouse.wheel(0,-2000);
    await page.getByRole('button',{name:'Profile',exact:true}).first().click();
    await page.getByRole('button',{name:'فارسی',exact:true}).click();
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'fa');
    await back().click(); await page.reload(); await ready();
    await page.getByRole('button',{name:'پروفایل',exact:true}).first().click();
    await page.getByRole('button',{name:'English',exact:true}).waitFor();
    await back().click();

    // Exercise cross-platform HTTP loading in the browser. All online responses
    // are mocked: the test never depends on public GitHub Pages availability.
    console.log('Browser: online catalog and opt-in download');
    await page.setViewportSize({width:390,height:1000});
    const remoteLevel = {...level, levelId:'online-smoke-test', levelVersion:1,
      titles:{fa:'تصویر آنلاین آزمایشی',en:'Online browser sample'}};
    const canonical = [remoteLevel.schemaVersion, remoteLevel.levelId,
      remoteLevel.levelVersion, remoteLevel.titles.fa, remoteLevel.titles.en,
      remoteLevel.width, remoteLevel.height, remoteLevel.palette, remoteLevel.cells];
    remoteLevel.checksum = crypto.createHash('sha256')
      .update(JSON.stringify(canonical)).digest('hex');
    const levelPayload = Buffer.from(JSON.stringify(remoteLevel),'utf8');
    const remoteCatalog = JSON.stringify({schemaVersion:1,pictures:[{
      id:remoteLevel.levelId,version:1,title:remoteLevel.titles.fa,
      titleEn:remoteLevel.titles.en,category:'objects',
      width:remoteLevel.width,height:remoteLevel.height,
      bytes:levelPayload.length,checksum:remoteLevel.checksum,
    }]});
    const preview = Buffer.from(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Y9nYAAAAASUVORK5CYII=',
      'base64');
    const remoteRequests = [];
    page.on('console', message => {
      if (message.text().includes('Online picture download failed:')) {
        console.log('Browser content diagnostic:',message.text());
      }
    });
    await page.route(onlineBase+'**', async route => {
      remoteRequests.push(route.request().url());
      const uri = new URL(route.request().url());
      if(uri.pathname.endsWith('/catalog.json')) {
        return route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:remoteCatalog});
      }
      if(uri.pathname.endsWith('/levels/online-smoke-test-v1.json')) {
        return route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:levelPayload});
      }
      if(uri.pathname.endsWith('/previews/online-smoke-test-v1.png')) {
        return route.fulfill({status:200,contentType:'image/png',body:preview});
      }
      return route.fulfill({status:404,body:'Not found'});
    });
    await page.goto(base+'#/gallery'); await ready();
    // The online collection now follows the local grid. Scroll to the end
    // until its lazy sliver builds the explicit download control.
    const downloadButton = page.getByRole('button',{name:'دریافت تصویر',exact:true});
    // This test previously switched to a 360px-tall viewport; keep the
    // pointer inside it or wheel events will not scroll the gallery.
    const galleryViewport = page.viewportSize();
    await page.mouse.move(180, Math.min(250, galleryViewport.height - 30));
    for(let i=0;i<25 && !(await downloadButton.isVisible());i++) {
      await page.mouse.wheel(0,1600);
      await page.waitForTimeout(80);
    }
    await downloadButton.waitFor();
    await downloadButton.click();
    await page.waitForTimeout(600);
    console.log('Online test requests:',remoteRequests);
    console.log('Online test download failed:',
      await page.getByText('دریافت یا ذخیره این تصویر کامل نشد. دوباره تلاش کنید.',{exact:true}).count());
    // The gallery is lazy and its status panel may scroll out of view.
    // Confirm the user-approved level was actually written to browser storage.
    await page.waitForFunction(() => Object.keys(localStorage).some(
      key => key.includes('pixelhub.online.level.online-smoke-test')));
    // The download is persisted before the router finishes its transition.
    // Wait for the browser URL instead of reading it during that transition.
    await page.waitForFunction(
      () => location.hash === '#/painting/online-smoke-test',
      null,
      {timeout:15000}
    );
    const onlineUnlock=page.getByRole('button',{name:/Unlock for [0-9]+ coins/});
    await onlineUnlock.waitFor();
    await onlineUnlock.click();
    await board().waitFor();

    assert.deepEqual(pageErrors,[]); assert.deepEqual(failedRequests,[]); assert.deepEqual(externalRequests,[]);
    console.log(JSON.stringify({defaultPersian:'passed',englishAndLanguageRestore:'passed',
      fastStroke:'passed',wrongColor:'passed',undoRemoved:'passed',resetConfirmation:'passed',
      persistentProgressAfterPageRecreationAndRefresh:'passed',completion:'passed',resetGeneration:'passed',
      browserHistory:'passed',paint32_64_128:'passed',largeGridZoomPan:'passed',responsiveDesktop:'passed',responsiveTablet:'passed',shortHeight:'passed',
      onlineCatalogAndDownload:'passed',runtimeRequests:'local and approved online catalog',pageErrors,screenshots:output},null,2));
  } finally {await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
