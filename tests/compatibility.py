import os,asyncio,json,threading,http.server,functools,urllib.request,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
HOOK="""globalThis.__p3QA={ctx:()=>renderer.getContext(),selectedName:()=>selected?.name,finish:()=>finishInterruptedInput(),positions:()=>Array.from(selected.geometry.attributes.position.array),state:()=>({tool,transformTool,stroke,paintActive,objects:items.length}),point:()=>{selected.updateWorldMatrix(true,false);camera.updateMatrixWorld();const p=selected.geometry.attributes.position;let best=0;for(let i=1;i<p.count;i++)if(p.getZ(i)>p.getZ(best))best=i;const v=new THREE.Vector3().fromBufferAttribute(p,best).applyMatrix4(selected.matrixWorld).project(camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};},undo:()=>undo(),add:()=>add('Sphere'),choose:t=>{tool=t;mode='sculpt';transformTool='none';},reset:()=>{undo();},adjCheck:()=>{const saved=snapshot(),o=entry(selected);adjacency(o);const old=o.mesh.geometry;const g=solidSculptGeometry(new THREE.BoxGeometry(2,2,2,2,2,2));o.mesh.geometry=g;old.dispose();o.base=g.attributes.position.array.slice();const a=adjacency(o),valid=a.length===g.attributes.position.count&&a.every(row=>row.every(i=>i<g.attributes.position.count));restore(saved);return valid;},hitAt:(x,y)=>{const h=hit(x,y);return h?{object:h.object.name,selected:h.object===selected}:null;},extra:()=>({pos:selected.position.toArray(),bg:scene.background.getHexString(),mat:originalMaterial(selected).color.getHexString(),ortho:!!camera.isOrthographicCamera,lights:customLights.map(l=>l.type),bones:rigBones.length,painted:!!selected.geometry.attributes.color}),place:()=>{selected.position.set(.31,.29,.41);syncTransform();},indicator:()=>({visible:ring.visible,radius:ring.scale.x,enabled:brushIndicatorEnabled}),roundTrip:()=>{const data=snapshot();restore(data);return items.length;},shapeCheck:()=>shapes.map(([name])=>{const g=geometry(name),p=g.attributes.position.array;for(let k=0;k<p.length;k++)if(!Number.isFinite(p[k]))throw Error(name+' nonfinite vertex');if(g.index)for(const i of g.index.array)if(i>=p.length/3)throw Error(name+' invalid index');const out={name,vertices:p.length/3};g.dispose();return out;})};"""
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
  for profile in ['touch','webgl1','no-worker','worker-failure','no-webgl']:
   context=await browser.new_context(viewport={'width':390,'height':844} if profile=='touch' else {'width':1280,'height':900},has_touch=profile=='touch',is_mobile=profile=='touch')
   if profile=='webgl1':await context.add_init_script("const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,...a){return t==='webgl2'?null:get.call(this,t,...a)}")
   if profile=='no-worker':await context.add_init_script("Object.defineProperty(window,'Worker',{value:undefined});Object.defineProperty(window,'ResizeObserver',{value:undefined});Object.defineProperty(window,'OffscreenCanvas',{value:undefined})")
   if profile=='no-webgl':await context.add_init_script("const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,...a){return /webgl/.test(t)?null:get.call(this,t,...a)}")
   if profile=='worker-failure':await context.add_init_script("Object.defineProperty(window,'Worker',{value:class{constructor(){throw Error('Test startup failure')}}});Object.defineProperty(window,'ResizeObserver',{value:undefined})")
   page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.route('https://**',lambda r:r.abort())
   await page.goto(f'http://127.0.0.1:{server.server_address[1]}',wait_until='networkidle')
   if profile=='no-webgl':
    await page.wait_for_selector('#p3BootFailure');assert 'graphics' in (await page.locator('#p3BootFailure').inner_text()).lower();print('PASS no WebGL: actionable recovery');await context.close();continue
   print('START',profile,errors,flush=True);await page.wait_for_function('!!window.__p3QA')
   if profile=='no-worker':assert await page.locator('button',has_text='V2 Performance Sculpt').is_disabled()
   if profile=='worker-failure':
    before=await page.evaluate('__p3QA.positions()');await page.locator('button',has_text='V2 Performance Sculpt').evaluate('(b)=>b.click()');await page.wait_for_function("document.querySelector('#v2-status')?.textContent.includes('Test startup failure')");assert await page.locator('#v2-apply').is_disabled();await page.locator('#v2-close').click();assert not await page.evaluate('window.p3PerformanceActive');assert before==await page.evaluate('__p3QA.positions()')
   if profile=='webgl1':assert await page.evaluate("!(__p3QA.ctx() instanceof WebGL2RenderingContext)")
   await page.evaluate("document.getElementById('p3StartApp')?.click();document.getElementById('logoOverlay').hidden=true")
   if profile=='touch':
    await page.evaluate("__p3QA.choose('stamp')")
    await page.evaluate("document.querySelectorAll('body>*:not(#view):not(script):not(style):not(link)').forEach(e=>e.style.visibility='hidden');document.querySelector('#view').style.visibility='visible'")
    point=await page.evaluate('__p3QA.point()');before=await page.evaluate('__p3QA.positions()');session=await context.new_cdp_session(page)
    await session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':point['x'],'y':point['y'],'force':.5}]})
    for i in range(1,7):await session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':point['x']+i*4,'y':point['y'],'force':.7}]})
    await session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await page.wait_for_timeout(120)
    after=await page.evaluate('__p3QA.positions()');assert max(abs(a-b) for a,b in zip(before,after))>1e-6;assert not (await page.evaluate('__p3QA.state()'))['stroke']
   if profile=='webgl1':
    before=await page.evaluate('__p3QA.positions()');await page.evaluate("window.loss=__p3QA.ctx().getExtension('WEBGL_lose_context');loss.loseContext()")
    await page.wait_for_function('window.P3GraphicsLost');await page.wait_for_timeout(250);await page.evaluate('loss.restoreContext()');await page.wait_for_function('!window.P3GraphicsLost');assert before==await page.evaluate('__p3QA.positions()')
   assert not errors,errors;print('PASS',profile,'local-only startup and interactions');await context.close()
  await browser.close()
asyncio.run(main())
