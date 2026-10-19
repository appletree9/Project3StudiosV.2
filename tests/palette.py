import os,asyncio,json,threading,http.server,functools,urllib.request,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
HOOK="""globalThis.__p3QA={center:()=>{selected.position.set(0,0,0);selected.updateWorldMatrix(true,false)},positions:()=>Array.from(selected.geometry.attributes.position.array),state:()=>({tool,transformTool,stroke,paintActive,objects:items.length}),point:()=>{selected.updateWorldMatrix(true,false);camera.updateMatrixWorld();const p=selected.geometry.attributes.position;let best=0;for(let i=1;i<p.count;i++)if(p.getZ(i)>p.getZ(best))best=i;const v=new THREE.Vector3().fromBufferAttribute(p,best).applyMatrix4(selected.matrixWorld).project(camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};},undo:()=>undo(),add:()=>add('Sphere'),choose:t=>{tool=t;mode='sculpt';transformTool='none';},reset:()=>{undo();},adjCheck:()=>{const saved=snapshot(),o=entry(selected);adjacency(o);const old=o.mesh.geometry;const g=solidSculptGeometry(new THREE.BoxGeometry(2,2,2,2,2,2));o.mesh.geometry=g;old.dispose();o.base=g.attributes.position.array.slice();const a=adjacency(o),valid=a.length===g.attributes.position.count&&a.every(row=>row.every(i=>i<g.attributes.position.count));restore(saved);return valid;},hitAt:(x,y)=>{const h=hit(x,y);return h?{object:h.object.name,selected:h.object===selected}:null;},extra:()=>({pos:selected.position.toArray(),bg:scene.background.getHexString(),mat:originalMaterial(selected).color.getHexString(),ortho:!!camera.isOrthographicCamera,lights:customLights.map(l=>l.type),bones:rigBones.length,painted:!!selected.geometry.attributes.color}),place:()=>{selected.position.set(.31,.29,.41);syncTransform();},indicator:()=>({visible:ring.visible,radius:ring.scale.x,enabled:brushIndicatorEnabled}),roundTrip:()=>{const data=snapshot();restore(data);return items.length;},shapeCheck:()=>shapes.map(([name])=>{const g=geometry(name),p=g.attributes.position.array;for(let k=0;k<p.length;k++)if(!Number.isFinite(p[k]))throw Error(name+' nonfinite vertex');if(g.index)for(const i of g.index.array)if(i>=p.length/3)throw Error(name+' invalid index');const out={name,vertices:p.length/3};g.dispose();return out;})};"""
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def do_GET(self):
  if self.path in ['/','/index.html']:
   s=(ROOT/'index.html').read_text().replace("$('left').prepend(v2Launch);","$('left').prepend(v2Launch);"+HOOK);b=s.encode();self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  else:super().do_GET()
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for mode in ['fresh','old-default','custom']:
   ctx=await browser.new_context(viewport={'width':390,'height':844} if os.environ.get('P3_PHONE_VIEWPORT')=='1' else {'width':1280,'height':900})
   if mode=='old-default':await ctx.add_init_script("localStorage.setItem('project3studios-v2:p3-interface-appearance',JSON.stringify({tint:'#182438',opacity:91,accent:'#6ba8ff'}));localStorage.setItem('project3studios-v2:p3sculpt-ui-accent','#8ca8bd')")
   if mode=='custom':await ctx.add_init_script("localStorage.setItem('project3studios-v2:p3-interface-appearance',JSON.stringify({tint:'#453749',opacity:88,accent:'#e6aa77'}))")
   page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));await page.goto(f'http://127.0.0.1:{server.server_address[1]}',wait_until='networkidle');await page.wait_for_selector('#p3PanelTint',state='attached')
   tint=await page.locator('#p3PanelTint').input_value();accent=await page.locator('#p3AccentTint').input_value();assert (tint,accent)==(('#453749','#e6aa77') if mode=='custom' else ('#373632','#b8aa97')),(mode,tint,accent)
   scene_bg=(await page.evaluate('__p3QA.extra()'))['bg'];assert scene_bg=='303237'
   await page.evaluate("document.getElementById('p3StartApp')?.click();document.getElementById('logoOverlay').hidden=true")
   assert await page.locator('#p3-light-shade-select').input_value()=='stone'
   if mode=='fresh':await page.screenshot(path='/tmp/p3-stone-dark.png')
   await page.locator('#themeSwitch').evaluate('(b)=>b.click()');assert await page.evaluate('document.body.classList.contains("light-mode")')
   if mode!='custom':
    assert await page.locator('body').evaluate('e=>getComputedStyle(e).getPropertyValue("--p3-ui-tint").trim()')=='#e7e1d7';await page.screenshot(path='/tmp/p3-stone-light.png')
   await page.locator('#p3UiReset').evaluate('(b)=>b.click()');assert await page.locator('#p3PanelTint').input_value()=='#373632'
   assert (await page.evaluate('__p3QA.extra()'))['bg']==scene_bg;assert not errors,errors;print('PASS',mode,'stone defaults, theme toggle, preserved custom colors, reset and unchanged scene background')
   await ctx.close()
  await browser.close()
asyncio.run(main())
