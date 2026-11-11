// GPL-3.0-or-later. Development-only synthetic adapter; Vite removes it from releases.
const handlers=new Map();let callbackId=0;const callbacks=new Map();
const state={revision:1,version:'0.2.2',platform:'Windows x64',busy:false,phase:'idle',title:'Choose your game disc',detail:'Your game, settings and saves stay in this folder.',percent:null,error:null,recovery:false,disc:null,prepared:false,imported:false,extracted:false,accent:'Cyan',options:{video_mode:0,hud_scale:0,render_percent:100,master_volume:100},keyboard:[['Move / navigate','W A S D'],['Select / main weapon','Enter'],['Back / shield','Backspace'],['Jump','Space']],releases:[{version:'0.2.2',title:'Nitrogen Squared 0.2.2',date:'2026-11-09',summary:'A smoother home for your next run.',body:'A Tauri launcher adapted from Recompia.\n\nYour game and saves stay local.',current:true}],update:null};
function emit(event,payload){for(const id of handlers.get(event)||[])callbacks.get(id)?.({event,payload});}
window.__N2_MOCK__={state,emit};
window.__TAURI_INTERNALS__={
  transformCallback(fn,once=false){const id=++callbackId;callbacks.set(id,once?(...args)=>{callbacks.delete(id);fn(...args);}:fn);return id;},
  unregisterCallback(id){callbacks.delete(id);},
  metadata:{currentWindow:{label:'main'},currentWebview:{label:'main'}},
  async invoke(cmd,args={}){
    if(cmd==='plugin:event|listen'){const ids=handlers.get(args.event)||[];ids.push(args.handler);handlers.set(args.event,ids);return args.handler;}
    if(cmd==='plugin:event|unlisten')return;
    if(cmd==='plugin:window|is_maximized')return false;
    if(cmd.startsWith('plugin:window|'))return;
    if(cmd==='host_info')return {testing:false};
    if(cmd==='choose_disc'){state.disc='C:\\Games\\N2O.cue';state.imported=true;state.revision++;emit('state',{...state});return structuredClone(state);}
    if(cmd==='lifecycle')return;
    if(cmd==='request'){
      if(args.command==='save_option')state.options[args.args.key]=args.args.value;
      if(args.command==='accent')state.accent=args.args.value;
      if(args.command==='play'){state.busy=true;state.phase='build';state.title='Building game';state.detail='42 of 100 · Building CXX object native/movie_player.cpp';state.workers='12 of 16 logical CPUs';state.elapsed=65;state.percent=42;}
      if(args.command==='stop'){state.busy=false;state.phase='idle';state.percent=null;state.title='Setup stopped';}
      if(args.command==='check_update')state.title='You have the latest release.';
      state.revision++;emit('state',structuredClone(state));return structuredClone(state);
    }
    throw Error('Unsupported mock '+cmd);
  }
};
