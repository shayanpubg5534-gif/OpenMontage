// Episode helpers (shared): fades and simple beats on the master timeline `tl`.
function show(sel,t,d){tl.fromTo(sel,{opacity:0},{opacity:1,duration:d||.45,ease:'power2.out'},t);}
function hide(sel,t,d){tl.to(sel,{opacity:0,duration:d||.4,ease:'power2.in'},t);}
function pop(sel,t){tl.fromTo(sel,{opacity:0,scale:.6},{opacity:1,scale:1,duration:.4,ease:'back.out(2.2)'},t);}
function rise(sel,t,dy){tl.fromTo(sel,{opacity:0,y:dy||30},{opacity:1,y:0,duration:.55,ease:'power3.out'},t);}
function drift(sel,t,d,from,to){tl.fromTo(sel,from,Object.assign({duration:d,ease:'sine.inOut'},to),t);}
