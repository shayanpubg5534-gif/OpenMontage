"""P8: read a Figma .fig file ("fig-kiwi" container) without Figma: schema + message → Python dicts; vector blobs → SVG paths.

    python3 epoch-ledger/charlab/p8/figdecode.py FILE.fig --list            # top-level frames
Used by peeps_extract.py. Pure Python (zlib only). Format: 'fig-kiwi' + u32 version + chunks [u32 len + raw-deflate data]:
chunk 0 = Kiwi binary schema, chunk 1 = the document message encoded with that schema, (chunk 2 = thumbnail PNG).
"""
import struct
import sys
import zlib


class R:
    def __init__(s, b): s.b, s.i = b, 0
    def byte(s): v = s.b[s.i]; s.i += 1; return v
    def vu(s):
        v = sh = 0
        while True:
            c = s.byte(); v |= (c & 127) << sh; sh += 7
            if c < 128: return v
    def vi(s): v = s.vu(); return (v >> 1) ^ -(v & 1)
    def f(s):
        c = s.byte()
        if c == 0: return 0.0
        bits = c | (s.byte() << 8) | (s.byte() << 16) | (s.byte() << 24)
        bits = ((bits << 23) | (bits >> 9)) & 0xFFFFFFFF
        return struct.unpack('<f', struct.pack('<I', bits))[0]
    def s(s):
        j = s.b.index(0, s.i); v = s.b[s.i:j].decode('utf8', 'replace'); s.i = j + 1; return v
    def bytes_(s): n = s.vu(); v = s.b[s.i:s.i + n]; s.i += n; return v


def parse_schema(b):
    r = R(b); defs = []
    for _ in range(r.vu()):
        name = r.s(); kind = r.byte(); fields = []
        for _ in range(r.vu()):
            fn = r.s(); t = r.vi(); arr = r.byte(); val = r.vu(); fields.append((fn, t, arr, val))
        defs.append((name, kind, fields))
    return defs


PRIM = {-1: 'bool', -2: 'byte', -3: 'int', -4: 'uint', -5: 'float', -6: 'string', -7: 'int64', -8: 'uint64'}


def decode(defs, r, di):
    name, kind, fields = defs[di]
    if kind == 0:                                  # enum
        v = r.vu(); return next((f[0] for f in fields if f[3] == v), v)
    def val(t):
        if t >= 0: return decode(defs, r, t)
        p = PRIM[t]
        if p == 'bool': return bool(r.byte())
        if p == 'byte': return r.byte()
        if p == 'int': return r.vi()
        if p in ('uint', 'uint64'): return r.vu()
        if p == 'int64': return r.vi()
        if p == 'float': return r.f()
        if p == 'string': return r.s()
    def field(t, arr):
        if arr:
            if t == -2: return r.bytes_()
            return [val(t) for _ in range(r.vu())]
        return val(t)
    out = {}
    if kind == 1:                                  # struct
        for fn, t, arr, _ in fields: out[fn] = field(t, arr)
        return out
    byid = {f[3]: f for f in fields}               # message
    while True:
        k = r.vu()
        if k == 0: return out
        fn, t, arr, _ = byid[k]; out[fn] = field(t, arr)


def load(path):
    b = open(path, 'rb').read(); assert b[:8] == b'fig-kiwi'
    off, ch = 12, []
    while off < len(b):
        n = struct.unpack('<I', b[off:off + 4])[0]; ch.append(b[off + 4:off + 4 + n]); off += 4 + n
    defs = parse_schema(zlib.decompress(ch[0], -15))
    root = next(i for i, d in enumerate(defs) if d[0] == 'Message')
    return decode(defs, R(zlib.decompress(ch[1], -15)), root)


def commands_to_svg(blob):
    """Figma path commands blob → SVG path data (0=Z, 1=M, 2=L, 3=Q, 4=C; float32 coordinates)."""
    i, out = 0, []
    n = {0: 0, 1: 2, 2: 2, 3: 4, 4: 6}
    while i < len(blob):
        c = blob[i]; i += 1
        if c not in n: break
        k = n[c]; v = struct.unpack('<%df' % k, blob[i:i + 4 * k]); i += 4 * k
        out.append('ZMLQC'[c] + (' ' + ' '.join('%.2f' % x for x in v) if k else ''))
    return ' '.join(out)


if __name__ == '__main__':
    m = load(sys.argv[1]); nodes = m['nodeChanges']
    print('nodes', len(nodes), 'blobs', len(m.get('blobs', [])))
    if '--list' in sys.argv:
        from collections import Counter
        print(Counter(n.get('type') for n in nodes).most_common(12))
        ids = {(n['guid']['sessionID'], n['guid']['localID']): n for n in nodes}
        for n in nodes:
            p = n.get('parentIndex', {}).get('guid')
            if p and ids.get((p['sessionID'], p['localID']), {}).get('type') == 'CANVAS':
                print(n.get('type'), repr(n.get('name')), n.get('size'))
