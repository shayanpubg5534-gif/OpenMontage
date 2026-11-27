// P10 limited cut-out rig for Open Peeps artwork (the artist's drawing is never redrawn or warped; only rigid pieces of
// it rotate about joints).
//
// A rig spec lists pieces cut from the composed character SVG (root user units):
//   { id, clip: [[x,y]...],   the region of the drawing this piece shows (it may run under neighbouring art)
//         cut:  [[x,y]...],   the region removed from what lies under it at rest (body or parent) so nothing doubles
//         pivot: [x,y],       joint centre
//         z: 'under'|'over',  under: the piece sits beneath the body, so clothing (a cuff, a sleeve) hides the joint;
//                             over: the piece sits above, and a joint disc fills the wedge that opens when it bends
//         disc: {r, fill, stroke, width} (optional), parent: id (optional),
//         caps: [[x,y,r]...] (optional) small round ink caps where a cut meets the artist's outline (a clean corner) }
// Joints are clean by construction: either clothing overlaps the joint (under) or a disc of the limb's own colour and
// line weight is drawn beneath both pieces, so a bend shows a rounded elbow in the artist's line, never a gap.
// The character's own groups (FACE, HEAD, BODY) stay in one shared source, so face swaps and head motion apply to all
// pieces at once.
export function rigSVG(svg, spec, { id = 'r' } = {}) {
  const open = svg.match(/^<svg[^>]*>/)[0], inner = svg.slice(open.length, svg.lastIndexOf('</svg>'));
  const P = pts => pts.map(p => p.join(',')).join(' ');
  const kids = pid => spec.filter(s => (s.parent || null) === pid);
  const defs = [`<g id="${id}_src">${inner}</g>`];
  // cuts are masks (applied to the flattened group) for the same reason as piece regions below
  const maskOf = (mid, cuts) => cuts.length ? (defs.push(`<mask id="${mid}" maskUnits="userSpaceOnUse" x="-1e4" y="-1e4" width="3e4" height="3e4">` +
    `<rect x="-1e4" y="-1e4" width="3e4" height="3e4" fill="#fff"/>${cuts.map(c => `<polygon points="${P(c.cut)}" fill="#000"/>`).join('')}</mask>`), ` mask="url(#${mid})"`) : '';
  const piece = s => {
    // the piece's region is a mask (applied to the flattened group): a clip-path anti-aliases each stacked layer of the
    // artwork separately, so the white base under a fill bleeds through as a light hairline along the edge
    defs.push(`<mask id="${id}_cp_${s.id}" maskUnits="userSpaceOnUse" x="-1e4" y="-1e4" width="3e4" height="3e4"><polygon points="${P(s.clip)}" fill="#fff"/></mask>`);
    const ch = kids(s.id);
    return `<g data-joint="${s.id}" data-pivot="${s.pivot.join(',')}">` +
      ch.filter(c => c.z === 'under').map(piece).join('') +
      `<g mask="url(#${id}_cp_${s.id})"><g${maskOf(`${id}_m_${s.id}`, ch)}><use href="#${id}_src"/></g></g>` +
      ch.filter(c => c.z !== 'under').map(piece).join('') + '</g>';
  };
  const top = kids(null);
  const body = `<g data-joint="body"${maskOf(`${id}_m_body`, top)}><use href="#${id}_src"/></g>`;
  // joint discs sit beneath everything: rotation-invariant, they only show in the wedge a bend opens
  const discs = spec.filter(s => s.disc).map(s => `<circle class="rig-disc" cx="${s.pivot[0]}" cy="${s.pivot[1]}" r="${s.disc.r}" fill="${s.disc.fill}" stroke="${s.disc.stroke || '#1e1b19'}" stroke-width="${s.disc.width || 9}"/>`).join('');
  const out = discs + top.filter(s => s.z === 'under').map(piece).join('') + body + top.filter(s => s.z !== 'under').map(piece).join('');
  const caps = spec.flatMap(s => s.caps || []).map(([x, y, r]) => `<circle class="rig-cap" cx="${x}" cy="${y}" r="${r}" fill="#1e1b19"/>`).join('');
  return `${open}<defs>${defs.join('')}</defs>${out}${caps}</svg>`;
}

// pose the rig: angles {id: degrees} → sets rotate(angle pivot) on each joint group (children inherit their parent's)
export const POSE_JS = `function poseRig(root, angles) {
  for (const g of root.querySelectorAll('[data-joint]')) { const id = g.getAttribute('data-joint'); if (id === 'body') continue;
    const [x, y] = g.getAttribute('data-pivot').split(',').map(Number);
    g.setAttribute('transform', 'rotate(' + (angles[id] || 0).toFixed(3) + ' ' + x + ' ' + y + ')'); } }`;
