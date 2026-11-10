// GPL-3.0-or-later. Interactions against the real frontend with synthetic backend state.
import {test,expect} from '@playwright/test';
for(const size of [{width:760,height:500},{width:960,height:620},{width:1100,height:700},{width:1440,height:900}]){
  test(`navigation and settings fit ${size.width}×${size.height}`,async({page})=>{
    await page.setViewportSize(size);const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto('/');await expect(page.getByRole('button',{name:'Choose game disc',exact:true})).toBeVisible();
    for(const name of ['Home',"What's New",'Settings']){
      await page.getByRole('button',{name,exact:true}).click();
      await expect(page.getByRole('button',{name,exact:true})).toHaveAttribute('aria-current','page');
      await expect.poll(()=>page.locator('#view').evaluate(el=>el.scrollWidth<=el.clientWidth+1)).toBeTruthy();
    }
    for(const name of ['Display','Audio','Controls','Storage','About']){
      await page.getByRole('tab',{name,exact:true}).check();
      await expect(page.locator('[role="tabpanel"]')).toHaveAttribute('id','panel-'+name);
      expect(await page.locator('#view').evaluate(el=>el.scrollWidth<=el.clientWidth+1)).toBeTruthy();
    }
    expect(errors).toEqual([]);
  });
}
test('tasks survive page changes and preferences commit through the bridge',async({page})=>{
  await page.goto('/');await page.getByRole('button',{name:'Choose game disc',exact:true}).click();
  await page.getByRole('button',{name:'Prepare & play',exact:true}).click();
  await expect(page.locator('#task-pill')).toContainText('42%');
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await expect(page.getByRole('combobox',{name:'Window mode',exact:true})).toBeDisabled();
  await expect(page.locator('#task-pill')).toContainText('42%');
  await page.locator('#task-pill').click();await page.getByRole('button',{name:'Stop',exact:true}).click();
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await page.getByRole('combobox',{name:'Window mode',exact:true}).selectOption('2');
  await expect.poll(()=>page.evaluate(()=>window.__N2_MOCK__.state.options.video_mode)).toBe(2);
  await page.getByRole('tab',{name:'Audio',exact:true}).check();
  await page.getByRole('slider',{name:'Master volume',exact:true}).focus();
  await page.keyboard.press('Home');
  for(let i=0;i<26;i++)await page.keyboard.press('ArrowRight');
  await expect.poll(()=>page.evaluate(()=>window.__N2_MOCK__.state.options.master_volume)).toBe(26);
});
test('remote release text is literal and reduced-motion navigation remains scrollable',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');
  await page.evaluate(()=>{const {state,emit}=window.__N2_MOCK__;state.releases[0].body='<img src=x onerror="window.bad=true">';state.revision++;emit('state',structuredClone(state));});
  await page.getByRole('button',{name:"What's New",exact:true}).click();
  await expect(page.locator('.notes-body')).toHaveText('<img src=x onerror="window.bad=true">');
  expect(await page.evaluate(()=>window.bad)).toBeUndefined();
  await page.getByRole('button',{name:'Settings',exact:true}).click();await page.getByRole('tab',{name:'Controls',exact:true}).check();
  expect(await page.locator('#view').evaluate(el=>getComputedStyle(el).overflowY)).toBe('auto');
});
