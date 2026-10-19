import os,asyncio,json,threading,http.server,functools,urllib.request,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
HOOK="""globalThis.__p3QA={positions:()=>Array.from(selected.geometry.attributes.position.array),state:()=>({tool,transformTool,stroke,paintActive,objects:items.length}),point:()=>{const p=selected.geometry.attributes.position;let best=0;for(let i=1;i<p.count;i++)if(p.getZ(i)>p.getZ(best))best=i;const v=new THREE.Vector3().fromBufferAttribute(p,best).applyMatrix4(selected.matrixWorld).project(camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};},undo:()=>undo(),add:()=>add('Sphere'),choose:t=>{tool=t;mode='sculpt';transformTool='none';},reset:()=>{undo();},roundTrip:()=>{const data=snapshot();restore(data);return items.length;},shapeCheck:()=>shapes.map(([name])=>{const g=geometry(name),p=g.attributes.position.array;for(let k=0;k<p.length;k++)if(!Number.isFinite(p[k]))throw Error(name+' nonfinite vertex');if(g.index)for(const i of g.index.array)if(i>=p.length/3)throw Error(name+' invalid index');const out={name,vertices:p.length/3};g.dispose();return out;})};"""
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
  await page.locator('[data-workspace="paint"]').evaluate('(b)=>b.click()');await page.locator('[data-transform="move"]').first.evaluate('(b)=>b.click()');await page.locator('[data-tool="grab"]').evaluate('(b)=>b.click()')
  state=await page.evaluate('__p3QA.state()');assert state['transformTool']=='none' and state['tool']=='grab' and not state['paintActive'],state
  point=await page.evaluate('__p3QA.point()');x=point['x'];y=point['y'];print('PICK',point,await page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.id',[x,y]))
  # Test-only hide floating controls over the model, leaving the canvas/input handlers unchanged.
  await page.evaluate("document.querySelectorAll('body>*:not(#view):not(script):not(style):not(link)').forEach(e=>e.classList.add('qa-hide'))");await page.add_style_tag(content='.qa-hide{visibility:hidden!important} #view{visibility:visible!important}')
  before=await page.evaluate('__p3QA.positions()');await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+80,y,steps=8);await page.wait_for_timeout(100);after=await page.evaluate('__p3QA.positions()');a=max(abs(v-w) for v,w in zip(before,after));assert a>1e-5,('Grab did not deform',await page.evaluate('__p3QA.state()'))
  await page.mouse.move(x+300,y,steps=12);await page.wait_for_timeout(100);far=await page.evaluate('__p3QA.positions()');b=max(abs(v-w) for v,w in zip(before,far));assert b>a,('Grab stopped off surface',a,b)
  await page.mouse.move(x,y,steps=12);await page.wait_for_timeout(100);back=await page.evaluate('__p3QA.positions()');drift=max(abs(v-w) for v,w in zip(before,back));await page.mouse.up();assert drift<.002,('Grab drift',drift)
  await page.evaluate('__p3QA.undo()');restored=await page.evaluate('__p3QA.positions()');assert max(abs(v-w) for v,w in zip(before,restored))<1e-6
  print('PASS main Grab: deformation, off-surface continuation, return without drift, undo; transform deselection')
  for tool in ['inflate','carve','clay','smooth','flatten','pinch']:
   await page.evaluate('(t)=>__p3QA.choose(t)',tool);base=await page.evaluate('__p3QA.positions()');await page.mouse.move(x-12,y);await page.mouse.down();await page.mouse.move(x+45,y+10,steps=12);await page.mouse.up();await page.wait_for_timeout(80);after=await page.evaluate('__p3QA.positions()');assert all(abs(v)<1e6 for v in after);change=max(abs(v-w) for v,w in zip(base,after));assert change>1e-7,(tool,'no deformation');print('PASS brush',tool,round(change,6));await page.evaluate('__p3QA.undo()')
  await page.locator('button',has_text='V2 Performance Sculpt').evaluate('(b)=>b.click()');await page.wait_for_function("document.querySelector('#v2-apply')&&!document.querySelector('#v2-apply').disabled",timeout=30000)
  print('WORKER',await page.locator('#v2-status').inner_text());await page.locator('#v2-tool').select_option('4');c=await page.locator('#p3-v2-engine canvas').bounding_box();wx=c['x']+c['width']/2;wy=c['y']+c['height']/2
  base=await page.evaluate('__p3QA.positions()');await page.mouse.move(wx,wy);await page.mouse.down();await page.mouse.move(wx+100,wy,steps=12);await page.mouse.up();await page.wait_for_timeout(100);await page.locator('#v2-apply').click(force=True);await page.wait_for_function("!document.querySelector('#p3-v2-engine')")
  after=await page.evaluate('__p3QA.positions()');change=max(abs(v-w) for v,w in zip(base,after));assert change>1e-5,('worker grab failed',change);print('PASS worker Grab + apply',change)
  await page.evaluate('__p3QA.roundTrip()');print('PASS scene snapshot/restore');print('SHAPES',json.dumps(await page.evaluate('__p3QA.shapeCheck()')));print('PAGE_ERRORS',json.dumps(errors));print('CONSOLE_ERRORS',json.dumps(console_errors));assert not errors
  await browser.close()
asyncio.run(main())
