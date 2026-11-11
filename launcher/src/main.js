/* Navigation lifecycle adapted from Dittobyte/Recompia main.js (56fca2b).
 * Modified 2026-11-09 for Nitrogen Squared. GPL-3.0-or-later. */
import '@fontsource-variable/inter/opsz.css';
import './theme.css';import './layout.css';import './components.css';import './nitrogen.css';
import { getCurrentWindow,LogicalSize } from '@tauri-apps/api/window';
import logoUrl from '../assets/logo.png';import tunnelUrl from '../assets/tunnel.png';
import {icon,esc,toast} from './ui.js';import {store} from './store.js';import {native} from './bridge.js';
import * as home from './pages/home.js';import * as news from './pages/news.js';import * as settings from './pages/settings.js';
const pages={home:{mod:home,label:'Home',icon:'house'},news:{mod:news,label:"What's New",icon:'newspaper'},settings:{mod:settings,label:'Settings',icon:'settings'}};
const nav=document.getElementById('nav'),view=document.getElementById('view');let current,token=0,leaving=[];
nav.innerHTML=`<div class="brand" data-tauri-drag-region><img class="brand-logo nitrogen-brand" src="${logoUrl}" alt="Nitrogen Squared" /></div>${Object.entries(pages).map(([id,p])=>`<button class="nav-item" data-page="${id}" aria-label="${p.label}">${icon(p.icon)}<span class="nav-label">${p.label}</span><span class="nav-tip" aria-hidden="true">${p.label}</span></button>`).join('')}<div class="nav-spacer"></div><button class="task-pill" id="task-pill" hidden>${icon('loader-circle','spin')}<span class="task-name clip"></span><span class="task-pct"></span><span class="task-track"><span class="task-fill"></span></span></button><div class="build-label"><span id="version"></span><span class="test-badge">DEV CANDIDATE</span></div>`;
function chrome(s){
  for(const button of nav.querySelectorAll('[data-page]')){if(button.dataset.page===current)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');}
  document.getElementById('version').textContent=s?'v'+s.version:'';
  const pill=document.getElementById('task-pill');pill.hidden=!s?.busy;if(pill.hidden)return;
  pill.querySelector('.task-name').textContent=s.title;pill.querySelector('.task-pct').textContent=s.percent==null?'':s.percent+'%';
  pill.title=s.detail||s.title;pill.setAttribute('aria-label',s.title);pill.style.setProperty('--pct',(s.percent||0)+'%');pill.toggleAttribute('data-indeterminate',s.percent==null);
}
async function go(page,opts={}){
  if(!pages[page])return;const id=++token;leaving.forEach(fn=>fn());leaving=[];current=page;
  document.body.dataset.art=page==='home'?'sharp':'soft';chrome(store.state);
  const host=document.createElement('div');host.className='page-host';
  const ctx={...opts,go,on(fn){const off=store.subscribe(fn);leaving.push(off);return off;},cleanup(fn){leaving.push(fn);}};
  try{await pages[page].mod.render(host,ctx);}catch(e){host.innerHTML=`<div class="page"><div class="banner danger">${esc(e.message)}</div></div>`;}
  if(id!==token)return;host.classList.add('entering');
  host.addEventListener('animationend',e=>{if(e.target===host)host.classList.remove('entering');});
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)host.classList.remove('entering');
  view.replaceChildren(host);view.scrollTop=0;view.focus({preventScroll:true});
}
nav.addEventListener('click',e=>{const page=e.target.closest('[data-page]')?.dataset.page;if(page&&page!==current)go(page);if(e.target.closest('#task-pill'))go('home');});
function windowButtons(){
  const win=getCurrentWindow();
  const host=document.getElementById('winbtns');
  host.innerHTML=`<button class="win-btn" id="win-min" aria-label="Minimise">${icon('minus')}</button><button class="win-btn" id="win-max" aria-label="Maximise">${icon('square')}</button><button class="win-btn close" id="win-close" aria-label="Close">${icon('x')}</button>`;
  document.getElementById('win-min').onclick=()=>win.minimize().catch(console.warn);
  document.getElementById('win-max').onclick=()=>win.toggleMaximize().catch(console.warn);
  document.getElementById('win-close').onclick=()=>win.close().catch(console.warn);
  const sync=()=>win.isMaximized().then(on=>{const b=document.getElementById('win-max');b.innerHTML=icon(on?'copy':'square');b.setAttribute('aria-label',on?'Restore':'Maximise');});
  win.onResized(sync).catch(console.warn);sync().catch(console.warn);
}
const frame=()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
async function smoke(){
  await document.fonts.ready;const art=new Image();art.src=tunnelUrl;await art.decode();
  let layout=true;const navigation=[];const win=getCurrentWindow();
  for(const [width,height] of [[760,500],[1100,700]]){
    await win.setSize(new LogicalSize(width,height));await frame();
    for(const name of Object.keys(pages)){
      await go(name);await frame();navigation.push(name);
      if(view.scrollWidth>view.clientWidth+1||document.documentElement.scrollWidth>innerWidth+1)layout=false;
      if(name==='settings')for(const radio of view.querySelectorAll('[name="settings-tab"]')){radio.click();await frame();if(view.scrollWidth>view.clientWidth+1)layout=false;}
    }
  }
  await go('home');await frame();await view.querySelector('.home-logo').decode();
  await native('lifecycle',{action:'self_test',ui:{navigation,layout,artwork:art.naturalWidth===1536,progress:!!document.getElementById('task-pill'),settings:['Display','Audio','Controls','Storage','About']}});
}
windowButtons();store.subscribe(chrome);chrome(null);go('home');
try{await store.start();const info=await native('host_info');document.querySelector('.test-badge').hidden=info.channel==='stable';if(info.testing)await smoke();}
catch(e){toast(e.message||String(e),'error');const detail=view.querySelector('#detail');if(detail){detail.hidden=false;detail.textContent='The launcher could not start. '+(e.message||String(e));}}
