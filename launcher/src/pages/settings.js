// SPDX-License-Identifier: GPL-3.0-or-later
// Recompia's controls and grouping, connected to the existing N2O preference file.
import './settings.css';
import { esc,icon } from '../ui.js';
import { store } from '../store.js';
const tabs=['Display','Audio','Controls','Storage','About'];
const row=(label,control,note='')=>`<div class="row-item"><div class="row-label">${label}${note?`<p class="faint">${note}</p>`:''}</div><div class="row-control">${control}</div></div>`;
const group=(title,content)=>`<section class="group"><h2 class="group-title">${title}</h2><div class="group-body glass">${content}</div></section>`;
const button=(label,target)=>`<button class="btn sm" data-open="${target}">${label}${icon('arrow-up-right')}</button>`;
const select=(key,label,values)=>`<span class="select"><select data-option="${key}" aria-label="${label}">${values.map(([v,name])=>`<option value="${v}">${name}</option>`).join('')}</select>${icon('chevron-down')}</span>`;
const slider=(key,label,min,max,step)=>`<span class="slider"><input type="range" data-option="${key}" aria-label="${label}" min="${min}" max="${max}" step="${step}" /><output></output></span>`;
export function render(el,ctx){
  el.innerHTML=`<div class="page set"><header class="set-head"><h1>Settings</h1><span class="faint">Saved automatically</span></header><div class="set-pills"><div class="seg" role="tablist" aria-label="Settings sections">${tabs.map(t=>`<label><input type="radio" name="settings-tab" role="tab" value="${t}" aria-controls="panel-${t}" /><span>${t}</span></label>`).join('')}</div></div><div class="set-body"></div></div>`;
  const body=el.querySelector('.set-body');let tab='Display';
  function content(){
    const s=store.state;
    if(tab==='Display')return group('Picture',row('Window mode',select('video_mode','Window mode',[[0,'Windowed'],[1,'Borderless'],[2,'Fullscreen']]))+row('HUD scale',select('hud_scale','HUD scale',[[0,'Auto'],[2,'2×'],[3,'3×'],[4,'4×'],[6,'6×']]),'Auto follows the window, with a 2× minimum.'))+group('Rendering',row('Scene resolution',slider('render_percent','Scene resolution',25,200,5),'Scale the 3D scene; menus and text stay sharp.'))+'<p class="faint">Changes apply on the next game launch. While playing, use the in-game Video menu.</p>';
    if(tab==='Audio')return group('Volume',row('Master volume',slider('master_volume','Master volume',0,100,1)))+'<p class="faint">Music, ambient sound and effects have separate controls in the game’s Audio menu. Changes here apply on the next launch.</p>';
    if(tab==='Controls')return group('Keyboard',(s?.keyboard||[]).map(([action,key])=>row(esc(action),`<kbd class="set-key">${esc(key)}</kbd>`)).join(''))+`<div class="cluster">${button('Open keyboard bindings','keybinds.ini')}</div><p class="faint">Custom bindings are preserved. Gamepads are detected automatically; use the in-game Controls menu to select a configuration.</p>`;
    if(tab==='Storage')return group('Your game',row('Source disc','<span class="set-disc path selectable"></span>')+row('Game disc','<button class="btn sm" data-act="choose">Choose disc…</button>')+row('Save data',button('Open saves','saves'))+row('Setup details',button('Open setup log','setup.log')))+group('Asset folders',row('Original assets & music','<button class="btn sm" data-act="assets" id="assets-button">Extract asset folders</button>','The game continues to read your original disc.'));
    return group('Nitrogen Squared',row('Version',`<span class="set-value">${esc(s?.version||'')} · ${esc(s?.platform||'')}</span>`)+row('Accent colour',`<span class="select"><select id="accent" aria-label="Accent colour">${['Cyan','Violet','Amber'].map(v=>`<option>${v}</option>`).join('')}</select>${icon('chevron-down')}</span>`)+row('Project',button('Open GitHub','project'))+row('Releases',button('Published releases','releases')))+group('Credits & license',row('Launcher interface',button('Dittobyte / Recompia','recompia'),'Adapted from Recompia. Inter typography and Lucide icons.')+row('GPL-3.0-or-later','<span class="faint">Source and notices included</span>','Copyright © 2026 N2O Recomp contributors. See LICENSE, COPYRIGHT and THIRD_PARTY.md in the included source.'));
  }
  function show(name){
    tab=name;body.id='panel-'+tab;body.setAttribute('role','tabpanel');body.innerHTML=content();
    for(const input of el.querySelectorAll('[name="settings-tab"]')){input.checked=input.value===tab;input.setAttribute('aria-selected',String(input.checked));}
    draw(store.state);
  }
  function draw(s){
    const blocked=!s||s.busy||s.recovery;
    for(const control of body.querySelectorAll('button,select,input'))control.disabled=blocked;
    for(const input of body.querySelectorAll('[data-option]')){
      if(document.activeElement!==input)input.value=s?.options[input.dataset.option]??input.min;
      if(input.type==='range')showRange(input);
    }
    const disc=body.querySelector('.set-disc');if(disc)disc.textContent=s?.disc||'No disc selected';
    const assets=body.querySelector('#assets-button');if(assets){assets.disabled=blocked||!s?.imported;assets.textContent=s?.extracted?'Open asset folders':'Extract asset folders';}
    const accent=body.querySelector('#accent');if(accent)accent.value=s?.accent||'Cyan';
  }
  function showRange(input){input.style.setProperty('--pct',100*(input.value-input.min)/(input.max-input.min)+'%');input.nextElementSibling.textContent=input.value+'%';}
  el.addEventListener('input',e=>{if(e.target.matches('input[type="range"]'))showRange(e.target);});
  el.addEventListener('change',async e=>{
    const input=e.target;
    if(input.name==='settings-tab'){show(input.value);return;}
    try{
      if(input.dataset.option)await store.perform('save_option',{key:input.dataset.option,value:Number(input.value)});
      else if(input.id==='accent')await store.perform('accent',{value:input.value});
    }catch{input.blur();draw(store.state);}
  });
  el.addEventListener('click',e=>{
    const button=e.target.closest('button');if(button?.dataset.open)store.perform('open',{target:button.dataset.open}).catch(()=>{});
    else if(button?.dataset.act)store.perform(button.dataset.act).catch(()=>{});
  });
  ctx.on(draw);show(tab);
}
