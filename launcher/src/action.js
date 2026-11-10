// SPDX-License-Identifier: GPL-3.0-or-later
// Recompia's single primary-action pattern, mapped to our portable state.
export function primaryAction(s){
  if(!s)return {label:'Loading',icon:'loader-circle',disabled:true};
  if(s.recovery)return {label:'Restore previous version',icon:'rotate-ccw',action:'restore',disabled:s.busy};
  if(s.busy)return {label:s.phase==='running'?'Running':s.phase==='update'?'Updating':'Setting up',icon:s.phase==='running'?'gamepad-2':'loader-circle',disabled:true};
  if(!s.disc)return {label:'Choose game disc',icon:'folder-open',action:'choose',disabled:false};
  return {label:s.prepared?'Play':'Prepare & play',icon:'play',action:'play',disabled:false};
}
export const canStop=s=>!!s?.busy&&!['running','restart'].includes(s.phase);
