// Epoch Ledger timeline helpers (expects `tl` = the paused master timeline).
// blink(sel, times): eyelid blinks · count(sel, from, to, start, dur, fmt): number count-up · usd(v): $1,234.00
// Determinism: a transformOrigin inside a timeline tween is interpolated and reverted with the playhead, and GSAP's
// smoothOrigin offsets SVG elements by their *current* transform, so a frame could depend on what was drawn before it
// (found by scripts/qc.mjs). The origin is a property of the element, not of a moment: it is applied once at build time
// (gsap.set outside the timeline, smoothOrigin off) and removed from the tween. An element given two different origins
// keeps them in its tweens (smoothOrigin off). R3 joints never get origin tweens: offsets go on R3.carrier groups.
// GSAP's default force3D:"auto" promotes an element to a GPU layer while its tween runs and drops it at the end, so
// Chromium's rasterisation of a frame (edges, grain) depends on which frames came before. Keep transforms 2D.
gsap.config({ force3D: false });
const __elOrigin = new WeakMap();
(function(){const hoist=(targets,v)=>{if(!v||typeof v!=='object'||Array.isArray(v)||!('transformOrigin' in v))return v;
  const o=v.transformOrigin,els=gsap.utils.toArray(targets).filter(e=>e instanceof Element);
  if(!els.length||typeof o!=='string'||els.some(e=>__elOrigin.has(e)&&__elOrigin.get(e)!==o)){if(!('smoothOrigin' in v))v.smoothOrigin=false;return v;}
  els.forEach(e=>{if(!__elOrigin.has(e)){__elOrigin.set(e,o);gsap.set(e,{transformOrigin:o,smoothOrigin:false});}});
  const c=Object.assign({},v);delete c.transformOrigin;return c;};
const wrap=(o,ms)=>ms.forEach(m=>{const g=o[m];if(!g||g.__elDet)return;const w=m==='fromTo'?function(t,a,b,...r){return g.call(this,t,hoist(t,a),hoist(t,b),...r);}:function(t,v,...r){return g.call(this,t,hoist(t,v),...r);};w.__elDet=1;o[m]=w;});
wrap(gsap.core.Timeline.prototype,['to','from','fromTo','set']);})();
gsap.set('.lid',{scaleY:0,transformOrigin:'50% 0%'});
function blink(sel,times){times.forEach(t=>tl.to(sel,{scaleY:1,duration:.06,yoyo:true,repeat:1,ease:'none'},t));}
function count(sel,from,to,start,dur,fmt){const o={v:from};tl.to(o,{v:to,duration:dur,ease:'power2.out',onUpdate:()=>{document.querySelector(sel).textContent=fmt(o.v)}},start);}
const usd=v=>'$'+Math.round(v).toLocaleString('en-US')+'.00';
// walk(prefix, wrapSel, start, steps, stepDur, dx): Maya-style walk cycle (from the pilot) — legs/arms swing
// about hip (150 330) / shoulder (150 204), upper body bobs, wrapper travels dx px, limbs settle at the end.
function walk(p,wrap,start,steps,stepDur,dx){
  tl.fromTo(wrap,{x:0},{x:dx,duration:stepDur*steps,ease:'none'},start);
  for(let i=0;i<steps;i++){const a=i%2?-20:20,t=start+i*stepDur;
    tl.to(`#${p}-leg-front`,{rotation:a,svgOrigin:'150 330',duration:stepDur,ease:'sine.inOut'},t);
    tl.to(`#${p}-leg-back`,{rotation:-a,svgOrigin:'150 330',duration:stepDur,ease:'sine.inOut'},t);
    tl.to(`#${p}-arm-front`,{rotation:-a*.8,svgOrigin:'150 204',duration:stepDur,ease:'sine.inOut'},t);
    tl.to(`#${p}-arm-back`,{rotation:a*.8,svgOrigin:'150 204',duration:stepDur,ease:'sine.inOut'},t);
    tl.to(`#${p}-upper`,{y:-7,duration:stepDur/2,yoyo:true,repeat:1,ease:'sine.inOut'},t);}
  const end=start+steps*stepDur;
  [`#${p}-leg-front`,`#${p}-leg-back`].forEach(s=>tl.to(s,{rotation:0,svgOrigin:'150 330',duration:.25,ease:'power2.out'},end));
  [`#${p}-arm-front`,`#${p}-arm-back`].forEach(s=>tl.to(s,{rotation:0,svgOrigin:'150 204',duration:.25,ease:'power2.out'},end));
  return end+.25;
}
// talk(mouthSel, start, flaps): simple mouth flaps for a speech bubble (not phoneme lip-sync).
function talk(sel,start,flaps){tl.to(sel,{scaleY:.4,transformOrigin:'50% 50%',duration:.09,yoyo:true,repeat:flaps*2-1,ease:'none'},start);}
// stamp(cardSel, stampSel, t): APPROVED-style stamp slam with card shake.
function stamp(card,mark,t){tl.fromTo(mark,{opacity:0,scale:2.6},{opacity:1,scale:1,duration:.16,ease:'power4.in'},t);
  tl.fromTo(card,{x:0},{x:6,duration:.05,yoyo:true,repeat:5,ease:'none'},t+.16);}
// Determinism: two tweens of one property on one element that overlap in time resolve by render order — GSAP renders
// a timeline's children in start order when the playhead moves forward and in reverse order when it moves backward,
// so the frame would depend on the direction of the last seek. Rule: the later-starting tween takes over. Each earlier
// tween is clipped at the next one's start by scrubbing it in its own sub-timeline (the curve up to the cut is
// unchanged). Called by kit.assemble after all scene code. Returns the number of tweens clipped.
function __elResolveOverlaps(tl) {
  const SKIP = new Set(['duration', 'ease', 'delay', 'repeat', 'repeatDelay', 'yoyo', 'yoyoEase', 'immediateRender', 'overwrite',
    'smoothOrigin', 'transformOrigin', 'svgOrigin', 'stagger', 'startAt', 'id', 'callbackScope', 'runBackwards', 'paused', 'data',
    'lazy', 'inherit', 'keyframes', 'force3D', 'parent']);
  const props = tw => { const v = tw.vars, ks = [];
    Object.keys(v).forEach(k => { if (SKIP.has(k) || k.startsWith('on')) return; if (k === 'attr' && v.attr) Object.keys(v.attr).forEach(a => ks.push('attr.' + a)); else ks.push(k); });
    return ks; };
  const chans = new Map();                                   // element → prop → [tween]
  tl.getChildren(false, true, false).forEach(tw => {
    if (!tw.duration() || tw.repeat() < 0) return;
    const tg = tw.targets(); if (tg.length !== 1 || !(tg[0] instanceof Element)) return;
    const m = chans.get(tg[0]) || new Map(); chans.set(tg[0], m);
    props(tw).forEach(p => { if (!m.has(p)) m.set(p, []); m.get(p).push(tw); });
  });
  const cut = new Map();                                     // tween → clip length (s)
  chans.forEach(m => m.forEach(list => {
    list.sort((a, b) => a.startTime() - b.startTime());
    for (let i = 0; i + 1 < list.length; i++) {
      const a = list[i], s = a.startTime(), e = s + a.totalDuration();
      const nxt = list.slice(i + 1).find(b => b.startTime() > s + 1e-6);
      if (nxt && nxt.startTime() < e - 1e-6) cut.set(a, Math.min(cut.get(a) ?? Infinity, nxt.startTime() - s));
    }
  }));
  cut.forEach((len, tw) => {
    const s = tw.startTime(); tl.remove(tw);
    const sub = gsap.timeline({ paused: true }); sub.add(tw, 0);
    tl.add(sub.tweenFromTo(0, len, { ease: 'none', duration: len, immediateRender: false }), s);
  });
  return cut.size;
}
