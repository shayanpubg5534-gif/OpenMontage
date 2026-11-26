// Character lab (P3): a restrained conversational performance library.
//
// An actor may list "perform": [{ "do": "<preset>", "t": seconds, ...options }]. Each preset expands into the
// compiler's ordinary tracks (face keys, gaze keys, gestures, hand poses, IK reaches), so everything stays compatible
// with motion, gaze, blinks, expressions and lip sync, and a shot can still add hand-written keys alongside.
//
// Direction rules baked in (documentary, not theatre): small amplitudes; one idea per gesture; hands return to rest;
// expressions ease in over 0.4–0.8 s and settle back to the actor's resting face; nothing loops on a fixed period.
//
// Context (actor "performCtx"): posture "stand" | "sit", listener [x,y,z] (whom they talk to; default: the camera side),
// desk height, restHands 'lap' | 'desk' (seated hands between gestures; needs duration), restFace (the face the actor settles back to, default a faint warm smile).

const S = { stand: { chest: 1.2, waist: 1.02, fwd: .33 }, sit: { chest: .98, waist: .82, fwd: .36 } };
const sideSign = s => (s === 'r' ? 1 : -1);   // local x: + is the actor's right (elmotion reach "local" frame)

export const PRESETS = {
  // ── listening and reactions ───────────────────────────────────────────────────────────────────────────────────
  listen: (o, C) => ({ face: [k(o.t, { ...C.rest, 'eyebrows-left-inner-up': .14, 'eyebrows-right-inner-up': .14 }, .7)],
    gestures: [{ t: o.t + (o.nodAt ?? 1.1), type: 'nod', amp: 2.4, dur: .8, count: o.double ? 2 : 1 }],
    look: C.listener ? [{ t: o.t, target: C.listener, w: .8 }] : [] }),
  nod: (o) => ({ gestures: [{ t: o.t, type: 'nod', amp: o.amp ?? 3.2, dur: o.dur ?? .8, count: o.count ?? 1 }] }),
  // a gaze shift away and back: thinking, recalling, not avoiding
  glance: (o, C) => ({ look: [{ t: o.t, target: o.to || C.aside, w: .65, blink: true }, { t: o.t + (o.dur ?? .9), target: o.back || C.listener, w: .8, blink: o.blinkBack ?? false }] }),

  // ── expressions (ease in, hold, settle back to the resting face) ──────────────────────────────────────────────
  concern: (o, C) => hold(o, C, { 'eyebrows-left-inner-up': .5, 'eyebrows-right-inner-up': .5, 'mouth-depression': .16, 'eyes-compressed': .12 },
    [{ t: o.t + .2, type: 'nod', amp: -1.6, dur: (o.dur ?? 2) * .8 }]),          // the head sinks a little (a negative nod)
  uncertain: (o, C) => hold(o, C, { 'eyebrows-left-inner-up': .42, 'eyebrows-right-inner-up': .16, 'mouth-compression': .28, 'mouth-narrow': .1 },
    [{ t: o.t + .1, type: 'tilt', amp: (o.dir ?? 1) * 4.5, dur: (o.dur ?? 2) + .4 }, { t: o.t + .35, type: 'shrug', amp: 2.2, dur: .9 }],
    o.glance !== false ? [{ t: o.t + .15, target: C.aside, w: .55, blink: true }, { t: o.t + (o.dur ?? 2) * .7, target: C.listener, w: .8 }] : []),
  relief: (o, C) => hold(o, C, { 'eyes-relaxed': .45, 'mouth-corner-puller': .26, 'eyebrows-left-inner-up': .12, 'eyebrows-right-inner-up': .12 },
    [{ t: o.t, type: 'shrug', amp: -3, dur: 1.6 }, { t: o.t + .9, type: 'nod', amp: 2.2, dur: .8 }]),   // an exhale: shoulders settle
  thoughtful: (o, C) => hold(o, C, { 'eyes-cocky': .2, 'mouth-compression': .22, 'eyebrows-left-down': .12, 'eyebrows-right-down': .12 },
    [{ t: o.t + .2, type: 'tilt', amp: (o.dir ?? -1) * 3, dur: (o.dur ?? 2.2) + .3 }],
    [{ t: o.t, target: o.to || C.asideLow, w: .6, blink: true }, { t: o.t + (o.dur ?? 2.2) * .8, target: C.listener, w: .8 }]),
  warm: (o, C) => ({ face: [k(o.t, { ...C.rest, 'mouth-corner-puller': .2 }, .6)] }),

  // ── hands (palm orientation is explicit: the converted rigs rest in a T-pose, see elmotion hand frames) ────────
  // palm-up explanatory gesture, one hand, near the body, at chest-to-waist height; returns to rest
  explain: (o, C) => { const s = o.side || 'r', g = sideSign(s), P = S[C.posture], d = o.dur ?? 1.2;
    return { hands: [{ t: o.t, side: s, pose: 'present', dur: .35 }, { t: o.t + d + .1, side: s, pose: 'relaxed', dur: .45 }],
      reach: [{ side: s, t0: o.t, in: .5, t1: o.t + d, out: .65, local: [g * (o.out ?? .16), (P.chest + P.waist) / 2 + (o.lift ?? 0), P.fwd + (o.fwd ?? 0)],
        fd: [g * .35, .12, 1], pn: [-g * .3, 1, .05] }],
      gestures: o.beat !== false ? [{ t: o.t + d * .45, type: 'nod', amp: 1.8, dur: .6 }] : [] }; },
  // both palms open, low and small: "what else could I do?" (uncertainty, candour)
  open_hands: (o, C) => { const P = S[C.posture], d = o.dur ?? 1.3, r = { hands: [], reach: [] };
    for (const s of ['l', 'r']) { const g = sideSign(s);
      r.hands.push({ t: o.t, side: s, pose: 'open', dur: .35 }, { t: o.t + d + .1, side: s, pose: 'relaxed', dur: .45 });
      r.reach.push({ side: s, t0: o.t, in: .55, t1: o.t + d, out: .7, local: [g * .2, P.waist + .06, P.fwd - .02], fd: [g * .45, .05, 1], pn: [-g * .45, 1, 0] }); }
    r.gestures = [{ t: o.t + .2, type: 'shrug', amp: 2.6, dur: .9 }]; return r; },
  // seated: forearms on the desk, palms down, relaxed (listening at a desk)
  hands_on_desk: (o, C) => { const r = { hands: [], reach: [] }, d = o.dur ?? 3;
    for (const s of o.side ? [o.side] : ['l', 'r']) { const g = sideSign(s);
      r.hands.push({ t: o.t, side: s, pose: 'relaxed', dur: .4 });
      r.reach.push({ side: s, t0: o.t, in: .7, t1: o.t + d, out: .7, local: [g * (o.out ?? .19), (C.desk ?? .76) + .025, o.fwd ?? .42], fd: [-g * .2, 0, 1], pn: [0, -1, 0] }); }
    return r; },
};

const k = (t, e, dur = .6) => ({ t, e, dur });
function hold(o, C, e, gestures = [], look = []) {
  const d = o.dur ?? 2, a = o.amount ?? 1, E = { ...C.rest }; for (const [n, v] of Object.entries(e)) E[n] = v * a;
  return { face: [k(o.t, E, o.in ?? .6), k(o.t + d, { ...C.rest }, o.out ?? .8)], gestures, look };
}

// expand an actor's "perform" list into ordinary tracks (merged with any hand-written keys, sorted by time)
export function expandPerformance(actor, defaults = {}) {
  if (!actor.perform) return actor;
  const ctx = { posture: 'stand', rest: { 'mouth-corner-puller': .1 }, ...defaults, ...(actor.performCtx || {}) };
  ctx.listener = ctx.listener || [0, 1.5, 3.5];
  ctx.aside = ctx.aside || [ctx.listener[0] - 1.4, ctx.listener[1] + .15, ctx.listener[2] - 1];
  ctx.asideLow = ctx.asideLow || [ctx.listener[0] - 1.1, ctx.listener[1] - .55, ctx.listener[2] - 1.2];
  const out = { face: [], look: [], gestures: [], hands: [], reach: [] };
  for (const p of actor.perform) { const f = PRESETS[p.do]; if (!f) throw new Error('perflib: unknown preset ' + p.do);
    const r = f(p, ctx); for (const key of Object.keys(out)) if (r[key]) out[key].push(...r[key]); }
  // resting hands between gestures (seated: on the thighs, palms down) so the mocap clip's own hands never hover
  if (ctx.restHands && ctx.duration) for (const s of ['l', 'r']) { const g = sideSign(s);
    const busy = [...(actor.reach || []), ...out.reach].filter(R => R.side === s).sort((a, b) => a.t0 - b.t0);
    const rest = ctx.restHands === 'desk' ? { local: [g * .19, (ctx.desk ?? .76) + .025, .42], fd: [-g * .2, 0, 1], pn: [0, -1, 0] }
      : { local: [g * .11, ctx.lapY ?? .64, .3], fd: [-g * .12, -.25, 1], pn: [-g * .1, -1, 0] };
    let from = 0, fin = .01;
    for (const R of [...busy, { t0: ctx.duration + 1, in: .01 }]) {
      if (R.t0 - from > .4) out.reach.push({ side: s, t0: from, in: fin, t1: R.t0, out: R.in ?? .6, ...rest });
      from = R.t1 ?? from; fin = R.out ?? .6; }
    out.hands.push({ t: 0, side: s, pose: 'relaxed' }); }
  for (const key of Object.keys(out)) {
    const merged = [...(actor[key] || []), ...out[key]].sort((a, b) => (a.t ?? a.t0) - (b.t ?? b.t0));
    if (merged.length) actor[key] = merged; }
  if (!actor.face || !actor.face.length || actor.face[0].t > 0) actor.face = [k(0, { ...ctx.rest }, .01), ...(actor.face || [])];
  return actor;
}
