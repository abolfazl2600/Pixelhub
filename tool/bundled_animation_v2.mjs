#!/usr/bin/env node
// Rebuild expressive animation companions from the original immutable pixel levels.
// Usage: node tool/bundled_animation_v2.mjs --write | --check
import {readFileSync, writeFileSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const SUBJECTS = ['sunflower','butterfly','rocket','fish','bird','bee','sailboat',
  'umbrella','tree','cat','tulip','ufo','diamond','moon'];

function makeAnimation(level) {
  const w=level.width,h=level.height,src=level.cells;
  const count=24, duration=125, frames=[];
  const index=(x,y)=>y*w+x;
  for(let t=0;t<count;t++){
    const cells=src.slice(),p=2*Math.PI*t/(count-1),s=Math.sin(p),f=Math.sin(2*p);
    const set=(x,y,color,onlyEmpty=false)=>{
      if(x>=0&&x<w&&y>=0&&y<h&&(!onlyEmpty||src[index(x,y)]===0))cells[index(x,y)]=color;
    };
    // Each layer is reconstructed from the original still frame, not from a
    // previous pose. The selected old footprint is cleared before redrawing.
    const move=(predicate,transform)=>{
      const pixels=[],owned=new Set();
      for(let y=0;y<h;y++)for(let x=0;x<w;x++){
        const i=index(x,y),color=src[i];
        if(color!==0&&predicate(x,y,color)){pixels.push([x,y,color]);owned.add(i);}
      }
      for(const [x,y] of pixels)cells[index(x,y)]=0;
      for(const [x,y,color] of pixels){
        const [xx,yy]=transform(x,y),dx=Math.round(xx),dy=Math.round(yy);
        if(dx<0||dx>=w||dy<0||dy>=h)continue;
        const dest=index(dx,dy);
        if(src[dest]!==0&&!owned.has(dest))continue; // preserve static details
        cells[dest]=color;
      }
    };
    const glint=(x,y,c)=>{
      if(x>=0&&x<w&&y>=0&&y<h&&src[index(x,y)]!==0)cells[index(x,y)]=c;
    };
    // Keep first/last keyframes identical to the level image for clean loops.
    if(t!==0&&t!==count-1){
      switch(level.levelId){
        case 'sunflower':{
          const dx=Math.round(1.6*s),dy=Math.round(.65*Math.sin(p+1));
          move((x,y,c)=>y>=2&&y<=9,(x,y)=>[x+dx,y+dy]);
          move((x,y,c)=>y>=10&&y<=14,(x,y)=>[x+Math.round(dx*(14-y)/5),y]);
          for(let k=0;k<4;k++){
            const x=4+k*2,y=4+k%3;
            if(src[index(x,y)]===2&&(t+k*3)%7<3)glint(x,y,1);
          }
          break;
        }
        case 'butterfly':{
          const span=1-.27*Math.abs(Math.sin(2*p));
          move((x,y,c)=>(x<15||x>16)&&y>=3&&y<=26,
            (x,y)=>[x<15?15+(x-15)*span:16+(x-16)*span,
                    y+Math.round(.75*Math.sin(2*p+(y>16?.8:0)))]);
          break;
        }
        case 'rocket':{
          const lift=Math.round(-1.5*Math.max(0,s)),jitter=Math.round(.65*Math.sin(3*p));
          move((x,y,c)=>y>=2&&y<=10,(x,y)=>[x+jitter,y+lift]);
          for(let y=11;y<=15;y++)for(let x=4;x<=11;x++)
            if(src[index(x,y)]===3)cells[index(x,y)]=0;
          const length=2+Math.round(2*(.5+.5*Math.sin(3*p)));
          for(let k=0;k<length;k++){
            const y=11+k-lift,x=7+Math.round(Math.sin(p*4+k)*.7);
            set(x,y,3,true);set(x+1,y,k%2===0?3:2,true);
            if(k===length-1)set(x,y+1,2,true);
          }
          if(t%4<2){set(4,14,3,true);set(11,15,2,true);}
          break;
        }
        case 'fish':{
          const dx=Math.round(1.5*s),dy=Math.round(Math.sin(p+.5));
          move((x,y,c)=>x>=9&&x<=26&&y>=9&&y<=22,(x,y)=>[x+dx,y+dy]);
          move((x,y,c)=>x>26&&y>=9&&y<=22,
            (x,y)=>[x+dx+Math.round(1.5*f),y+dy]);
          for(let k=0;k<3;k++)set(3+2*k,9-(t+k*4)%9,3,true);
          break;
        }
        case 'bird':{
          const bob=Math.round(.85*s);
          move((x,y,c)=>x>=15&&y>=7&&y<=23,(x,y)=>[x,y+bob]);
          move((x,y,c)=>x>=5&&x<15&&y>=12&&y<=21,
            (x,y)=>[x-Math.round(.6*f),y-Math.round(1.5*Math.max(0,f))]);
          move((x,y,c)=>x<5&&y>=10&&y<=17,(x,y)=>[x+Math.round(s),y]);
          break;
        }
        case 'bee':{
          const hover=Math.round(1.2*s);
          move((x,y,c)=>y>=13&&y<=23,(x,y)=>[x,y+hover]);
          move((x,y,c)=>c===3&&y>=6&&y<13,
            (x,y)=>[x+(x<16?-1:1)*Math.round(Math.abs(f)),
                    y-Math.round(1.3*Math.max(0,f))+hover]);
          break;
        }
        case 'sailboat':{
          const bob=Math.round(Math.max(0,Math.sin(p+.4))),wind=Math.round(s);
          move((x,y,c)=>y>=8&&y<=19&&x!==15,
            (x,y)=>[x+wind*Math.max(0,(20-y)/15),y]);
          move((x,y,c)=>y>=21&&y<=26,(x,y)=>[x,y+bob]);
          move((x,y,c)=>y>=28&&c===4,(x,y)=>[x+Math.round(2*s),y]);
          break;
        }
        case 'umbrella':{
          const lean=Math.round(1.4*s);
          move((x,y,c)=>y>=2&&y<=17,(x,y)=>[x+lean,y]);
          move((x,y,c)=>y>=18&&y<=27,
            (x,y)=>[x+Math.round(lean*(27-y)/10),y]);
          for(let k=0;k<6;k++){
            const x=2+k*5,y=1+(t*2+k*7)%28;
            if(y>=2&&y<28&&src[index(x,y)]===0)set(x,y,7,true);
            if(y>=3&&y<28&&src[index(x,y-1)]===0)set(x,y-1,7,true);
          }
          break;
        }
        case 'tree':{
          move((x,y,c)=>y<=26&&c>=4&&c<=11,
            (x,y)=>[x+Math.round(Math.sin(p+x/9)*(26-y)/18),y]);
          for(let k=0;k<8;k++){
            const x=6+(k*3)%20,y=2+(k*5)%19,i=index(x,y);
            if(src[i]>=4&&src[i]<=7&&(t+k*3)%9<=2)glint(x,y,8);
          }
          break;
        }
        case 'cat':{
          const ear=Math.round(s);
          move((x,y,c)=>y>=12&&y<=19&&
            ((x>=16&&x<28)||(x>=36&&x<48)),
            (x,y)=>[x+(x<32?-ear:ear),y]);
          if((t>=6&&t<=8)||(t>=17&&t<=18)){
            for(let y=28;y<=31;y++)for(let x of [24,25,26,27,36,37,38,39])
              if(src[index(x,y)]===3)cells[index(x,y)]=2;
            for(const x of [24,25,26,27,36,37,38,39])set(x,30,3);
          }
          break;
        }
        case 'tulip':{
          const dx=Math.round(1.5*s);
          move((x,y,c)=>c===1&&y>=6&&y<=15,
            (x,y)=>[x+dx,y+Math.round(.6*Math.sin(p+.4))]);
          move((x,y,c)=>c===2&&y>=16&&y<=26,
            (x,y)=>[x+Math.round(dx*(26-y)/11),y]);
          break;
        }
        case 'ufo':{
          const hover=Math.round(1.6*s);
          move((x,y,c)=>y>=7&&y<=20,(x,y)=>[x,y+hover]);
          move((x,y,c)=>c===3&&y>=21,
            (x,y)=>[16+(x-16)*(1+.18*Math.sin(p)),y]);
          for(const x of [8,15,22]){
            const y=17+hover;
            if(src[index(x,17)]===2&&t%6<3)set(x,y,3);
          }
          break;
        }
        case 'diamond':{
          const head=(t*1.4+3)%35;
          for(let y=5;y<29;y++)for(let x=3;x<29;x++){
            const c=src[index(x,y)];
            if(c===0)continue;
            const d=Math.abs(x+.42*y-head);
            if(d<.9&&c!==6)glint(x,y,6);
            else if(d<2.1&&c>=1&&c<=5)glint(x,y,7);
          }
          break;
        }
        case 'moon':{
          const dx=Math.round(s);
          move((x,y,c)=>y>=2&&y<=27,(x,y)=>[x+dx,y]);
          const points=[[3,4],[26,6],[27,15],[5,25]];
          for(let k=0;k<points.length;k++){
            const [x,y]=points[k];
            if(t%8>=k*2&&t%8<k*2+4){
              set(x,y,1,true);if(t%8===k*2+2)set(x+1,y,2,true);
            }
          }
          break;
        }
        default:throw Error('Unknown subject: '+level.levelId);
      }
    }
    const changes=[];
    for(let i=0;i<src.length;i++)
      if(cells[i]!==src[i])changes.push([i,cells[i]]);
    frames.push({changes});
  }
  return {schemaVersion:1,levelId:level.levelId,
    levelVersion:level.levelVersion,levelChecksum:level.checksum,
    frameDurationMs:duration,frames};
}

// CLI_ENTRY
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv.includes('--write')&&!process.argv.includes('--check'))
  throw Error('Use --write to rebuild or --check to verify companions');
const catalog=JSON.parse(readFileSync(resolve(root,'apps/game/assets/animations/catalog.json'),'utf8'));
for(const id of SUBJECTS){
  const name=id==='sunflower'?'sunflower-v2.json':id+'.json';
  const level=JSON.parse(readFileSync(resolve(root,'apps/game/assets/levels',name),'utf8'));
  const path=resolve(root,'apps/game/assets/animations',catalog[id]);
  const content=JSON.stringify(makeAnimation(level));
  if(process.argv.includes('--write'))writeFileSync(path,content);
  else if(readFileSync(path,'utf8')!==content)
    throw Error('Companion has stale frames: '+id);
}
console.log('Verified '+SUBJECTS.length+' expressive offline animations.');
