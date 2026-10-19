/** @typedef {{radius:number,intensity:number,spacing:number,accumulate:boolean,strokeType:'dot'|'drag'}} BrushSettings */
/**
 * Canvas stamp pipeline. No lineTo/native path strokes are used.
 * 3D integrations supply onStamp(x,y,pressure,settings,alpha) and own deformation.
 * Default rendering stamps white alpha into a 2D canvas. All coordinates/radii
 * are backing pixels, unless coordinateSpace:'css' is requested by a 3D adapter.
 */
export function createStampEngine({settings={},onStamp=null,coordinateSpace='pixels',color=[255,255,255]}={}){
 const config={radius:40,intensity:.5,spacing:.05,accumulate:false,strokeType:'drag',...settings};
 // One normalized radial texture, shared by every size; never rebuilt per frame.
 const size=128;let alphaCanvas,alphaContext;try{if(typeof OffscreenCanvas==='function'){alphaCanvas=new OffscreenCanvas(size,size);alphaContext=alphaCanvas.getContext('2d')}}catch{}
 if(!alphaContext&&typeof document!=='undefined'){alphaCanvas=Object.assign(document.createElement('canvas'),{width:size,height:size});alphaContext=alphaCanvas.getContext('2d')}if(!alphaContext)throw Error('Alpha canvas unavailable');
 const pixels=alphaContext.createImageData(size,size),alpha=new Float32Array(size*size);
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const d=Math.hypot((x+.5)*2/size-1,(y+.5)*2/size-1),t=Math.max(0,1-d),a=t*t*(3-2*t),i=y*size+x;
  alpha[i]=a;pixels.data[i*4]=color[0];pixels.data[i*4+1]=color[1];pixels.data[i*4+2]=color[2];pixels.data[i*4+3]=Math.round(a*255);
 }alphaContext.putImageData(pixels,0,0);
 const sampleAlpha=(u,v)=>{if(!Number.isFinite(u)||!Number.isFinite(v)||Math.abs(u)>1||Math.abs(v)>1)return 0;return alpha[Math.min(size-1,Math.floor((v+1)*.5*size))*size+Math.min(size-1,Math.floor((u+1)*.5*size))]};
 let active=false,canvas=null,pointer=null,x=0,y=0,pressure=1,carry=0,stroke=null,ctx=null,base=null,image=null,coverage=null;
 const point={x:0,y:0,pressure:1};
 function read(target,e){const r=target.getBoundingClientRect();if(!(r.width>0&&r.height>0)||!Number.isFinite(e.clientX)||!Number.isFinite(e.clientY))return false;point.x=(e.clientX-r.left)*(coordinateSpace==='css'?1:target.width/r.width);point.y=(e.clientY-r.top)*(coordinateSpace==='css'?1:target.height/r.height);const pad=stroke?.radius||Math.max(1,Math.min(2048,Number(config.radius)||40)),w=coordinateSpace==='css'?r.width:target.width,h=coordinateSpace==='css'?r.height:target.height;point.x=Math.max(-pad,Math.min(w+pad,point.x));point.y=Math.max(-pad,Math.min(h+pad,point.y));point.pressure=e.pointerType==='mouse'||e.pressure===undefined?1:Math.max(0,Math.min(1,Number(e.pressure)||0));return true}
 function snapshot(){const r=Number(config.radius),i=Number(config.intensity),s=Number(config.spacing);return Object.freeze({radius:Math.max(1,Math.min(2048,Math.round(Number.isFinite(r)?r:40))),intensity:Number.isFinite(i)?Math.max(0,Math.min(1,i)):0,spacing:Number.isFinite(s)?Math.max(.01,Math.min(2,s)):.05,accumulate:!!config.accumulate,strokeType:config.strokeType==='dot'?'dot':'drag'})}
 function emit(px,py,p){if(onStamp){onStamp(px,py,p,stroke,sampleAlpha);return}const a=stroke.intensity*p;if(a<=0)return;const r=stroke.radius;
  if(stroke.accumulate){ctx.save();ctx.globalAlpha=a;ctx.globalCompositeOperation='source-over';ctx.drawImage(alphaCanvas,px-r,py-r,r*2,r*2);ctx.restore();return}
  // Maximum coverage per stroke, NOT repeated alpha blending. Every pixel is
  // composited from its stroke-start value, so revisiting cannot build height.
  const w=canvas.width,h=canvas.height,l=Math.max(0,Math.floor(px-r)),top=Math.max(0,Math.floor(py-r)),right=Math.min(w,Math.ceil(px+r)),bottom=Math.min(h,Math.ceil(py+r));
  for(let yy=top;yy<bottom;yy++)for(let xx=l;xx<right;xx++){const k=yy*w+xx,j=k*4,v=sampleAlpha((xx+.5-px)/r,(yy+.5-py)/r)*a;if(v<=coverage[k])continue;coverage[k]=v;const ba=base[j+3]/255,oa=v+ba*(1-v);for(let c=0;c<3;c++)image.data[j+c]=oa?(color[c]*v+base[j+c]*ba*(1-v))/oa:0;image.data[j+3]=oa*255;}
  if(right>l&&bottom>top)ctx.putImageData(image,0,0,l,top,right-l,bottom-top);
 }
 function move(e){if(!read(canvas,e))return;const dx=point.x-x,dy=point.y-y,d=Math.hypot(dx,dy),p=point.pressure;
  // Static points never divide by distance or repeatedly accumulate stamps.
  if(!Number.isFinite(d)||d<=1e-8)return;const step=Math.max(.25,stroke.radius*stroke.spacing);
  // Carry arc length between input segments. This makes a segmented/coalesced
  // path equivalent to the same straight path delivered as one fast event.
  let travelled=step-carry;
  if(stroke.strokeType==='drag')for(;travelled<=d+1e-8;travelled+=step){const t=Math.min(1,travelled/d);emit(x+dx*t,y+dy*t,pressure+(p-pressure)*t)}
  carry=(carry+d)%step;if(carry<1e-8||step-carry<1e-8)carry=0;x=point.x;y=point.y;pressure=p;
 }
 function handleStrokeStart(target,event){if(active||event.button>0||!read(target,event))return false;stroke=snapshot();canvas=target;pointer=event.pointerId;x=point.x;y=point.y;pressure=point.pressure;carry=0;
  if(!onStamp){ctx=target.getContext('2d');if(!ctx)throw Error('Stamp target must be a 2D canvas');if(!stroke.accumulate){image=ctx.getImageData(0,0,target.width,target.height);base=image.data.slice();coverage=new Float32Array(target.width*target.height)}}
  active=true;emit(x,y,pressure);return true;
 }
 function handleStrokeMove(target,event){if(!active||target!==canvas||event.pointerId!==pointer)return false;const coalesced=event.getCoalescedEvents?.();if(coalesced?.length){for(const e of coalesced)move(e);if(coalesced[coalesced.length-1].clientX!==event.clientX||coalesced[coalesced.length-1].clientY!==event.clientY)move(event)}else move(event);return true}
 function handleStrokeEnd(target,event){if(!active||target!==canvas||event.pointerId!==pointer)return false;try{if(event.type!=='pointercancel'&&event.type!=='lostpointercapture')move(event)}finally{cancel()}return true}
 function cancel(){active=false;canvas=null;pointer=null;ctx=null;image=null;base=null;coverage=null}
 return {settings:config,alphaCanvas,sampleAlpha,handleStrokeStart,handleStrokeMove,handleStrokeEnd,cancel,get active(){return active}};
}
