// GPL-3.0-or-later. User-facing readiness and cancellation policy.
import {test} from 'node:test';import assert from 'node:assert/strict';
import {primaryAction,canStop} from '../src/action.js';
test('new import, prepared game, interrupted update and running game choose appropriate actions',()=>{
  assert.equal(primaryAction(null).disabled,true);
  assert.equal(primaryAction({disc:null}).action,'choose');
  assert.equal(primaryAction({disc:'local.cue',prepared:false}).label,'Prepare & play');
  assert.equal(primaryAction({disc:'local.cue',prepared:true}).label,'Play');
  assert.equal(primaryAction({recovery:true,busy:false}).action,'restore');
  assert.equal(primaryAction({busy:true,phase:'running'}).disabled,true);
});
test('stopping is available only before running or committed update restart',()=>{
  assert.equal(canStop({busy:true,phase:'setup'}),true);
  assert.equal(canStop({busy:true,phase:'update'}),true);
  assert.equal(canStop({busy:true,phase:'running'}),false);
  assert.equal(canStop({busy:true,phase:'restart'}),false);
  assert.equal(canStop({busy:false,phase:'idle'}),false);
});
