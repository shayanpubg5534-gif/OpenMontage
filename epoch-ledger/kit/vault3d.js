// Epoch Ledger — reusable Three.js bank vault (seek-safe, deterministic).
//
// const vault = EpochVault3D.create({ canvas, shots: [...], materialize: {...} });
// tl.to(P, { t: D, duration: D, ease: 'none', onUpdate: () => vault.draw(P.t) }, 0);
//
// A "shot" is a time window in which the canvas is drawn with its own camera move.
// Outside every shot draw() returns early, so HTML scenes can cover the canvas for free.
//   { start, end, dur, camFrom:[x,y,z], camTo:[x,y,z], lookAt:[x,y,z],
//     coins: bool (savings stacks), hubSpin: rad/s, lock: bool (pulsing red lock),
//     materialize: bool (gold motes converge into a banknote stack) }
// materialize: { start, dur, notesStart, notesDur, spinStart, spinDur, glowFadeStart, glowFadeDur, at:[x,z] }
// Defaults reproduce the "How Banks Create Money" pilot.
(function (global) {
  function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
  const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
  const ease=(x)=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
  const lerp=(a,b,t)=>a+(b-a)*t;

  const PILOT_SHOTS=[
    {start:0,end:4.8,dur:4.75,camFrom:[-0.6,-0.5,13.8],camTo:[-1.9,0.3,10.6],lookAt:[-3.4,-0.5,0],coins:true,hubSpin:.05,lock:false,materialize:false},
    {start:25.15,end:Infinity,dur:6,camFrom:[-4.4,-0.6,9.0],camTo:[-2.6,0.4,12.6],lookAt:[-2.4,-2.2,1.2],coins:false,hubSpin:0,lock:true,materialize:true},
  ];
  const PILOT_MAT={start:27.9,dur:1.5,notesStart:28.4,notesDur:1.0,spinStart:28,spinDur:3.4,glowFadeStart:29.4,glowFadeDur:1.5,at:[-2.4,3.6]};

  function create(opts){
    const o=Object.assign({seed:1971,width:1920,height:1080,shots:PILOT_SHOTS},opts||{});
    const M=Object.assign({},PILOT_MAT,o.materialize||{});
    const [NX,NZ]=M.at;
    const rnd=mulberry(o.seed);
    const R=new THREE.WebGLRenderer({canvas:o.canvas,antialias:true,preserveDrawingBuffer:true});
    R.setPixelRatio(1); R.setSize(o.width,o.height,false);
    R.outputColorSpace=THREE.SRGBColorSpace; R.toneMapping=THREE.ACESFilmicToneMapping; R.toneMappingExposure=1.05;
    R.shadowMap.enabled=true; R.shadowMap.type=THREE.PCFSoftShadowMap;
    const S=new THREE.Scene(); S.background=new THREE.Color(0x0a0e16); S.fog=new THREE.Fog(0x0a0e16,12,30);

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

    const coinGeo=new THREE.CylinderGeometry(.34,.34,.07,40);
    const stacks=[[-2.6,3.0,13],[-1.7,3.6,9],[1.8,3.3,15],[2.7,2.7,10],[0.2,4.0,7]];
    const coinCount=stacks.reduce((s,x)=>s+x[2],0);
    const coins=new THREE.InstancedMesh(coinGeo,gold,coinCount); coins.castShadow=true; S.add(coins);
    {const m=new THREE.Matrix4();let k=0;stacks.forEach(([x,z,n])=>{for(let i=0;i<n;i++){m.makeTranslation(x+(rnd()-.5)*.04,-3.56+i*.075,z+(rnd()-.5)*.04);coins.setMatrixAt(k++,m);}});}

    const notes=new THREE.Group(); notes.position.set(NX,-3.6,NZ); S.add(notes);
    const noteMat=new THREE.MeshStandardMaterial({color:0x4f8f5e,roughness:.7,metalness:.05});
    const bandMat=new THREE.MeshStandardMaterial({color:0xe9d8a6,roughness:.5});
    const NOTES=26, noteMeshes=[];
    for(let i=0;i<NOTES;i++){const g=new THREE.Group();
      const n=new THREE.Mesh(new THREE.BoxGeometry(1.9,.045,.9),noteMat);n.castShadow=true;g.add(n);
      g.position.y=.03+i*.05; g.rotation.y=(rnd()-.5)*.06; g.visible=false; notes.add(g); noteMeshes.push(g);}
    const band=new THREE.Mesh(new THREE.BoxGeometry(.32,NOTES*.05+.02,.94),bandMat); band.position.y=NOTES*.025+.02; band.visible=false; notes.add(band);
    const noteGlow=new THREE.PointLight(0xffd27a,0,8,2); noteGlow.position.set(NX,-2.2,NZ+1); S.add(noteGlow);

    function points(n,color,size,opacity){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(n*3),3));
      const m=new THREE.PointsMaterial({color,size,transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending});const p=new THREE.Points(g,m);S.add(p);return p;}
    const DUST=260, dust=points(DUST,0xffe2b0,.035,.55), dustSeed=[];
    for(let i=0;i<DUST;i++) dustSeed.push([(rnd()-.5)*14,(rnd()-.5)*8,rnd()*8-0.5,rnd()*6.28]);
    const MOTES=520, motes=points(MOTES,0xffd27a,.07,0), moteA=[], moteB=[];
    for(let i=0;i<MOTES;i++){const th=rnd()*6.28,ph=Math.acos(2*rnd()-1),r=4+rnd()*5;
      moteA.push([NX+Math.sin(ph)*Math.cos(th)*r,Math.cos(ph)*r*.6+0.5,Math.sin(ph)*Math.sin(th)*r+3]);
      moteB.push([NX+(rnd()-.5)*1.9,-3.6+rnd()*NOTES*.05,NZ+(rnd()-.5)*.9]);}

    const beam=new THREE.Mesh(new THREE.ConeGeometry(3.4,14,48,1,true),new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:.05,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide}));
    beam.position.set(-2.5,3,3); beam.rotation.z=-.45; beam.rotation.x=.25; S.add(beam);
    S.add(new THREE.HemisphereLight(0x9fb4d6,0x1a1208,.35));
    const key=new THREE.DirectionalLight(0xffe2b8,2.4); key.position.set(-6,7,9); key.castShadow=true;
    key.shadow.mapSize.set(1024,1024); Object.assign(key.shadow.camera,{left:-8,right:8,top:8,bottom:-8,near:1,far:30}); S.add(key);
    const rim=new THREE.DirectionalLight(0x8fb6ff,1.1); rim.position.set(7,2,-1); S.add(rim);

    const cam=new THREE.PerspectiveCamera(38,o.width/o.height,.1,100);

    function draw(t){
      const shot=o.shots.find(s=>t>=s.start&&t<s.end&&!(s.start>0&&t===s.start));
      if(!shot) return;
      const dp=dust.geometry.attributes.position.array;
      for(let i=0;i<DUST;i++){const s=dustSeed[i];dp[i*3]=s[0]+Math.sin(t*.4+s[3])*.3;dp[i*3+1]=s[1]+((t*.12+s[3])%3)-1.5;dp[i*3+2]=s[2];}
      dust.geometry.attributes.position.needsUpdate=true;
      const u=t-shot.start, p=ease(clamp(u/shot.dur));
      const a=shot.camFrom,b=shot.camTo,l=shot.lookAt;
      cam.position.set(lerp(a[0],b[0],p),lerp(a[1],b[1],p),lerp(a[2],b[2],p)); cam.lookAt(l[0],l[1],l[2]);
      hub.rotation.z=shot.hubSpin?t*shot.hubSpin:0; coins.visible=!!shot.coins;
      if(shot.lock){const pulse=.5+.5*Math.sin(u*5);const on=clamp((u-.5)/.4);
        lockMat.emissiveIntensity=on*(1.2+pulse*1.6); lockLight.intensity=on*(3+pulse*3);}
      else {lockMat.emissiveIntensity=0; lockLight.intensity=0;}
      if(shot.materialize){
        const g=clamp((t-M.start)/M.dur), ge=ease(g);
        const mp=motes.geometry.attributes.position.array;
        for(let i=0;i<MOTES;i++){const A=moteA[i],B=moteB[i];const w=Math.sin(i+t*2)*.08*(1-ge);
          mp[i*3]=lerp(A[0],B[0],ge)+w;mp[i*3+1]=lerp(A[1],B[1],ge);mp[i*3+2]=lerp(A[2],B[2],ge)+w;}
        motes.geometry.attributes.position.needsUpdate=true;
        motes.material.opacity=g<=0?0:(g<.85?Math.min(1,g*4):Math.max(0,(1-g)/.15));
        notes.visible=g>0; const shown=Math.floor(clamp((t-M.notesStart)/M.notesDur)*NOTES);
        noteMeshes.forEach((m,i)=>m.visible=i<shown); band.visible=shown>=NOTES;
        notes.rotation.y=lerp(-.5,.25,clamp((t-M.spinStart)/M.spinDur));
        noteGlow.intensity=g>0?(g<1?g*14:lerp(14,6,clamp((t-M.glowFadeStart)/M.glowFadeDur))):0;
      } else { notes.visible=false; motes.material.opacity=0; noteGlow.intensity=0; }
      R.render(S,cam);
    }
    draw(0);
    return {draw, scene:S, camera:cam, renderer:R};
  }
  global.EpochVault3D={create,PILOT_SHOTS,PILOT_MAT};
})(window);
