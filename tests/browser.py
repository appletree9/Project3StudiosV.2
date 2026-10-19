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
  page=await browser.new_page(viewport={'width':390,'height':844} if os.environ.get('P3_PHONE_VIEWPORT')=='1' else {'width':1440,'height':1000});errors=[];console_errors=[]
  async def cdn(route):
   url=route.request.url;path=pathlib.Path('/tmp/p3-cdn-'+hashlib.sha256(url.encode()).hexdigest())
   if not path.exists():path.write_bytes(await asyncio.to_thread(lambda:urllib.request.urlopen(url,timeout=30).read()))
   await route.fulfill(body=path.read_bytes(),content_type='application/javascript',headers={'access-control-allow-origin':'*'})
  await page.route('https://cdn.jsdelivr.net/**',cdn)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None)
  await page.goto(f'http://127.0.0.1:{server.server_address[1]}',wait_until='networkidle',timeout=60000);await page.wait_for_function('!!window.__p3QA')
  await page.evaluate("document.getElementById('p3StartApp')?.click();document.getElementById('logoOverlay').hidden=true")
  await page.locator('[data-workspace="paint"]').evaluate('(b)=>b.click()');await page.locator('[data-transform="move"]').first.evaluate('(b)=>b.click()');await page.locator('[data-tool="drag"]').evaluate('(b)=>b.click()')
  state=await page.evaluate('__p3QA.state()');assert state['transformTool']=='none' and state['tool']=='drag' and not state['paintActive'],state
  point=await page.evaluate('__p3QA.point()');x=point['x'];y=point['y'];print('PICK',point,await page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.id',[x,y]))
  # Test-only hide floating controls over the model, leaving the canvas/input handlers unchanged.
  await page.evaluate("document.querySelectorAll('body>*:not(#view):not(script):not(style):not(link)').forEach(e=>e.classList.add('qa-hide'))");await page.add_style_tag(content='.qa-hide{visibility:hidden!important} #view{visibility:visible!important}')
  before=await page.evaluate('__p3QA.positions()');await page.mouse.move(x,y);await page.wait_for_timeout(30);assert (await page.evaluate('__p3QA.indicator()'))['visible'];await page.mouse.down();await page.mouse.move(x+80,y,steps=8);await page.wait_for_timeout(100);after=await page.evaluate('__p3QA.positions()');a=max(abs(v-w) for v,w in zip(before,after));assert a>1e-5,('Drag did not deform',await page.evaluate('__p3QA.state()'))
  await page.mouse.move(x+300,y,steps=12);await page.wait_for_timeout(100);far=await page.evaluate('__p3QA.positions()');b=max(abs(v-w) for v,w in zip(before,far));assert b>a,('Drag stopped off surface',a,b)
  await page.mouse.move(x,y,steps=12);await page.wait_for_timeout(100);back=await page.evaluate('__p3QA.positions()');drift=max(abs(v-w) for v,w in zip(before,back));await page.mouse.up();assert drift<.002,('Drag drift',drift)
  await page.evaluate('__p3QA.undo()');restored=await page.evaluate('__p3QA.positions()');assert max(abs(v-w) for v,w in zip(before,restored))<1e-6
  print('PASS main Drag: deformation, off-surface continuation, return without drift, undo; transform deselection')
  for tool in ['inflate','carve','clay','smooth','flatten','pinch','grab','crease','scrape','polish']:
   await page.evaluate('(t)=>__p3QA.choose(t)',tool);base=await page.evaluate('__p3QA.positions()');await page.mouse.move(x-12,y);await page.mouse.down();await page.mouse.move(x+45,y+10,steps=12);await page.mouse.up();await page.wait_for_timeout(80);after=await page.evaluate('__p3QA.positions()');assert all(abs(v)<1e6 for v in after);change=max(abs(v-w) for v,w in zip(base,after));assert change>1e-7,(tool,'no deformation');print('PASS brush',tool,round(change,6));await page.evaluate('__p3QA.undo()')
  await page.locator('button',has_text='V2 Performance Sculpt').evaluate('(b)=>b.click()');await page.wait_for_function("document.querySelector('#v2-apply')&&!document.querySelector('#v2-apply').disabled",timeout=30000)
  print('WORKER',await page.locator('#v2-status').inner_text());assert await page.locator('#v2-brush-cursor').count()==1;await page.locator('#v2-tool').select_option('9',force=True);c=await page.locator('#p3-v2-engine canvas').bounding_box();wx=c['x']+c['width']/2;wy=c['y']+c['height']/2
  base=await page.evaluate('__p3QA.positions()');await page.mouse.move(wx,wy);await page.mouse.down();await page.mouse.move(wx+100,wy,steps=12);await page.mouse.up();await page.wait_for_timeout(100);await page.locator('#v2-apply').click(force=True);await page.wait_for_function("!document.querySelector('#p3-v2-engine')")
  after=await page.evaluate('__p3QA.positions()');change=max(abs(v-w) for v,w in zip(base,after));assert change>1e-5,('worker grab failed',change);print('PASS worker Drag + apply',change)
  await page.evaluate('__p3QA.roundTrip()');print('PASS scene snapshot/restore');print('SHAPES',json.dumps(await page.evaluate('__p3QA.shapeCheck()')));
  # Exercise existing editor controls without changing user-facing source.
  await page.locator('#duplicate').evaluate('(b)=>b.click()');assert (await page.evaluate('__p3QA.state()'))['objects']==2
  await page.locator('#remove').evaluate('(b)=>b.click()');assert (await page.evaluate('__p3QA.state()'))['objects']==1
  theme=await page.evaluate("document.body.classList.contains('light-mode')");await page.locator('#themeSwitch').evaluate('(b)=>b.click()');assert await page.evaluate("document.body.classList.contains('light-mode')")!=theme
  await page.locator('#background').evaluate("e=>{e.value='#223344';e.dispatchEvent(new Event('input',{bubbles:true}))}");assert (await page.evaluate('__p3QA.extra()'))['bg']=='223344'
  await page.locator('#materialViewMode').select_option('matcap',force=True);await page.locator('#color').evaluate("e=>{e.value='#44bb88';e.dispatchEvent(new Event('input',{bubbles:true}))}");assert (await page.evaluate('__p3QA.extra()'))['mat']=='44bb88';await page.locator('#materialViewMode').select_option('material',force=True)
  await page.locator('#cameraProjection').select_option('orthographic',force=True);assert (await page.evaluate('__p3QA.extra()'))['ortho'];await page.locator('#cameraProjection').select_option('perspective',force=True)
  await page.evaluate('__p3QA.place()')
  await page.locator('#moveSnapStep').evaluate("e=>{e.value='0.25';e.dispatchEvent(new Event('change',{bubbles:true}))}");await page.locator('#snapNow').evaluate('(b)=>b.click()');assert all(abs(v/.25-round(v/.25))<1e-5 for v in (await page.evaluate('__p3QA.extra()'))['pos'])
  await page.locator('#lightType').select_option('point',force=True);await page.locator('#addLight').evaluate('(b)=>b.click()')
  for kind,expected in [('spot','SpotLight'),('directional','DirectionalLight'),('hemisphere','HemisphereLight'),('ambient','AmbientLight'),('point','PointLight')]:
   await page.locator('#lightType').select_option(kind,force=True);assert (await page.evaluate('__p3QA.extra()'))['lights']==[expected]
  await page.locator('#removeLight').evaluate('(b)=>b.click()');assert not (await page.evaluate('__p3QA.extra()'))['lights']
  assert await page.evaluate('__p3QA.adjCheck()');print('PASS duplicate/remove, theme, background, material/Matcap, projection, snapping, five light types, adjacency refresh after topology change')
  # Paint and native scene files.
  await page.evaluate('__p3QA.center()');point=await page.evaluate('__p3QA.point()');x=point['x'];y=point['y'];await page.locator('[data-workspace="paint"]').evaluate('(b)=>b.click()');await page.locator('#vertexPaintColor').evaluate("e=>{e.value='#ee2222';e.dispatchEvent(new Event('input',{bubbles:true}))}");await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+30,y,steps=6);await page.mouse.up();print('PAINT_STATE',await page.evaluate('__p3QA.state()'),point,await page.evaluate('([x,y])=>({hit:__p3QA.hitAt(x,y),element:document.elementFromPoint(x,y)?.id})',[x,y]));assert (await page.evaluate('__p3QA.extra()'))['painted'];await page.locator('[data-tool="drag"]').evaluate('(b)=>b.click()')
  async def dialog(d):await d.accept('QA Sculpt' if d.type=='prompt' else None)
  page.on('dialog',dialog)
  async with page.expect_download() as downloaded:await page.locator('#saveOBJ').evaluate('(b)=>b.click()')
  obj=await downloaded.value;objpath=await obj.path();assert 'v ' in pathlib.Path(objpath).read_text()
  async with page.expect_download(predicate=lambda d:d.suggested_filename.endswith('.p3sculpt')) as downloaded:await page.locator('#p3SaveProject').evaluate('(b)=>b.click()')
  download=await downloaded.value;print('PROJECT_DOWNLOAD',download.suggested_filename,flush=True);data=pathlib.Path(await download.path()).read_bytes();assert json.loads(data)['meshes'],(download.suggested_filename,data[:80])
  await page.locator('#p3ProjectFile').set_input_files({'name':'QA.p3sculpt','mimeType':'application/json','buffer':data});await page.wait_for_timeout(250);assert (await page.evaluate('__p3QA.state()'))['objects']==1
  before_invalid=await page.evaluate('__p3QA.positions()');bad=json.loads(data);bad['meshes'][0]['indices']=[0,1,len(bad['meshes'][0]['positions'])];await page.locator('#p3ProjectFile').set_input_files({'name':'bad.p3sculpt','mimeType':'application/json','buffer':json.dumps(bad).encode()});await page.wait_for_timeout(100);assert await page.evaluate('__p3QA.positions()')==before_invalid;print('PASS malformed project rejected without changing the scene')
  await page.locator('#rigPreset').select_option('basic',force=True);await page.locator('#rigCreate').evaluate('(b)=>b.click()');assert (await page.evaluate('__p3QA.extra()'))['bones']>=3;await page.locator('#rigClose').evaluate('(b)=>b.click()')
  print('PASS painting, OBJ export, native project save/reopen, basic rig create/close')
  # Export and mesh-processing paths on a small test scene.
  exports=[('#measureSTL','stl'),('#capture','png')]
  if os.environ.get('P3_TEST_GLB')=='1':exports.insert(0,('#exportGLBColors','glb'))
  for selector,kind in exports:
   if kind=='png':
    await page.locator('#renderSize').select_option('640x360',force=True);await page.locator('#renderQuality').select_option('1',force=True)
   async with page.expect_download(timeout=45000) as downloaded:await page.locator(selector).evaluate('(b)=>b.click()')
   download=await downloaded.value;raw=pathlib.Path(await download.path()).read_bytes();assert len(raw)>100
   if kind=='glb':assert raw[:4]==b'glTF'
   if kind=='png':assert raw[:8]==b'\x89PNG\r\n\x1a\n'
   print('PASS export',kind,len(raw))
  await page.locator('#voxelResolution').evaluate("e=>{e.value='16';e.dispatchEvent(new Event('input',{bubbles:true}))}");await page.locator('#voxelRemesh').evaluate('(b)=>b.click()');await page.wait_for_function("!document.getElementById('voxelRemesh').disabled",timeout=30000);assert 'Complete:' in await page.locator('#voxelStatus').text_content(),await page.locator('#voxelStatus').text_content();print('PASS voxel remesh at resolution 16')
  if await page.locator('#p3MovieExport').is_enabled():
   await page.locator('#p3MovieMotion').select_option('turntable',force=True);webm=await page.locator('#p3MovieFormat option[value*=webm]').first.get_attribute('value');await page.locator('#p3MovieFormat').select_option(webm,force=True) if webm else None;await page.locator('#p3MovieEndTime').evaluate("e=>{e.value='2';e.dispatchEvent(new Event('change',{bubbles:true}))}");await page.locator('#p3MovieResolution').select_option('640x360',force=True);await page.locator('#p3MovieQuality').select_option('low',force=True);await page.locator('#p3MovieFPS').select_option('15',force=True);await page.locator('#p3MovieExport').evaluate('(b)=>b.click()');await page.wait_for_function("!document.getElementById('p3MovieExport').disabled",timeout=30000);assert await page.locator('#p3MovieDownload').get_attribute('href') and (await page.locator('#p3MovieStatus').text_content()).startswith('Ready:'),await page.locator('#p3MovieStatus').text_content();print('PASS short turntable movie export')
  
  print('PAGE_ERRORS',json.dumps(errors));print('CONSOLE_ERRORS',json.dumps(console_errors));assert not errors
  await browser.close()
asyncio.run(main())
