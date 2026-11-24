// ───────────────────────── Three.js vault (scenes 1 & 6) ─────────────────────────
const D = __D__;
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const rnd = mulberry(1971);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=(x)=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const lerp=(a,b,t)=>a+(b-a)*t;

const canvas=document.getElementById('gl');
const R=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
R.setPixelRatio(1); R.setSize(1920,1080,false);
R.outputColorSpace=THREE.SRGBColorSpace; R.toneMapping=THREE.ACESFilmicToneMapping; R.toneMappingExposure=1.05;
R.shadowMap.enabled=true; R.shadowMap.type=THREE.PCFSoftShadowMap;
const S=new THREE.Scene(); S.background=new THREE.Color(0x0a0e16); S.fog=new THREE.Fog(0x0a0e16,12,30);

// simple studio environment for metal reflections
const pm=new THREE.PMREMGenerator(R); const es=new THREE.Scene();
es.add(new THREE.Mesh(new THREE.BoxGeometry(30,30,30),new THREE.MeshBasicMaterial({color:0x1a1e28,side:THREE.BackSide})));
[[0xfff0d0,-8,8,6,10,5],[0x9fc4ff,9,3,3,5,9],[0xffc878,0,-8,7,14,3],[0xffffff,0,10,-4,8,4]].forEach(([c,x,y,z,w,h])=>{
  const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:c,side:THREE.DoubleSide}));m.position.set(x,y,z);m.lookAt(0,0,0);es.add(m);});
S.environment=pm.fromScene(es,0.04).texture;

const steel=new THREE.MeshStandardMaterial({color:0xb4bac4,metalness:.88,roughness:.3});
const dark=new THREE.MeshStandardMaterial({color:0x4b515c,metalness:.85,roughness:.38});
const brass=new THREE.MeshStandardMaterial({color:0xd0a04a,metalness:.92,roughness:.26});
const gold=new THREE.MeshStandardMaterial({color:0xe6b54e,metalness:.95,roughness:.22});

const wall=new THREE.Mesh(new THREE.PlaneGeometry(40,20),new THREE.MeshStandardMaterial({color:0x2a303b,roughness:.9,metalness:.1}));
wall.position.z=-0.7; wall.receiveShadow=true; S.add(wall);
for(let i=-6;i<=6;i++){const seam=new THREE.Mesh(new THREE.BoxGeometry(.05,20,.05),dark);seam.position.set(i*2.6,0,-0.65);S.add(seam);}
const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,30),new THREE.MeshStandardMaterial({color:0x171b22,roughness:.45,metalness:.3}));
floor.rotation.x=-Math.PI/2; floor.position.y=-3.6; floor.receiveShadow=true; S.add(floor);

const frame=new THREE.Mesh(new THREE.TorusGeometry(3.38,.4,32,128),dark); frame.position.z=-0.25; S.add(frame);
const door=new THREE.Group(); S.add(door);
const slab=new THREE.Mesh(new THREE.CylinderGeometry(3,3,.6,128),steel); slab.rotation.x=Math.PI/2; slab.castShadow=true; door.add(slab);
[[2.4,.08],[1.25,.07],[2.85,.05]].forEach(([r,t])=>{const ring=new THREE.Mesh(new THREE.TorusGeometry(r,t,16,128),dark);ring.position.z=.31;door.add(ring);});
for(let i=0;i<20;i++){const a=i/20*Math.PI*2;const b=new THREE.Mesh(new THREE.CylinderGeometry(.15,.15,.22,24),brass);b.rotation.x=Math.PI/2;b.position.set(Math.cos(a)*2.63,Math.sin(a)*2.63,.38);door.add(b);}
const hub=new THREE.Group(); hub.position.z=.4; door.add(hub);
const hubc=new THREE.Mesh(new THREE.CylinderGeometry(.62,.62,.5,48),brass); hubc.rotation.x=Math.PI/2; hub.add(hubc);
for(let i=0;i<5;i++){const a=i/5*Math.PI*2;const sp=new THREE.Group();sp.rotation.z=a;
  const rod=new THREE.Mesh(new THREE.CylinderGeometry(.08,.08,1.9,16),steel);rod.position.y=.95;sp.add(rod);
  const ball=new THREE.Mesh(new THREE.SphereGeometry(.17,24,16),brass);ball.position.y=1.9;sp.add(ball);sp.position.z=.3;hub.add(sp);}
[1.7,-1.7].forEach(y=>{const h=new THREE.Mesh(new THREE.BoxGeometry(.55,.9,.6),dark);h.position.set(-3.35,y,.1);S.add(h);});
const panel=new THREE.Mesh(new THREE.BoxGeometry(.9,1.4,.25),dark); panel.position.set(4.6,0,-.4); S.add(panel);
const lockMat=new THREE.MeshStandardMaterial({color:0x330a06,emissive:0xff3b20,emissiveIntensity:0});
const lockLed=new THREE.Mesh(new THREE.SphereGeometry(.16,24,16),lockMat); lockLed.position.set(4.6,.3,-.22); S.add(lockLed);
const lockLight=new THREE.PointLight(0xff4a2a,0,6,2); lockLight.position.set(4.6,.3,.4); S.add(lockLight);

// coin stacks (savings) for the hook
const coinGeo=new THREE.CylinderGeometry(.34,.34,.07,40);
const stacks=[[-2.6,3.0,13],[-1.7,3.6,9],[1.8,3.3,15],[2.7,2.7,10],[0.2,4.0,7]];
const coinCount=stacks.reduce((s,x)=>s+x[2],0);
const coins=new THREE.InstancedMesh(coinGeo,gold,coinCount); coins.castShadow=true; S.add(coins);
{const m=new THREE.Matrix4();let k=0;stacks.forEach(([x,z,n])=>{for(let i=0;i<n;i++){m.makeTranslation(x+(rnd()-.5)*.04,-3.56+i*.075,z+(rnd()-.5)*.04);coins.setMatrixAt(k++,m);}});}

// banknote stack that materialises in the reveal
const notes=new THREE.Group(); notes.position.set(-2.4,-3.6,3.6); S.add(notes);
const noteMat=new THREE.MeshStandardMaterial({color:0x4f8f5e,roughness:.7,metalness:.05});
const bandMat=new THREE.MeshStandardMaterial({color:0xe9d8a6,roughness:.5});
const NOTES=26, noteMeshes=[];
for(let i=0;i<NOTES;i++){const g=new THREE.Group();
  const n=new THREE.Mesh(new THREE.BoxGeometry(1.9,.045,.9),noteMat);n.castShadow=true;g.add(n);
  g.position.y=.03+i*.05; g.rotation.y=(rnd()-.5)*.06; g.visible=false; notes.add(g); noteMeshes.push(g);}
const band=new THREE.Mesh(new THREE.BoxGeometry(.32,NOTES*.05+.02,.94),bandMat); band.position.y=NOTES*.025+.02; band.visible=false; notes.add(band);
const noteGlow=new THREE.PointLight(0xffd27a,0,8,2); noteGlow.position.set(-2.4,-2.2,4.6); S.add(noteGlow);

// particles: dust (always) + gold motes that converge into the banknotes
function points(n,color,size,opacity){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(n*3),3));
  const m=new THREE.PointsMaterial({color,size,transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending});const p=new THREE.Points(g,m);S.add(p);return p;}
const DUST=260, dust=points(DUST,0xffe2b0,.035,.55), dustSeed=[];
for(let i=0;i<DUST;i++) dustSeed.push([(rnd()-.5)*14,(rnd()-.5)*8,rnd()*8-0.5,rnd()*6.28]);
const MOTES=520, motes=points(MOTES,0xffd27a,.07,0), moteA=[], moteB=[];
for(let i=0;i<MOTES;i++){const th=rnd()*6.28,ph=Math.acos(2*rnd()-1),r=4+rnd()*5;
  moteA.push([-2.4+Math.sin(ph)*Math.cos(th)*r,Math.cos(ph)*r*.6+0.5,Math.sin(ph)*Math.sin(th)*r+3]);
  moteB.push([-2.4+(rnd()-.5)*1.9,-3.6+rnd()*NOTES*.05,3.6+(rnd()-.5)*.9]);}

// light beam + lights
const beam=new THREE.Mesh(new THREE.ConeGeometry(3.4,14,48,1,true),new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:.05,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide}));
beam.position.set(-2.5,3,3); beam.rotation.z=-.45; beam.rotation.x=.25; S.add(beam);
S.add(new THREE.HemisphereLight(0x9fb4d6,0x1a1208,.35));
const key=new THREE.DirectionalLight(0xffe2b8,2.4); key.position.set(-6,7,9); key.castShadow=true;
key.shadow.mapSize.set(1024,1024); Object.assign(key.shadow.camera,{left:-8,right:8,top:8,bottom:-8,near:1,far:30}); S.add(key);
const rim=new THREE.DirectionalLight(0x8fb6ff,1.1); rim.position.set(7,2,-1); S.add(rim);

const cam=new THREE.PerspectiveCamera(38,1920/1080,.1,100);

function draw(t){
  const hook=t<4.8, reveal=t>25.15;
  if(!hook && !reveal) return;
  // dust drift
  const dp=dust.geometry.attributes.position.array;
  for(let i=0;i<DUST;i++){const s=dustSeed[i];dp[i*3]=s[0]+Math.sin(t*.4+s[3])*.3;dp[i*3+1]=s[1]+((t*.12+s[3])%3)-1.5;dp[i*3+2]=s[2];}
  dust.geometry.attributes.position.needsUpdate=true;
  if(hook){
    const p=ease(clamp(t/4.75));
    cam.position.set(lerp(-0.6,-1.9,p),lerp(-0.5,0.3,p),lerp(13.8,10.6,p)); cam.lookAt(-3.4,-0.5,0);
    hub.rotation.z=t*.05; coins.visible=true; notes.visible=false; motes.material.opacity=0; noteGlow.intensity=0;
    lockMat.emissiveIntensity=0; lockLight.intensity=0;
  } else {
    const u=t-25.15, p=ease(clamp(u/6));
    cam.position.set(lerp(-4.4,-2.6,p),lerp(-0.6,0.4,p),lerp(9.0,12.6,p)); cam.lookAt(-2.4,-2.2,1.2);
    hub.rotation.z=0; coins.visible=false;
    const pulse=.5+.5*Math.sin(u*5); const on=clamp((u-.5)/.4);
    lockMat.emissiveIntensity=on*(1.2+pulse*1.6); lockLight.intensity=on*(3+pulse*3);
    // materialisation: "did not exist before" → "the loan created it"
    const g=clamp((t-27.9)/1.5), ge=ease(g);
    const mp=motes.geometry.attributes.position.array;
    for(let i=0;i<MOTES;i++){const a=moteA[i],b=moteB[i];const w=Math.sin(i+t*2)*.08*(1-ge);
      mp[i*3]=lerp(a[0],b[0],ge)+w;mp[i*3+1]=lerp(a[1],b[1],ge);mp[i*3+2]=lerp(a[2],b[2],ge)+w;}
    motes.geometry.attributes.position.needsUpdate=true;
    motes.material.opacity=g<=0?0:(g<.85?Math.min(1,g*4):Math.max(0,(1-g)/.15));
    notes.visible=g>0; const shown=Math.floor(clamp((t-28.4)/1.0)*NOTES);
    noteMeshes.forEach((m,i)=>m.visible=i<shown); band.visible=shown>=NOTES;
    notes.rotation.y=lerp(-.5,.25,clamp((t-28)/3.4));
    noteGlow.intensity=g>0?(g<1?g*14:lerp(14,6,clamp((t-29.4)/1.5))):0;
  }
  R.render(S,cam);
}
draw(0);

// ───────────────────────── GSAP master timeline ─────────────────────────
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({paused:true});
const P={t:0}; tl.to(P,{t:D,duration:D,ease:'none',onUpdate:()=>draw(P.t)},0);
gsap.set('.lid',{scaleY:0,transformOrigin:'50% 0%'});
function blink(sel,times){times.forEach(t=>tl.to(sel,{scaleY:1,duration:.06,yoyo:true,repeat:1,ease:'none'},t));}
function count(sel,from,to,start,dur,fmt){const o={v:from};tl.to(o,{v:to,duration:dur,ease:'power2.out',onUpdate:()=>{document.querySelector(sel).textContent=fmt(o.v)}},start);}
const usd=v=>'$'+Math.round(v).toLocaleString('en-US')+'.00';

// Scene 1 — hook (0 – 4.75)
tl.fromTo('#myth .label',{opacity:0,y:16},{opacity:1,y:0,duration:.5,ease:'power3.out'},0.05);
tl.fromTo('#myth-h',{opacity:0,y:28},{opacity:1,y:0,duration:.7,ease:'power3.out'},0.2);
tl.fromTo('#myth-strike',{scaleX:0},{scaleX:1,duration:.35,ease:'power2.in'},3.42);
tl.fromTo('#myth-x',{opacity:0,scale:2.4,rotation:-30},{opacity:1,scale:1,rotation:-8,duration:.32,ease:'back.out(3)'},3.6);
tl.fromTo('#myth-h',{color:'#f4ead5'},{color:'#8d8676',duration:.3},3.55);
tl.fromTo('#myth-true',{opacity:0,y:14},{opacity:1,y:0,duration:.45,ease:'power2.out'},3.85);
tl.to('#s1',{opacity:0,duration:.3},4.45);

// Scene 2 — Maya walks to the bank (4.45 – 9.8)
tl.fromTo('#s2',{opacity:0},{opacity:1,duration:.35,ease:'power1.inOut'},4.45);
tl.fromTo('#s2-cam',{scale:1.1},{scale:1.0,duration:4.6,ease:'power2.out'},4.45);
tl.fromTo('#s2-clouds',{x:0},{x:80,duration:5.3,ease:'none'},4.45);
tl.fromTo('#s2-far',{x:0},{x:-24,duration:5.3,ease:'none'},4.45);
tl.fromTo('#s2-mid',{x:0},{x:-50,duration:5.3,ease:'none'},4.45);
tl.fromTo('#s2-bank',{x:0},{x:-80,duration:5.3,ease:'none'},4.45);
tl.fromTo('#s2-fg',{x:0},{x:-170,duration:5.3,ease:'none'},4.45);
tl.fromTo('#s2-tag',{opacity:0,scale:.6,y:20},{opacity:1,scale:1,y:0,duration:.4,ease:'back.out(2.2)'},4.85);
tl.to('#s2-tag',{opacity:0,y:-10,duration:.3},6.3);
const W0=5.6, STEP=.31, N=6;
tl.fromTo('#s2-maya-wrap',{x:0},{x:540,duration:STEP*N,ease:'none'},W0);
for(let i=0;i<N;i++){const a=i%2?-20:20;
  tl.to('#m2-leg-front',{rotation:a,svgOrigin:'150 330',duration:STEP,ease:'sine.inOut'},W0+i*STEP);
  tl.to('#m2-leg-back',{rotation:-a,svgOrigin:'150 330',duration:STEP,ease:'sine.inOut'},W0+i*STEP);
  tl.to('#m2-arm-front',{rotation:-a*.8,svgOrigin:'150 204',duration:STEP,ease:'sine.inOut'},W0+i*STEP);
  tl.to('#m2-arm-back',{rotation:a*.8,svgOrigin:'150 204',duration:STEP,ease:'sine.inOut'},W0+i*STEP);
  tl.to('#m2-upper',{y:-7,duration:STEP/2,yoyo:true,repeat:1,ease:'sine.inOut'},W0+i*STEP);}
['#m2-leg-front','#m2-leg-back'].forEach(s=>tl.to(s,{rotation:0,svgOrigin:'150 330',duration:.25,ease:'power2.out'},W0+N*STEP));
['#m2-arm-front','#m2-arm-back'].forEach(s=>tl.to(s,{rotation:0,svgOrigin:'150 204',duration:.25,ease:'power2.out'},W0+N*STEP));
tl.to('#m2-arm-front',{rotation:-35,svgOrigin:'150 204',duration:.3,ease:'back.out(2)'},7.72);
tl.fromTo('#s2-bubble',{opacity:0,scale:.4,transformOrigin:'20% 100%'},{opacity:1,scale:1,duration:.38,ease:'back.out(2.4)'},7.62);
tl.to('#m2-mouth',{scaleY:.4,transformOrigin:'50% 50%',duration:.09,yoyo:true,repeat:7,ease:'none'},7.7);
blink('#m2 .lid',[5.1,7.0,8.9]);
tl.to('#s2-cam',{scale:1.55,transformOrigin:'1030px 690px',duration:.65,ease:'power2.in'},9.2);

// Scene 3 — the loan office (9.5 – 15.3)
tl.fromTo('#s3',{opacity:0},{opacity:1,duration:.35,ease:'power1.inOut'},9.5);
tl.fromTo('#s3-cam',{scale:1.06,x:20},{scale:1.0,x:0,duration:5.0,ease:'power1.out'},9.5);
tl.fromTo('#s3-gauge',{opacity:0,y:30,scale:.85},{opacity:1,y:0,scale:1,duration:.4,ease:'back.out(1.8)'},9.8);
tl.fromTo('#s3-needle',{rotation:-88,svgOrigin:'160 180'},{rotation:52,svgOrigin:'160 180',duration:.95,ease:'power3.out'},9.98);
count('#s3-score',300,742,9.98,.95,v=>Math.round(v));
tl.fromTo('#s3-good',{opacity:0,scale:.5},{opacity:1,scale:1,duration:.3,ease:'back.out(3)'},10.9);
tl.fromTo('#s3-doc',{opacity:0,y:30},{opacity:1,y:0,duration:.4,ease:'power3.out'},10.2);
tl.to('#b3-stamp',{opacity:1,duration:.1},10.75);
tl.to('#b3-arm-front',{rotation:-28,svgOrigin:'236 214',duration:.3,ease:'power2.out'},10.8);
tl.to('#b3-arm-front',{rotation:6,svgOrigin:'236 214',duration:.12,ease:'power4.in'},11.15);
tl.to('#b3-arm-front',{rotation:0,svgOrigin:'236 214',duration:.4,ease:'power2.out'},11.4);
tl.fromTo('#s3-stamp',{opacity:0,scale:2.6},{opacity:1,scale:1,duration:.16,ease:'power4.in'},11.24);
tl.fromTo('#s3-doc',{x:0},{x:6,duration:.05,yoyo:true,repeat:5,ease:'none'},11.4);
tl.to('#m3-mouth',{scaleY:1.35,transformOrigin:'50% 0%',duration:.25,ease:'power2.out'},11.5);
blink('#m3 .lid',[10.4,12.3,14.2]); blink('#b3 .lid',[9.9,11.9,13.8]);
tl.to(['#s3-gauge','#s3-doc'],{opacity:0,y:-20,duration:.3,ease:'power2.in'},12.45);
tl.fromTo('#s3-book',{opacity:0,scaleX:.1,transformOrigin:'50% 50%'},{opacity:1,scaleX:1,duration:.45,ease:'power3.out'},12.55);
tl.fromTo('#s3-l1',{opacity:0,x:-14},{opacity:1,x:0,duration:.3},12.95);
tl.fromTo('#s3-l1 i',{scaleX:0},{scaleX:1,duration:.4,ease:'power2.out'},12.98);
tl.fromTo('#s3-l2',{opacity:0,x:-14},{opacity:1,x:0,duration:.3},13.28);
tl.fromTo('#s3-l2 i',{scaleX:0},{scaleX:1,duration:.4,ease:'power2.out'},13.31);
tl.to('#s3-cam',{scale:2.6,transformOrigin:'960px 440px',duration:.75,ease:'power2.in'},14.55);

// Scene 4 — the ledger (15.0 – 21.15)
tl.fromTo('#s4',{opacity:0},{opacity:1,duration:.35,ease:'power1.inOut'},15.0);
tl.fromTo('#s4-cam',{scale:1.08},{scale:1.0,duration:1.2,ease:'power3.out'},15.0);
tl.to('#s4-cam',{scale:1.035,x:-10,duration:4.6,ease:'sine.inOut'},16.2);
['#s4-hline','#s4-vline','#s4-ink-l','#s4-ink-r','#s4-arrow','#s4-sig'].forEach(s=>{const el=document.querySelector(s);const L=el.getTotalLength();gsap.set(el,{strokeDasharray:L+' '+L,strokeDashoffset:L});});
gsap.set('#s4-arrow',{strokeDasharray:'14 12'});
tl.fromTo('#s4-title',{opacity:0,y:-12},{opacity:1,y:0,duration:.4},15.15);
tl.fromTo('.colhead',{opacity:0,y:16},{opacity:1,y:0,duration:.45,stagger:.12,ease:'power3.out'},15.25);
tl.to('#s4-hline',{strokeDashoffset:0,duration:.55,ease:'power2.inOut'},15.3);
tl.to('#s4-vline',{strokeDashoffset:0,duration:.5,ease:'power2.inOut'},15.5);
tl.fromTo('#s4-b1',{opacity:0,scale:0},{opacity:1,scale:1,duration:.35,ease:'back.out(3)'},16.05);
tl.fromTo('#s4-r1',{opacity:0,x:-30},{opacity:1,x:0,duration:.45,ease:'power3.out'},16.12);
tl.to('#s4-ink-l',{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},16.2);
tl.fromTo('#s4-iou',{opacity:0,y:40,rotation:-14},{opacity:1,y:0,rotation:-4,duration:.45,ease:'back.out(1.8)'},17.4);
tl.to('#s4-sig',{strokeDashoffset:0,duration:.6,ease:'power1.inOut'},17.7);
tl.fromTo('#s4-arrow',{opacity:0},{opacity:1,duration:.2},19.3);
tl.fromTo('#s4-arrow',{strokeDashoffset:300},{strokeDashoffset:0,duration:.6,ease:'none'},19.3);
tl.fromTo('#s4-arrowhead',{opacity:0,scale:0,transformOrigin:'50% 50%'},{opacity:1,scale:1,duration:.25,ease:'back.out(3)'},19.75);
tl.fromTo('#s4-tag',{opacity:0},{opacity:1,duration:.3},19.45);
tl.fromTo('#s4-b2',{opacity:0,scale:0},{opacity:1,scale:1,duration:.35,ease:'back.out(3)'},19.82);
tl.fromTo('#s4-r2',{opacity:0,x:30},{opacity:1,x:0,duration:.45,ease:'power3.out'},19.86);
tl.to('#s4-ink-r',{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},19.92);
tl.fromTo('#s4-check',{opacity:0,y:10},{opacity:1,y:0,duration:.35},20.35);
tl.to('#s4-arrow',{strokeDashoffset:-260,duration:1.4,ease:'none'},19.9);

// Scene 5 — keystrokes → phone (20.7 – 25.65)
tl.fromTo('#s5',{clipPath:'inset(0 0 0 100%)'},{clipPath:'inset(0 0 0 0%)',duration:.55,ease:'power3.inOut'},20.7);
tl.fromTo('#s5-cam',{scale:1.04},{scale:1.0,duration:4.5,ease:'sine.out'},20.7);
const keyOrder=[3,14,7,22,11,18,5,26,9,16,2,21];
keyOrder.forEach((k,i)=>{const t=21.35+i*.075;tl.to(`#k${k} rect`,{y:'+=4',fill:'#7fe0c4',duration:.05,yoyo:true,repeat:1,ease:'none'},t);});
tl.to('#s5-hands',{y:3,duration:.075,yoyo:true,repeat:11,ease:'none'},21.35);
tl.fromTo('#s5-text',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.9,ease:'steps(30)'},21.35);
tl.fromTo('#s5-cursor',{x:0},{x:620,duration:.9,ease:'steps(30)'},21.35);
gsap.set('#s5-arrow',{opacity:0}); gsap.set('#s5-ahead',{opacity:0});
tl.to('#s5-arrow',{opacity:1,duration:.2},22.05);
tl.fromTo('#s5-arrow',{strokeDashoffset:0},{strokeDashoffset:-120,duration:3,ease:'none'},22.05);
tl.fromTo('#s5-pulse',{strokeDashoffset:70},{strokeDashoffset:-560,duration:.6,ease:'power1.in'},22.05);
tl.fromTo('#s5-ahead',{opacity:0,scale:0,transformOrigin:'50% 50%'},{opacity:1,scale:1,duration:.2,ease:'back.out(3)'},22.5);
count('#s5-bal',0,10000,22.62,.8,usd);
tl.fromTo('#s5-phone',{boxShadow:'0 0 0 10px #2b3a52,0 30px 60px rgba(0,0,0,.4)'},{boxShadow:'0 0 0 10px #7fe0c4,0 0 90px rgba(127,224,196,.65)',duration:.3,yoyo:true,repeat:1},22.62);
tl.fromTo('#s5-tx',{opacity:0,y:30},{opacity:1,y:0,duration:.4,ease:'back.out(1.6)'},23.35);
tl.to('#m5-mouth',{scaleY:1.5,transformOrigin:'50% 0%',duration:.25,ease:'power2.out'},23.4);
tl.fromTo('#m5-upper',{y:0},{y:-6,duration:.25,yoyo:true,repeat:1,ease:'sine.inOut'},23.4);
blink('#m5 .lid',[21.2,24.5]);
tl.to('#s5',{opacity:0,duration:.45,ease:'power1.in'},25.2);

// Scene 6 — the reveal (25.2 – end)
tl.fromTo('#s6-lock',{opacity:0,x:-20},{opacity:1,x:0,duration:.45,ease:'power3.out'},25.7);
tl.to('#s6-lock',{opacity:0,duration:.4},28.9);
tl.fromTo('#s6-eq',{opacity:0},{opacity:1,duration:.3},29.3);
tl.fromTo('#e1',{opacity:0,y:20},{opacity:1,y:0,duration:.35,ease:'power3.out'},29.38);
tl.fromTo('#e2',{opacity:0,x:-20},{opacity:1,x:0,duration:.3,ease:'power2.out'},29.6);
tl.fromTo('#e3',{opacity:0,y:20},{opacity:1,y:0,duration:.35,ease:'power3.out'},29.74);
tl.fromTo('#e4',{opacity:0,scale:.6},{opacity:1,scale:1,duration:.45,ease:'back.out(2.2)'},30.0);
tl.fromTo('#s6-brand',{opacity:0},{opacity:.9,duration:.6},30.3);

window.__timelines["main"] = tl;
tl.seek(0);
