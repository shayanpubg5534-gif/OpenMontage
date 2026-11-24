// Epoch Ledger timeline helpers (expects `tl` = the paused master timeline).
// blink(sel, times): eyelid blinks · count(sel, from, to, start, dur, fmt): number count-up · usd(v): $1,234.00
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
