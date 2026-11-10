// GPL-3.0-or-later. Recompia split-pane styling, portable cached/bundled notes.
import './news.css';
import { esc } from '../ui.js';
import { store } from '../store.js';
export function render(el,ctx){
  el.innerHTML='<div class="page news-page"><section class="news glass"><nav class="note-list" aria-label="Releases"></nav><article class="note-detail"><h1></h1><p class="faint note-date"></p><div class="notes-body selectable"></div></article></section></div>';
  let selected=ctx.version,prior='';
  const list=el.querySelector('.note-list');
  function select(version){
    selected=version;const r=store.state?.releases.find(r=>r.version===selected);if(!r)return;
    for(const button of list.querySelectorAll('button')){if(button.dataset.version===version)button.setAttribute('aria-current','true');else button.removeAttribute('aria-current');}
    el.querySelector('h1').textContent=r.title;el.querySelector('.note-date').textContent=(r.current?'Included in this build · ':'')+r.date;
    // Notes are untrusted data. Keep remote HTML and scripts as literal text.
    el.querySelector('.notes-body').textContent=r.body;
    el.querySelector('.note-detail').scrollTop=0;
  }
  function draw(s){
    const next=JSON.stringify(s?.releases||[]);if(prior===next)return;prior=next;
    list.innerHTML=(s?.releases||[]).map(r=>`<button class="note-item" data-version="${esc(r.version)}"><strong>Version ${esc(r.version)}</strong><span class="faint">${esc(r.current?'This build':r.date)}</span></button>`).join('');
    select(s?.releases.some(r=>r.version===selected)?selected:s?.releases[0]?.version);
  }
  list.addEventListener('click',e=>{const version=e.target.closest('[data-version]')?.dataset.version;if(version)select(version);});
  ctx.on(draw);draw(store.state);
}
