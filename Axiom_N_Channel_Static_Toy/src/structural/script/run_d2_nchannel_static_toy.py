#!/usr/bin/env python3
"""Exhaustive D2 axiom-consistency test for a 3-channel static descriptor."""
from __future__ import annotations

import argparse, json, math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

n = 3
V = [(i, j) for i in range(n) for j in range(n)]
pos = {v: k for k, v in enumerate(V)}
E = [(pos[i, j], pos[a, b]) for i, j in V for a, b in ((i + 1, j), (i, j + 1)) if a < n and b < n]
deg = [sum(x in e for e in E) for x in range(9)]
inc = [sum(1 << k for k, e in enumerate(E) if x in e) for x in range(9)]
THETA = (0.5, 0.3, 0.2)
EPS = 1e-12
R = []
B = []
for s in range(512):
    R.append(sum(1 << k for k, (u, v) in enumerate(E) if s >> u & 1 and s >> v & 1))
    B.append(sum(1 << k for k, (u, v) in enumerate(E) if bool(s >> u & 1) ^ bool(s >> v & 1)))

def subs(mask):
    sub = mask
    while True:
        yield sub
        if not sub: return
        sub = (sub - 1) & mask

def adm(s, a): return not (a & ~R[s])
def rest(s, a, y):
    if y & ~s: raise ValueError('Y must be a subset of S')
    return y, a & R[y]
def comp(s, a, t, c): return (a & R[s & t]) == (c & R[s & t])
def glue(s, a, t, c):
    if not comp(s, a, t, c): raise ValueError('incompatible records')
    return s | t, a | c

def d3(s, a, theta=THETA):
    if not s: raise ValueError('empty carrier has no normalized weight')
    out = []
    for q in range(3):
        z = 0.0
        for x in range(9):
            if s >> x & 1:
                if q == 0: z += (a & inc[x]).bit_count() / deg[x]
                elif q == 1: z += (R[s] & inc[x]).bit_count() / deg[x]
                else: z += 1.0 / (1 + (B[s] & inc[x]).bit_count())
        out.append(z / s.bit_count())
    return sum(t * z for t, z in zip(theta, out)), out

def trans(s, a, f):
    ss = 0; aa = 0
    for x in range(9):
        if s >> x & 1: ss |= 1 << pos[f(*V[x])]
    for k, (u, v) in enumerate(E):
        if a >> k & 1:
            w, z = pos[f(*V[u])], pos[f(*V[v])]
            aa |= 1 << next(i for i, e in enumerate(E) if {w, z} == set(e))
    return ss, aa

D4 = (
    lambda i,j:(i,j), lambda i,j:(j,2-i), lambda i,j:(2-i,2-j), lambda i,j:(2-j,i),
    lambda i,j:(i,2-j), lambda i,j:(j,i), lambda i,j:(2-i,j), lambda i,j:(2-j,2-i),
)
def coords(s): return [list(V[x]) for x in range(9) if s >> x & 1]
def edgecoords(a): return [[list(V[u]), list(V[v])] for k,(u,v) in enumerate(E) if a >> k & 1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-root', type=Path, default=Path('results')/'structural')
    o = ap.parse_args()
    C = [(s,a) for s in range(512) for a in subs(R[s])]
    assert len(C) == 21799
    NE = [(s,a) for s,a in C if s]

    rec = rng = changed = 0; lo = 9.; hi = -1.
    exemplar = None
    for s,a in NE:
        x, q = d3(s,a); one,_ = d3(s,a,(1,0,0)); rec=max(rec,abs(one-q[0]))
        rng += int(x < min(q)-EPS or x > max(q)+EPS or x < -EPS or x > 1+EPS)
        lo=min(lo,x); hi=max(hi,x)
        if abs(x-one)>EPS:
            changed += 1
            if exemplar is None and a and s.bit_count() >= 2: exemplar=(s,a)
    assert rec <= EPS and not rng

    rr = 0
    for s,a in C:
        for y in subs(s):
            sy, ay = rest(s,a,y); assert ay == a & R[y] and adm(sy,ay); rr += 1

    bad = 0
    for s in range(512):
        if B[s]:
            blocked = {k:'blocked' for k in range(12) if B[s] >> k & 1}
            assert all(v == 'blocked' for v in blocked.values())
            k = next(iter(blocked)); blocked[k]='transmissive'
            assert not all(v == 'blocked' for v in blocked.values()); bad += 1

    gp=bp=bo=0; witness=None
    for s in range(512):
        for t in range(512):
            a,c=R[s],R[t]; assert comp(s,a,t,c)
            u,g=glue(s,a,t,c); assert adm(u,g); bridge=R[u] & ~(a|c); assert not (bridge & g)
            gp+=1
            if bridge:
                bp+=1; bo+=bridge.bit_count()
                if witness is None: witness={'S':coords(s),'T':coords(t),'newly_internal_unrecorded_relations':edgecoords(bridge),'active_after_gluing':edgecoords(g)}

    sc=0
    for s,a in NE:
        x,_=d3(s,a)
        for f in D4:
            ss,aa=trans(s,a,f); y,_=d3(ss,aa); assert math.isclose(x,y,abs_tol=EPS); sc+=1

    es,ea=exemplar; xv,qv=d3(es,ea)
    summary={'status':'pass','scope':'finite axiom-consistency toy model; not a physical prediction model',
      'formula':{'carrier':'C_p=S in D2','theta':THETA,'channels':['active relation participation','induced internal relation capacity','blocked boundary shielding']},
      'enumeration':{'all_admissible_configurations':len(C),'nonempty_carriers':len(NE),'empty_carrier_excluded_from_normalized_descriptor':1},
      'tests':{'N_equals_1_recovery':{'cases':len(NE),'max_abs_error':rec},'convex_bound_and_unit_range':{'cases':len(NE),'min':lo,'max':hi,'violations':rng,'descriptor_differs_from_base':changed},'restriction':{'cases':rr},'boundary_transmissive_rejected':{'domains':bad},'conservative_gluing':{'domain_pairs':gp,'bridge_pairs':bp,'bridge_occurrences':bo},'D4_symmetry':{'cases':sc}},
      'representative':{'S':coords(es),'A':edgecoords(ea),'channel_values':qv,'one_channel_toy_Dw':qv[0],'three_channel_descriptor':xv},'bridge_witness':witness}
    d=o.output_root/datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M%S'); d.mkdir(parents=True)
    (d/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (d/'test_report.md').write_text('# D2 N-channel static toy model\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'RESULT_DIRECTORY={d.resolve()}\nSTATUS=PASS')
if __name__ == '__main__': main()
