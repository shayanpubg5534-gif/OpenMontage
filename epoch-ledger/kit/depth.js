// Epoch Ledger depth layers (pairs with kit/depth.py): a parallax camera for layered plates. Opt-in head script.
// Layers are <div id="{sid}-L{bg|mg|fg}" data-depth="metres">; a move shifts and scales each by the inverse of its depth,
// so near objects slide past faster than far ones and a push-in grows the foreground more than the background.
// Moves are ordinary tweens on the master timeline `tl` (deterministic, seekable). Original implementation.
const DL = {
  // jump to a framing at time t (e.g. the opening frame of a shot) — same parameters as move
  set(sid, t, o) { DL.move(sid, t, 0, o); },
  // truck: metres right (+), rise: metres up (+), dolly: metres forward (+); focal: px per metre at 1 m
  move(sid, t0, d, o) {
    const fx = o.focus || [960, 540];
    document.querySelectorAll(`[id^="${sid}-L"][data-depth]`).forEach(el => {
      const z = +el.dataset.depth, k = (o.focal || 1000) / z;
      const scale = z / Math.max(.2, z - (o.dolly || 0));
      const x = -(o.truck || 0) * k, y = (o.rise || 0) * k;
      // overscan just enough that a shifted layer never reveals its edge
      const over = 1 + 2 * Math.abs(x) / 1920 + 2 * Math.abs(y) / 1080;
      const v = { x, y, scale: scale * over, transformOrigin: `${fx[0]}px ${fx[1]}px` };
      if (d > 0) tl.to(el, Object.assign(v, { duration: d, ease: o.ease || 'sine.inOut' }), t0); else tl.set(el, v, t0);
    });
  },
};
