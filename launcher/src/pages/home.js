/* Adapted from Dittobyte/Recompia home.js, commit 56fca2b30cc900971b8871eaa1b9b7343c91e16a.
 * Modified 2026-11-09 for Nitrogen Squared. GPL-3.0-or-later; see ../../UPSTREAM.md. */
import './home.css';
import logoUrl from '../../assets/logo.png';
import { esc, icon } from '../ui.js';
import { store } from '../store.js';
import { primaryAction,canStop } from '../action.js';
const patch=(node,html)=>{if(node.dataset.html!==html){node.innerHTML=html;node.dataset.html=html;}};
export function render(el,ctx){
  el.innerHTML=`<div class="page home"><div class="home-hero">
    <p class="eyebrow">N2O: NITROUS OXIDE · NATIVE RECOMPILATION</p>
    <h1 class="display"><img class="home-logo" src="${logoUrl}" alt="Nitrogen Squared" /></h1>
    <p class="home-tagline">Return to the tunnel.</p>
    <div class="home-actions"><button class="btn primary big" id="primary"></button><button class="btn big on-art" id="update">${icon('download')}Check updates</button></div>
    <p class="home-detail" id="detail"></p>
    <div class="home-task glass strong" id="task" hidden><span class="msg clip" id="task-msg"></span><span class="pct num" id="task-pct"></span><span class="task-detail" id="task-detail"></span><progress max="100" id="task-bar" aria-label="Current stage progress"></progress><span class="task-meta num" id="task-meta"></span><button class="btn sm" id="task-stop">${icon('square')}Stop</button></div>
    <div class="home-notices" id="notices"></div>
  </div><section class="home-news" id="news" aria-label="Newest releases"></section></div>`;
  const part=id=>el.querySelector('#'+id);
  function clock(s){
    const seconds=Math.max(0,Math.floor((s?.elapsed||0)+(s?.busy?(performance.now()-(store.receivedAt||performance.now()))/1000:0)));
    const elapsed=`${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')} elapsed`;
    part('task-meta').textContent=[s?.phase!=='running'?s?.workers:'',elapsed].filter(Boolean).join(' · ');
  }
  function draw(s){
    const action=primaryAction(s),b=part('primary');
    patch(b,icon(action.icon,action.disabled&&s?.phase!=='running'?'spin':'')+esc(action.label));
    b.disabled=action.disabled;b.dataset.act=action.action||'';
    const update=part('update');update.disabled=!s||s.busy||s.recovery;
    update.dataset.act=s?.update?'install_update':'check_update';
    patch(update,icon('download')+(s?.update?`Update to ${esc(s.update.version)}`:'Check updates'));
    part('detail').textContent=s?.error||(!s?.busy?s?.detail:'')||'';
    part('detail').hidden=!part('detail').textContent;
    part('task').hidden=!s?.busy;
    part('task-msg').textContent=s?.title||'';part('task-msg').title=s?.detail||'';
    part('task-detail').textContent=s?.detail||'';
    clock(s);
    part('task-pct').textContent=s?.percent==null?'':s.percent+'%';
    if(s?.percent==null)part('task-bar').removeAttribute('value');else part('task-bar').value=s.percent;
    part('task-stop').hidden=!canStop(s);part('task-stop').dataset.act='stop';
    patch(part('news'),(s?.releases||[]).slice(0,3).map(r=>`<button class="release glass hover" data-version="${esc(r.version)}"><span class="release-head"><span class="release-title"><strong>${esc(r.version)}</strong>${r.current?' <span class="note-mark">This build</span>':''}</span><time>${esc(r.date)}</time></span><span class="release-line">${esc(r.summary)}</span></button>`).join(''));
  }
  el.addEventListener('click',e=>{
    const button=e.target.closest('[data-act]');if(button?.dataset.act)store.perform(button.dataset.act).catch(()=>{});
    const version=e.target.closest('[data-version]')?.dataset.version;if(version)ctx.go('news',{version});
  });
  ctx.on(draw);draw(store.state);
  const timer=setInterval(()=>{if(store.state?.busy)clock(store.state);},1000);
  ctx.cleanup(()=>clearInterval(timer));
}
