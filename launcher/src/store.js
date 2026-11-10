// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted state ownership pattern from Recompia; our portable command contract.
import { request, on, native } from './bridge.js';
import { confirm, toast, errText } from './ui.js';
const subscribers=new Set();
export const store={
  state:null,
  subscribe(fn){subscribers.add(fn);return ()=>subscribers.delete(fn);},
  set(state){
    if (!state || (this.state && state.revision<this.state.revision)) return;
    this.state=state;
    document.documentElement.dataset.accent=state.accent;
    for(const fn of [...subscribers]) {try{fn(state);}catch(e){console.error(e);}}
  },
  async start(){
    await on('state',s=>this.set(s));
    await on('close-blocked',message=>toast(message,'error'));
    await on('backend-exit',()=>{if(!this.exiting)toast('Launcher backend stopped. See .local/launcher-error.log.','error');});
    await on('update-ready',async()=>{
      try{this.exiting=true;await native('lifecycle',{action:'finalize_update'});}
      catch(e){this.exiting=false;toast(errText(e),'error');}
    });
    this.set(await request('state'));
  },
  async perform(action,args={}){
    try{
      if(action==='restore'){
        if(!await confirm({title:'Restore previous version?',body:'Restore the previous launcher files and restart. Your game files and saves are kept.',ok:'Restore'}))return;
        this.exiting=true;await native('lifecycle',{action:'restore'});return;
      }
      if(action==='install_update' && !await confirm({title:`Install version ${this.state.update?.version}?`,body:'The launcher will restart. Your game files, settings and saves are kept.',ok:'Install update'}))return;
      this.set(await request(action,args));
      if(action==='save_option')toast('Saved. Applies on the next game launch.','ok');
    }catch(e){this.exiting=false;toast(errText(e),'error');throw e;}
  }
};
