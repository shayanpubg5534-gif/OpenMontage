"""P8: render nodes of the Open Peeps Figma file (CC0, Pablo Stanley) to standalone SVG, keeping the artist's own vector
paths and colours, with each body part in its own named group (for rigging).

    python3 epoch-ledger/charlab/p8/peeps_extract.py FILE.fig OUTDIR --frame variations-standing [--each]
--each writes one SVG per child instance (one character each), named after the instance.

Figma semantics implemented (the subset this file uses): frames, groups, instances of symbols with instance swaps
(overriddenSymbolID) and fill/visibility overrides addressed by guid paths; derived symbol data (layout of swapped
parts); vector, boolean and rectangle nodes drawn from their pre-computed fill and stroke geometry (stroke geometry
is already outlined, so it is filled with the stroke paint). Children are ordered by their fractional index.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import figdecode as F  # noqa: E402

K = lambda g: (g['sessionID'], g['localID'])


class Doc:
    def __init__(s, path):
        s.m = F.load(path); s.N = s.m['nodeChanges']; s.blobs = s.m.get('blobs', [])
        s.ids = {K(n['guid']): n for n in s.N}; s.kids = {}
        for n in s.N:
            p = n.get('parentIndex', {}).get('guid')
            if p: s.kids.setdefault(K(p), []).append(n)
        for v in s.kids.values(): v.sort(key=lambda n: n['parentIndex'].get('position', ''))

    def color(s, paints):
        for p in reversed(paints or []):
            if p.get('type') == 'SOLID' and p.get('visible', True):
                c = p['color']; a = c.get('a', 1) * p.get('opacity', 1)
                return '#%02x%02x%02x' % tuple(round(255 * c[k]) for k in 'rgb'), a
        return None, 0

    def geom(s, g):
        return F.commands_to_svg(s.blobs[g['commandsBlob']]['bytes'])

    def mat(s, t):
        return 'matrix(%.4f %.4f %.4f %.4f %.3f %.3f)' % (t['m00'], t['m10'], t['m01'], t['m11'], t['m02'], t['m12'])

    def render(s, node, ov=None, derived=None, depth=0):
        """ov / derived: {path tuple (relative to the innermost instance): override / derived data}."""
        ov = ov or {}; derived = derived or {}
        me = (K(node['guid']),)
        o = ov.get(me, {}); d = derived.get(me, {})
        if not o.get('visible', node.get('visible', True)): return ''
        t = d.get('transform') or node.get('transform')
        attrs = (' transform="%s"' % s.mat(t)) if t and depth else ''
        op = o.get('opacity', node.get('opacity', 1))
        if op < 1: attrs += ' opacity="%.3f"' % op
        name = (node.get('name') or '').replace('"', "'")
        typ = node.get('type')
        if typ == 'INSTANCE':
            sd = node.get('symbolData', {})
            sid = K(o.get('overriddenSymbolID') or sd.get('symbolID'))
            sub_ov = {}
            for x in sd.get('symbolOverrides', []):                   # this instance's own overrides
                sub_ov[tuple(K(g) for g in x['guidPath']['guids'])] = x
            for path, x in ov.items():                              # outer overrides reaching inside (outer wins)
                if len(path) > 1 and path[0] == me[0]: sub_ov[path[1:]] = {**sub_ov.get(path[1:], {}), **x}
            sub_der = {}
            for x in node.get('derivedSymbolData', []) or []:
                sub_der[tuple(K(g) for g in x['guidPath']['guids'])] = x
            for path, x in derived.items():
                if len(path) > 1 and path[0] == me[0]: sub_der[path[1:]] = {**sub_der.get(path[1:], {}), **x}
            sym = s.ids.get(sid)
            if not sym: return ''
            inner = ''.join(s.render(c, sub_ov, sub_der, depth + 1) for c in s.kids.get(sid, []))
            return '<g id="%s" data-symbol="%s"%s>%s</g>' % (name, (sym.get('name') or '').replace('"', "'"), attrs, inner)
        out = []
        if typ in ('VECTOR', 'BOOLEAN_OPERATION', 'ROUNDED_RECTANGLE', 'RECTANGLE', 'ELLIPSE', 'STAR', 'REGULAR_POLYGON'):
            fg = d.get('fillGeometry') or node.get('fillGeometry') or []
            col, a = s.color(o.get('fillPaints', node.get('fillPaints')))
            if col:
                for g in fg:
                    rule = 'evenodd' if g.get('windingRule') == 'ODD' else 'nonzero'
                    out.append('<path d="%s" fill="%s"%s fill-rule="%s"/>' % (s.geom(g), col, '' if a >= 1 else ' fill-opacity="%.3f"' % a, rule))
            sg = d.get('strokeGeometry') or node.get('strokeGeometry') or []
            col, a = s.color(o.get('strokePaints', node.get('strokePaints')))
            if col:
                for g in sg: out.append('<path d="%s" fill="%s"%s/>' % (s.geom(g), col, '' if a >= 1 else ' fill-opacity="%.3f"' % a))
            if typ == 'BOOLEAN_OPERATION':
                return '<g id="%s"%s>%s</g>' % (name, attrs, ''.join(out))
        if typ in ('FRAME', 'GROUP', 'SYMBOL', 'CANVAS', 'BOOLEAN_OPERATION') or not out:
            col, a = s.color(node.get('fillPaints')) if typ == 'FRAME' and depth else (None, 0)
            if col and node.get('size'):
                out.append('<rect width="%.2f" height="%.2f" fill="%s"/>' % (node['size']['x'], node['size']['y'], col))
            out += [s.render(c, ov, derived, depth + 1) for c in s.kids.get(K(node['guid']), [])]
        if typ == 'TEXT': return ''
        return '<g id="%s"%s>%s</g>' % (name, attrs, ''.join(out))

    def svg(s, node):
        w, h = node['size']['x'], node['size']['y']
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.0f" height="%.0f">%s</svg>'
                % (w, h, w, h, s.render(node)))


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    frame = sys.argv[sys.argv.index('--frame') + 1]
    D = Doc(src); fr = next(n for n in D.N if n.get('name') == frame and n.get('type') in ('FRAME', 'SYMBOL'))
    if '--each' in sys.argv:
        for c in D.kids.get(K(fr['guid']), []):
            if c.get('type') != 'INSTANCE': continue
            open(os.path.join(out, (c.get('name') or 'node').replace('/', '_') + '.svg'), 'w').write(D.svg(c))
    open(os.path.join(out, frame.replace('/', '_') + '.svg'), 'w').write(D.svg(fr))
    print('written', out)
