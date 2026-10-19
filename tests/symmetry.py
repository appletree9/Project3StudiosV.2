import os,asyncio,json,threading,http.server,functools,urllib.request,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
HOOK="""globalThis.__p3QA={positions:()=>Array.from(selected.geometry.attributes.position.array),state:()=>({tool,transformTool,stroke,paintActive,objects:items.length}),point:()=>{selected.updateWorldMatrix(true,false);camera.updateMatrixWorld();const p=selected.geometry.attributes.position;let best=0;for(let i=1;i<p.count;i++)if(p.getZ(i)>p.getZ(best))best=i;const v=new THREE.Vector3().fromBufferAttribute(p,best).applyMatrix4(selected.matrixWorld).project(camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};},undo:()=>undo(),add:()=>add('Sphere'),choose:t=>{tool=t;mode='sculpt';transformTool='none';},reset:()=>{undo();},adjCheck:()=>{const saved=snapshot(),o=entry(selected);adjacency(o);const old=o.mesh.geometry;const g=solidSculptGeometry(new THREE.BoxGeometry(2,2,2,2,2,2));o.mesh.geometry=g;old.dispose();o.base=g.attributes.position.array.slice();const a=adjacency(o),valid=a.length===g.attributes.position.count&&a.every(row=>row.every(i=>i<g.attributes.position.count));restore(saved);return valid;},hitAt:(x,y)=>{const h=hit(x,y);return h?{object:h.object.name,selected:h.object===selected}:null;},extra:()=>({pos:selected.position.toArray(),bg:scene.background.getHexString(),mat:originalMaterial(selected).color.getHexString(),ortho:!!camera.isOrthographicCamera,lights:customLights.map(l=>l.type),bones:rigBones.length,painted:!!selected.geometry.attributes.color}),place:()=>{selected.position.set(.31,.29,.41);syncTransform();},symmetry:()=>{const inv=selected.matrixWorld.clone().invert();return {visible:symmetryBrushRing.visible,main:ring.position.clone().applyMatrix4(inv).toArray(),mirror:symmetryBrushRing.position.clone().applyMatrix4(inv).toArray()};},indicator:()=>({visible:ring.visible,radius:ring.scale.x,enabled:brushIndicatorEnabled}),roundTrip:()=>{const data=snapshot();restore(data);return items.length;},shapeCheck:()=>shapes.map(([name])=>{const g=geometry(name),p=g.attributes.position.array;for(let k=0;k<p.length;k++)if(!Number.isFinite(p[k]))throw Error(name+' nonfinite vertex');if(g.index)for(const i of g.index.array)if(i>=p.length/3)throw Error(name+' invalid index');const out={name,vertices:p.length/3};g.dispose();return out;})};"""
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
  page=await browser.new_page(viewport={'width':390,'height':844} if os.environ.get('P3_PHONE_VIEWPORT')=='1' else {'width':1440,'height':1000});errors=[];console_errors=[]
  async def cdn(route):
   url=route.request.url;path=pathlib.Path('/tmp/p3-cdn-'+hashlib.sha256(url.encode()).hexdigest())
   if not path.exists():path.write_bytes(await asyncio.to_thread(lambda:urllib.request.urlopen(url,timeout=30).read()))
   await route.fulfill(body=path.read_bytes(),content_type='application/javascript',headers={'access-control-allow-origin':'*'})
  await page.route('https://cdn.jsdelivr.net/**',cdn)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None)
  await page.goto(f'http://127.0.0.1:{server.server_address[1]}',wait_until='networkidle',timeout=60000);await page.wait_for_function('!!window.__p3QA')
  await page.evaluate("document.getElementById('p3StartApp')?.click();document.getElementById('logoOverlay').hidden=true")
  hideStyle=await page.add_style_tag(content='body>*:not(#view):not(script):not(style):not(link){visibility:hidden!important} #view{visibility:visible!important}')
  point=await page.evaluate('__p3QA.point()');x=point['x']+55;y=point['y'];await page.mouse.move(x,y);await page.wait_for_timeout(80)
  assert not (await page.evaluate('__p3QA.symmetry()'))['visible']
  await page.locator('#p3SymOn').evaluate("e=>{e.checked=true;e.dispatchEvent(new Event('change'))}")
  for axis in ['x','y','z']:
   await page.locator('#p3SymAxis').evaluate("(e,v)=>{e.value=v;e.dispatchEvent(new Event('change'))}",axis);await page.wait_for_timeout(50)
   result=await page.evaluate('__p3QA.symmetry()');assert result['visible'],result
   for k in range(3):assert abs(result['mirror'][k]-result['main'][k]*(-1 if k=='xyz'.index(axis) else 1))<1e-5,result
   assert ('Mirror '+axis.upper()) in await page.locator('#p3BrushIndicator').text_content()
  await page.locator('#p3BrushIndicators').evaluate("e=>{e.checked=false;e.dispatchEvent(new Event('change'))}");assert not (await page.evaluate('__p3QA.symmetry()'))['visible']
  await page.locator('#p3BrushIndicators').evaluate("e=>{e.checked=true;e.dispatchEvent(new Event('change'))}");await page.mouse.move(x+1,y);await page.wait_for_timeout(50);assert (await page.evaluate('__p3QA.symmetry()'))['visible']
  await page.locator('#p3SymOn').evaluate("e=>{e.checked=false;e.dispatchEvent(new Event('change'))}");assert not (await page.evaluate('__p3QA.symmetry()'))['visible']
  print('PASS main: X/Y/Z mirror alignment, axis label, symmetry off, indicator toggle')
  # Restore visibility before entering the performance workspace.
  await hideStyle.evaluate('(e)=>e.remove()')
  await page.locator('button',has_text='V2 Performance Sculpt').evaluate('(b)=>b.click()');await page.wait_for_function("document.querySelector('#v2-apply')&&!document.querySelector('#v2-apply').disabled",timeout=30000)
  await page.locator('#v2-sym').check();c=await page.locator('#p3-v2-engine canvas').bounding_box();wx=c['x']+c['width']*.55;wy=c['y']+c['height']*.5
  await page.mouse.move(wx,wy);await page.wait_for_function("document.getElementById('v2-brush-mirror').style.display==='block'")
  assert 'Mirror X' in await page.locator('#v2-brush-label').text_content()
  p=await page.locator('#v2-brush-mirror').evaluate('(e)=>parseFloat(e.style.left)');assert abs(p-c['width']*.45)<c['width']*.025
  await page.locator('#v2-orbit').click();await page.mouse.move(wx,wy);await page.mouse.down();await page.mouse.move(wx+60,wy+25,steps=6);await page.mouse.up();await page.locator('#v2-orbit').click();await page.mouse.move(wx+1,wy);await page.wait_for_timeout(100)
  await page.wait_for_function("document.getElementById('v2-brush-mirror').style.display==='block'");updated=await page.locator('#v2-brush-mirror').evaluate('(e)=>parseFloat(e.style.left)');assert abs(updated-p)>.5,(updated,p)
  await page.locator('#v2-sym').uncheck();assert await page.locator('#v2-brush-mirror').evaluate("e=>e.style.display==='none'")
  print('PASS worker: mirror outline, label, projection, orbit refresh, symmetry off')
  print('PAGE_ERRORS',errors,'CONSOLE_ERRORS',console_errors);assert not errors and not console_errors
  await browser.close()
asyncio.run(main())
