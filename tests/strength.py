import os,asyncio,json,threading,http.server,functools,urllib.request,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
HOOK="""const strengthBaseline=snapshot();globalThis.__p3QA={strengthReset:()=>{restore(strengthBaseline);},center:()=>{selected.position.set(0,0,0);selected.updateWorldMatrix(true,false)},positions:()=>Array.from(selected.geometry.attributes.position.array),state:()=>({tool,transformTool,stroke,paintActive,objects:items.length}),point:()=>{selected.updateWorldMatrix(true,false);camera.updateMatrixWorld();const p=selected.geometry.attributes.position;let best=0;for(let i=1;i<p.count;i++)if(p.getZ(i)>p.getZ(best))best=i;const v=new THREE.Vector3().fromBufferAttribute(p,best).applyMatrix4(selected.matrixWorld).project(camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};},undo:()=>undo(),add:()=>add('Sphere'),choose:t=>{tool=t;mode='sculpt';transformTool='none';},reset:()=>{undo();},adjCheck:()=>{const saved=snapshot(),o=entry(selected);adjacency(o);const old=o.mesh.geometry;const g=solidSculptGeometry(new THREE.BoxGeometry(2,2,2,2,2,2));o.mesh.geometry=g;old.dispose();o.base=g.attributes.position.array.slice();const a=adjacency(o),valid=a.length===g.attributes.position.count&&a.every(row=>row.every(i=>i<g.attributes.position.count));restore(saved);return valid;},hitAt:(x,y)=>{const h=hit(x,y);return h?{object:h.object.name,selected:h.object===selected}:null;},extra:()=>({pos:selected.position.toArray(),bg:scene.background.getHexString(),mat:originalMaterial(selected).color.getHexString(),ortho:!!camera.isOrthographicCamera,lights:customLights.map(l=>l.type),bones:rigBones.length,painted:!!selected.geometry.attributes.color}),place:()=>{selected.position.set(.31,.29,.41);syncTransform();},indicator:()=>({visible:ring.visible,radius:ring.scale.x,enabled:brushIndicatorEnabled}),roundTrip:()=>{const data=snapshot();restore(data);return items.length;},shapeCheck:()=>shapes.map(([name])=>{const g=geometry(name),p=g.attributes.position.array;for(let k=0;k<p.length;k++)if(!Number.isFinite(p[k]))throw Error(name+' nonfinite vertex');if(g.index)for(const i of g.index.array)if(i>=p.length/3)throw Error(name+' invalid index');const out={name,vertices:p.length/3};g.dispose();return out;})};"""
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
  browser=await p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=await browser.new_page(viewport={'width':390,'height':844} if os.environ.get('P3_PHONE_VIEWPORT')=='1' else {'width':1200,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(f'http://127.0.0.1:{server.server_address[1]}',wait_until='networkidle');await page.wait_for_function('!!window.__p3QA')
  await page.evaluate("document.getElementById('p3StartApp')?.click();document.getElementById('logoOverlay').hidden=true;document.querySelectorAll('body>*:not(#view):not(script):not(style):not(link)').forEach(e=>e.classList.add('qa-hide'))");await page.add_style_tag(content='.qa-hide{visibility:hidden!important} #view{visibility:visible!important}')
  async def set_strength(value):await page.locator('#strength').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(value))
  for tool in ['inflate','carve','clay','smooth','flatten','pinch','grab','drag','crease','scrape','polish','stamp']:
   changes=[]
   for value in [0,.1,1]:
    await page.evaluate('__p3QA.strengthReset()');await page.locator('[data-tool="'+tool+'"]').evaluate('(b)=>b.click()');await set_strength(value);point=await page.evaluate('__p3QA.point()');x,y=point['x'],point['y'];before=await page.evaluate('__p3QA.positions()');await page.mouse.move(x-8,y);await page.mouse.down();await page.mouse.move(x+32,y+8,steps=8);await page.mouse.up();await page.wait_for_timeout(40);after=await page.evaluate('__p3QA.positions()');assert all(abs(v)<100 for v in after);changes.append(max(abs(a-b) for a,b in zip(before,after)))
   assert changes[0]<1e-7,(tool,'zero strength modifies mesh',changes)
   assert changes[2]>changes[1]*1.2 and changes[1]>0,(tool,'strength response',changes)
   print('PASS strength 0 / 10 / 100%',tool,changes,flush=True)
  assert await page.locator('#strengthValue').text_content()=='100%'
  for value in [.1,1]:
   await page.evaluate('__p3QA.strengthReset()');await page.locator('button',has_text='V2 Performance Sculpt').evaluate('(b)=>b.click()');await page.wait_for_function("document.querySelector('#v2-apply')&&!document.querySelector('#v2-apply').disabled")
   await page.locator('#v2-strength').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(value));await page.wait_for_timeout(30);r=await page.locator('#p3-v2-engine canvas').bounding_box();x,y=r['x']+r['width']/2,r['y']+r['height']/2;before=await page.evaluate('__p3QA.positions()');await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+30,y,steps=8);await page.mouse.up();await page.locator('#v2-apply').click(force=True);await page.wait_for_function("!document.querySelector('#p3-v2-engine')");after=await page.evaluate('__p3QA.positions()');delta=max(abs(a-b) for a,b in zip(before,after));
   if value==.1:low=delta
   else:assert delta>low*1.2,(low,delta);print('PASS worker strength comparison',low,delta)
  assert not errors,errors;print('PAGE_ERRORS',errors);await browser.close()
asyncio.run(main())
