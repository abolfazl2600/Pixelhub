const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

async function main() {
  const base = process.env.PIXELHUB_BASE_URL || 'http://127.0.0.1:8080/Pixelhub/';
  const output = process.env.PIXELHUB_SMOKE_OUTPUT || path.join(__dirname, 'artifacts');
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
      p.on('request', r => { const u=new URL(r.url()); if(u.protocol.startsWith('http') && u.origin!==new URL(base).origin) externalRequests.push(u.origin); });
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
      const vp=page.viewportSize(), w=Math.min(vp.width,430);
      await page.mouse.move((vp.width-w)/2+w-4, Math.min(vp.height-40,300));
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
    async function point(x,y) {
      const b=await board().boundingBox(); assert(b && b.y>=0 && b.y+b.height<=page.viewportSize().height);
      return {x:b.x+b.width*(x+.5)/16, y:b.y+b.height*(y+.5)/16};
    }
    async function line(x1,y,x2) {
      const a=await point(x1,y),b=await point(x2,y);
      await page.mouse.move(a.x,a.y); await page.mouse.down();
      if(x1!==x2)await page.mouse.move(b.x,b.y); await page.mouse.up();
    }

    console.log('Browser: default language and home');
    await page.goto(base); await ready();
    await page.getByRole('button',{name:'English',exact:true}).waitFor();
    await page.screenshot({path:path.join(output,'home-fa.png')});
    await page.getByRole('button',{name:'English',exact:true}).click();
    await page.getByRole('button',{name:'فارسی',exact:true}).waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.lang),'en');
    await page.screenshot({path:path.join(output,'home-en.png')});
    console.log('Browser: painting and autosave');
    await start().click(); await board().waitFor();
    assert.equal(new URL(page.url()).hash,'#/painting/sunflower');
    await line(0,0,15); await saved(16);
    await page.getByRole('button',{name:'Undo',exact:true}).click(); await saved(0);
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
    await page.getByRole('button',{name:'فارسی',exact:true}).waitFor();
    await page.reload(); await ready(); await board().waitFor(); await saved(16);
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

    // Paint a real cell in each required size, using actual browser storage.
    for (const id of ['rainbow','gem','planet']) {
      await page.goto(base+'#/painting/'+id); await ready(); await board().waitFor();
      const current=await board().boundingBox();
      const dimension={rainbow:32,gem:64,planet:128}[id];
      await page.mouse.click(current.x+current.width/(dimension*2),current.y+current.height/(dimension*2));
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
    for(let n=0;n<5;n++) await page.getByRole('button',{name:'Zoom in',exact:true}).click();
    await page.getByRole('button',{name:'Move / zoom',exact:true}).click();
    const b=await board().boundingBox();
    await page.mouse.move(b.x+b.width*.5,b.y+b.height*.5); await page.mouse.down();
    await page.mouse.move(b.x+b.width*.65,b.y+b.height*.6,{steps:10}); await page.mouse.up();
    await page.screenshot({path:path.join(output,'planet-zoom.png')});
    await page.setViewportSize({width:1440,height:900}); await page.goto(base); await ready();
    const action=await start().boundingBox();
    assert(action && action.x>=(1440-430)/2 && action.x+action.width<=(1440+430)/2);
    await page.screenshot({path:path.join(output,'home-desktop.png')});
    await page.setViewportSize({width:800,height:360}); await page.goto(base); await ready();
    await start().click(); await back().click(); await start().waitFor();
    await page.getByRole('button',{name:'فارسی',exact:true}).click(); await page.reload(); await ready();
    await page.getByRole('button',{name:'English',exact:true}).waitFor();

    assert.deepEqual(pageErrors,[]); assert.deepEqual(failedRequests,[]); assert.deepEqual(externalRequests,[]);
    console.log(JSON.stringify({defaultPersian:'passed',englishAndLanguageRestore:'passed',
      fastStroke:'passed',wrongColor:'passed',undo:'passed',resetConfirmation:'passed',
      persistentProgressAfterPageRecreationAndRefresh:'passed',completion:'passed',resetGeneration:'passed',
      browserHistory:'passed',paint32_64_128:'passed',largeGridZoomPan:'passed',desktopFrame:'passed',shortHeight:'passed',
      runtimeRequests:'local only',pageErrors,screenshots:output},null,2));
  } finally {await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
