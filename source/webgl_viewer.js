const canvas=document.getElementById('view');
const gl=canvas.getContext('webgl',{antialias:true,alpha:false,preserveDrawingBuffer:true});
if(!gl)throw new Error('浏览器无法启用 WebGL，请查看 previews 内的效果图。');
let yaw=.35,pitch=.30,zoom=1,explode=0,drag=null,queued=false;
const visible=new Set(DATA.map(p=>p.id));
function shader(type,source){let s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
const program=gl.createProgram();
gl.attachShader(program,shader(gl.VERTEX_SHADER,`
attribute vec3 position;attribute vec3 normal;attribute vec3 color;
uniform vec4 rotation;uniform vec3 offset;uniform vec3 viewport;
varying vec3 vnormal;varying vec3 vcolor;
void main(){vec3 p=position+offset;p.z-=viewport.z;
float x=p.x*rotation.x+p.y*rotation.y;
float d=-p.x*rotation.y+p.y*rotation.x;
float y=p.z*rotation.z+d*rotation.w;
float depth=d*rotation.z-p.z*rotation.w;
gl_Position=vec4(x*viewport.x,y*viewport.y,depth/500.,1.);
vnormal=normal;vcolor=color;}`));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`
precision mediump float;varying vec3 vnormal;varying vec3 vcolor;
void main(){vec3 n=normalize(vnormal);vec3 light=normalize(vec3(-.4,-.65,.75));
float brightness=.54+.48*max(0.,dot(n,light));
gl_FragColor=vec4(vcolor*brightness,1.);}`));
gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
gl.useProgram(program);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
const attrs=['position','normal','color'].map(n=>gl.getAttribLocation(program,n));
const rot=gl.getUniformLocation(program,'rotation'),off=gl.getUniformLocation(program,'offset'),vp=gl.getUniformLocation(program,'viewport');
DATA.forEach(p=>{let a=new Float32Array(p.f.length*27);let k=0;
for(let i=0;i<p.f.length;i++){
let flat=null;
if(p.id==='P01_Board_Left'||p.id==='P02_Board_Right'){
const [aa,bb,cc]=p.f[i].map(j=>p.v[j]);
const u=bb.map((x,j)=>x-aa[j]),v=cc.map((x,j)=>x-aa[j]);
flat=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
const len=Math.hypot(...flat)||1;flat=flat.map(x=>x/len);}
for(let index of p.f[i]){
for(let x of p.v[index])a[k++]=x;for(let x of flat||p.n[index])a[k++]=x;for(let x of p.c[i])a[k++]=x/255;}}
p.buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,p.buffer);gl.bufferData(gl.ARRAY_BUFFER,a,gl.STATIC_DRAW);p.count=p.f.length*3;
let row=document.createElement('label');row.className='part';let cb=document.createElement('input');cb.type='checkbox';cb.checked=true;
cb.onchange=()=>{cb.checked?visible.add(p.id):visible.delete(p.id);schedule()};let t=document.createElement('span');t.textContent=p.label;
row.append(cb,t);document.getElementById('parts').append(row);});
function schedule(){if(!queued){queued=true;requestAnimationFrame(draw)}}
function draw(){queued=false;let w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio,2);
if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(.945,.953,.969,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
let scale=Math.min(w/240,h/215)*zoom;
gl.uniform4f(rot,Math.cos(yaw),Math.sin(yaw),Math.cos(pitch),Math.sin(pitch));
gl.uniform3f(vp,2*scale/w,2*scale/h,73+explode*30);
for(let p of DATA){if(!visible.has(p.id))continue;gl.bindBuffer(gl.ARRAY_BUFFER,p.buffer);
for(let i=0;i<3;i++){gl.enableVertexAttribArray(attrs[i]);gl.vertexAttribPointer(attrs[i],3,gl.FLOAT,false,36,i*12)}
gl.uniform3f(off,p.offset[0]*explode,p.offset[1]*explode,p.offset[2]*explode);gl.drawArrays(gl.TRIANGLES,0,p.count);}}
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);canvas.style.cursor='grabbing'};
canvas.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.007;pitch=Math.max(-1.3,Math.min(1.3,pitch+(e.clientY-drag[1])*.005));drag=[e.clientX,e.clientY];schedule()};
canvas.onpointerup=()=>{drag=null;canvas.style.cursor='grab'};
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.min(3.8,Math.max(.45,zoom*Math.exp(-e.deltaY*.001)));schedule()},{passive:false});
document.getElementById('explode').oninput=e=>{explode=Number(e.target.value);schedule()};
document.getElementById('iso').onclick=()=>{yaw=.35;pitch=.30;schedule()};document.getElementById('front').onclick=()=>{yaw=0;pitch=0;schedule()};
document.getElementById('back').onclick=()=>{yaw=Math.PI;pitch=.2;schedule()};
document.getElementById('reset').onclick=()=>{yaw=.35;pitch=.30;zoom=1;explode=0;document.getElementById('explode').value=0;visible.clear();DATA.forEach(p=>visible.add(p.id));document.querySelectorAll('.part input').forEach(i=>i.checked=true);schedule()};
new ResizeObserver(schedule).observe(canvas);schedule();
