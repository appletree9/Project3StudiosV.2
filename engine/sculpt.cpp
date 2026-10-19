#include <cmath>
#include <algorithm>
#include <cstdint>
#ifdef P3_THREADS
#include <thread>
#include <mutex>
#include <condition_variable>
void startPool();
#endif
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define API EMSCRIPTEN_KEEPALIVE
#else
#define API
#endif
// Fixed capacity: no malloc, vector growth or memory growth during strokes.
constexpr int CAP=300000, NC=65536;
static float p[CAP*3],n[CAP*3],undoP[CAP*3];
static uint32_t tri[CAP*6],ids[CAP],offsets[CAP+1],adjacent[CAP*12],adjCursor[CAP];
static float brushOld[CAP*3];
struct Node{float lo[3],hi[3];int a,b,left,right;};
static Node nodes[NC];static int count,nt,used;static float best,bx,by,bz;
void bounds(int q){auto &v=nodes[q];for(int k=0;k<3;k++){v.lo[k]=1e30f;v.hi[k]=-1e30f;}for(int i=v.a;i<v.b;i++)for(int k=0;k<3;k++){float x=p[ids[i]*3+k];v.lo[k]=std::min(v.lo[k],x);v.hi[k]=std::max(v.hi[k],x);}}
int build(int a,int b){int q=used++;auto &v=nodes[q];v.a=a;v.b=b;v.left=v.right=-1;bounds(q);if(b-a>16){int k=0;for(int j=1;j<3;j++)if(v.hi[j]-v.lo[j]>v.hi[k]-v.lo[k])k=j;int m=(a+b)/2;std::nth_element(ids+a,ids+m,ids+b,[k](int x,int y){return p[x*3+k]<p[y*3+k];});v.left=build(a,m);v.right=build(m,b);}return q;}
extern "C" {
API float* positions(){return p;} API float* normals(){return n;} API uint32_t* indices(){return tri;}
API int capacity(){return CAP;}
API int setup(int vertices,int triangles){if(vertices<3||vertices>CAP||triangles<1||triangles>CAP*2)return 0;for(int i=0;i<triangles*3;i++)if(tri[i]>=(uint32_t)vertices)return 0;count=vertices;nt=triangles;std::fill(offsets,offsets+count+1,0);for(int t=0;t<nt*3;t++)offsets[tri[t]+1]+=2;for(int i=1;i<=count;i++)offsets[i]+=offsets[i-1];std::copy(offsets,offsets+count,adjCursor);for(int t=0;t<nt*3;t+=3){for(int j=0;j<3;j++){int a=tri[t+j];adjacent[adjCursor[a]++]=tri[t+(j+1)%3];adjacent[adjCursor[a]++]=tri[t+(j+2)%3];}}for(int i=0;i<count;i++)ids[i]=i;used=0;build(0,count);
#ifdef P3_THREADS
startPool();
#endif
return 1;}
API void checkpoint(){std::copy(p,p+count*3,undoP);}
API void undo(){std::swap_ranges(p,p+count*3,undoP);used=0;build(0,count);}
API void recalc(){std::fill(n,n+count*3,0.f);for(int t=0;t<nt*3;t+=3){int a=tri[t]*3,b=tri[t+1]*3,c=tri[t+2]*3;float x=p[b]-p[a],y=p[b+1]-p[a+1],z=p[b+2]-p[a+2],u=p[c]-p[a],v=p[c+1]-p[a+1],w=p[c+2]-p[a+2];float nx=y*w-z*v,ny=z*u-x*w,nz=x*v-y*u;for(int j=0;j<3;j++){int i=tri[t+j]*3;n[i]+=nx;n[i+1]+=ny;n[i+2]+=nz;}}for(int i=0;i<count*3;i+=3){float l=std::sqrt(n[i]*n[i]+n[i+1]*n[i+1]+n[i+2]*n[i+2]);if(l>1e-12f){n[i]/=l;n[i+1]/=l;n[i+2]/=l;}}}
}
void refit(int q){auto &v=nodes[q];if(v.left<0){bounds(q);return;}for(int k=0;k<3;k++){v.lo[k]=std::min(nodes[v.left].lo[k],nodes[v.right].lo[k]);v.hi[k]=std::max(nodes[v.left].hi[k],nodes[v.right].hi[k]);}}
int deform(int q,float x,float y,float z,float radius,float amount,int tool,float dx,float dy,float dz){auto &v=nodes[q];float d=0;float c[3]={x,y,z};for(int k=0;k<3;k++){float a=std::max(v.lo[k]-c[k],std::max(0.f,c[k]-v.hi[k]));d+=a*a;}if(d>radius*radius)return 0;int changed=0;if(v.left>=0){changed=deform(v.left,x,y,z,radius,amount,tool,dx,dy,dz)+deform(v.right,x,y,z,radius,amount,tool,dx,dy,dz);}else{for(int a=v.a;a<v.b;a++){int i=ids[a]*3;float u=p[i]-x,w=p[i+1]-y,t=p[i+2]-z;float dist=std::sqrt(u*u+w*w+t*t);if(dist>=radius)continue;float f=1-dist/radius;f=f*f*amount; if(tool==7||tool==8){float sx=0,sy=0,sz=0;int id=ids[a],degree=offsets[id+1]-offsets[id];if(!degree)continue;for(uint32_t k=offsets[id];k<offsets[id+1];k++){int v=adjacent[k]*3;sx+=brushOld[v];sy+=brushOld[v+1];sz+=brushOld[v+2];}sx=sx/degree-brushOld[i];sy=sy/degree-brushOld[i+1];sz=sz/degree-brushOld[i+2];if(tool==7){float dot=sx*n[i]+sy*n[i+1]+sz*n[i+2];sx-=n[i]*dot*.75f;sy-=n[i+1]*dot*.75f;sz-=n[i+2]*dot*.75f;}float t=f*(tool==7?.5f:.8f);p[i]+=sx*t;p[i+1]+=sy*t;p[i+2]+=sz*t;}else if(tool==2||tool==6){float dot=u*dx+w*dy+t*dz;if(tool==6)dot=std::max(0.f,dot+radius*.06f);p[i]-=dx*dot*f;p[i+1]-=dy*dot*f;p[i+2]-=dz*dot*f;}else if(tool==3||tool==5){float dot=u*dx+w*dy+t*dz;p[i]-=(u-dx*dot)*f*.3f;p[i+1]-=(w-dy*dot)*f*.3f;p[i+2]-=(t-dz*dot)*f*.3f;if(tool==5){p[i]-=n[i]*f*.025f;p[i+1]-=n[i+1]*f*.025f;p[i+2]-=n[i+2]*f*.025f;}}else if(tool==4){p[i]+=dx*f;p[i+1]+=dy*f;p[i+2]+=dz*f;}else{p[i]+=(tool==10?dx:n[i])*f*.045f;p[i+1]+=(tool==10?dy:n[i+1])*f*.045f;p[i+2]+=(tool==10?dz:n[i+2])*f*.045f;}changed++;}}if(changed)refit(q);return changed;}

#ifdef P3_THREADS
// One persistent helper plus the coordinator; each owns disjoint BVH subtrees.
static std::mutex jobMutex;static std::condition_variable workCV,doneCV;
static bool hasJob=false,done=true;static int jobTool,result;static float args[8];
void startPool(){static bool started=false;if(started)return;started=true;
 std::thread([]{for(;;){std::unique_lock<std::mutex> lock(jobMutex);workCV.wait(lock,[]{return hasJob;});hasJob=false;lock.unlock();
 int value=deform(nodes[0].left,args[0],args[1],args[2],args[3],args[4],jobTool,args[5],args[6],args[7]);
 lock.lock();result=value;done=true;lock.unlock();doneCV.notify_one();}}).detach();}
#endif
extern "C" API int dab(float x,float y,float z,float r,float a,int tool,float dx,float dy,float dz){
if(tool==7||tool==8)std::copy(p,p+count*3,brushOld);
#ifdef P3_THREADS
 if(count>20000&&nodes[0].left>=0){
  {std::lock_guard<std::mutex> lock(jobMutex);args[0]=x;args[1]=y;args[2]=z;args[3]=r;args[4]=a;args[5]=dx;args[6]=dy;args[7]=dz;jobTool=tool;done=false;hasJob=true;}
  workCV.notify_one();int changed=deform(nodes[0].right,x,y,z,r,a,tool,dx,dy,dz);
  {std::unique_lock<std::mutex> lock(jobMutex);doneCV.wait(lock,[]{return done;});changed+=result;}
  if(changed)refit(0);return changed;
 }
#endif
 return deform(0,x,y,z,r,a,tool,dx,dy,dz);
}
void pickNode(int q,const float* o,const float* d,float tol){auto &v=nodes[q];float near=0,far=best;for(int k=0;k<3;k++){if(std::abs(d[k])<1e-8f){if(o[k]<v.lo[k]-tol||o[k]>v.hi[k]+tol)return;}else{float a=(v.lo[k]-tol-o[k])/d[k],b=(v.hi[k]+tol-o[k])/d[k];if(a>b)std::swap(a,b);near=std::max(near,a);far=std::min(far,b);if(near>far)return;}}if(v.left>=0){pickNode(v.left,o,d,tol);pickNode(v.right,o,d,tol);return;}for(int a=v.a;a<v.b;a++){int i=ids[a]*3;float x=p[i]-o[0],y=p[i+1]-o[1],z=p[i+2]-o[2],t=x*d[0]+y*d[1]+z*d[2];if(t<0||t>=best)continue;float u=x-t*d[0],w=y-t*d[1],v=z-t*d[2];if(u*u+w*w+v*v<=tol*tol){best=t;bx=p[i];by=p[i+1];bz=p[i+2];}}}
extern "C" {API int pick(float ox,float oy,float oz,float dx,float dy,float dz,float tolerance){float o[3]={ox,oy,oz},d[3]={dx,dy,dz};best=1e30f;pickNode(0,o,d,tolerance);return best<1e30f;}API float hitx(){return bx;}API float hity(){return by;}API float hitz(){return bz;}}
// Drag uses frozen stroke weights and checkpoint positions, so it follows the
// cursor even after leaving the original surface and does not accumulate drift.
static float grabWeights[CAP],grabFactors[CAP];static int grabMirror=0;static float grabCenterX=0;
extern "C" {
API void drag_begin(float x,float y,float z,float r,int mirror){grabMirror=mirror;grabCenterX=x;for(int i=0;i<count;i++){int k=i*3;float dx=undoP[k]-x,dy=undoP[k+1]-y,dz=undoP[k+2]-z;float d=std::sqrt(dx*dx+dy*dy+dz*dz),f=std::max(0.f,1-d/r),w1=f*f,w2=0;if(mirror&&std::abs(x)>.0001f){dx=undoP[k]+x;d=std::sqrt(dx*dx+dy*dy+dz*dz);f=std::max(0.f,1-d/r);w2=f*f;}grabWeights[i]=std::max(w1,w2);grabFactors[i]=w2?(w1-w2)/(w1+w2):1;}}
API void drag_update(float dx,float dy,float dz,float amount){for(int i=0;i<count;i++){int k=i*3;float w=grabWeights[i]*amount,mx=dx*grabFactors[i];p[k]=undoP[k]+mx*w;p[k+1]=undoP[k+1]+dy*w;p[k+2]=undoP[k+2]+dz*w;}for(int q=used-1;q>=0;q--)refit(q);}
}
