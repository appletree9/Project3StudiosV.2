#define P3_THREADS
#include "../engine/sculpt.cpp"
#include <cstdio>
#include <cstdlib>
int main(){const int size=30000;for(int i=0;i<size;i++){p[i*3]=(i%100)*.02f-1;p[i*3+1]=((i/100)%100)*.02f-1;p[i*3+2]=(i/10000)*.03f;}tri[0]=0;tri[1]=1;tri[2]=100; if(!setup(size,1))return 1;for(int i=0;i<size;i++)n[i*3+2]=1;
 static float expected[90000];std::copy(p,p+90000,expected);
 for(int j=0;j<20;j++){float cx=(j-10)*.025f,r=.55f;for(int i=0;i<size;i++){int k=i*3;float x=expected[k]-cx,y=expected[k+1],z=expected[k+2];float distance=std::sqrt(x*x+y*y+z*z);if(distance<r){float f=1-distance/r;expected[k+2]+=f*f*.4f*.045f;}}dab(cx,0,0,r,.4f,0,0,0,1);}
 for(int i=0;i<90000;i++)if(std::abs(p[i]-expected[i])>1e-6f){std::printf("FAIL at %d\n",i);std::_Exit(1);}std::puts("PASS: persistent threaded BVH deformation matches brute force over 20 strokes / 30,000 vertices");std::fflush(stdout);std::_Exit(0);}
