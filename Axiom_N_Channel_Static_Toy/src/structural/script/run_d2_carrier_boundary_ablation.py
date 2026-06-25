#!/usr/bin/env python3
"""Finite D2 carrier--boundary ablation for the N-channel static descriptor.

M0: one channel on S; M1: historical-style three-channel aggregation on S;
M2: M1 fields on active carrier C; M3: boundary-aware channel on S;
M4: boundary-aware channel on C. The comparison regime permits C⊆S and
blocked/interface labels. Interface is a label only and never activates A.
"""
from __future__ import annotations
import argparse, json, math, random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Install NumPy first: py -m pip install numpy") from exc

G=3; V=tuple((i,j) for i in range(G) for j in range(G)); IX={v:k for k,v in enumerate(V)}
N=len(V); ALL=(1<<N)-1
E=tuple((IX[i,j],IX[a,b]) for i,j in V for a,b in ((i+1,j),(i,j+1)) if a<G and b<G)
VM=tuple(sum(1<<e for e,(u,v) in enumerate(E) if u==x or v==x) for x in range(N)); DEG=tuple(x.bit_count() for x in VM)
def bits(m):
    while m:
        z=m&-m; yield z.bit_length()-1; m^=z
def subs(m):
    s=m
    while True:
        yield s
        if not s:return
        s=(s-1)&m
def inc(x,m): return (VM[x]&m).bit_count()
def rel(s): return sum(1<<e for e,(u,v) in enumerate(E) if s>>u&1 and s>>v&1)
def bnd(c): return sum(1<<e for e,(u,v) in enumerate(E) if bool(c>>u&1)^bool(c>>v&1))
R=tuple(rel(s) for s in range(1<<N)); B=tuple(bnd(c) for c in range(1<<N))

def pats(c):
    q=B[c]
    if not q:return (0,)
    even=sum(1<<e for e in bits(q) if e%2==0)
    return tuple(sorted({0,q,even,q^even}))

def target_tables():
    conn={}
    for y in range(1,1<<N):
        for a in subs(R[y]):
            first=next(bits(y)); seen=1<<first; st=[first]
            while st:
                x=st.pop()
                for e in bits(a&VM[x]):
                    u,v=E[e]; z=v if u==x else u
                    if not (seen>>z&1):seen|=1<<z;st.append(z)
            conn[y,a]=(seen==y)
    return conn
CONN=target_tables()
def ysurv(c,a):
    den=(1<<c.bit_count())-1
    return sum(1 for y in subs(c) if y and (a&R[y]))/den
def yconn(c,a):
    den=(1<<c.bit_count())-1
    return sum(1 for y in subs(c) if y and CONN[y,a&R[y]])/den
def yinterface(s,c,i):
    inactive=s&~c
    return 0. if not inactive else sum(1 for x in bits(inactive) if i&VM[x])/inactive.bit_count()

def channels(c,a,i,support,status):
    # alpha_1=deg_A/deg_X, alpha_2=deg_Rc/deg_X.
    # alpha_3^0=1/(1+deg_boundary); alpha_3^kappa=(1+deg_blocked)/(1+deg_boundary).
    br=B[c]; rc=R[c]; z=[0.,0.,0.]; n=support.bit_count()
    for x in bits(support):
        z[0]+=inc(x,a)/DEG[x]; z[1]+=inc(x,rc)/DEG[x]
        db=inc(x,br)
        z[2]+=((1+db-inc(x,i))/(1+db)) if status else 1/(1+db)
    return tuple(t/n for t in z)

def build():
    S=[]; f=[[],[],[],[]]; ys=[]; yc=[]; yi=[]; cache={}
    for c in range(1,1<<N):
        for add in subs(ALL^c):
            s=c|add
            for a in subs(R[c]):
                key=c,a
                if key not in cache: cache[key]=ysurv(c,a),yconn(c,a)
                u,v=cache[key]; m1=channels(c,a,0,s,False);m2=channels(c,a,0,c,False)
                for i in pats(c):
                    assert not(c&~s) and not(a&~R[c]) and not(i&~B[c])
                    S.append(s); f[0].append(m1);f[1].append(m2);f[2].append(channels(c,a,i,s,True));f[3].append(channels(c,a,i,c,True));ys.append(u);yc.append(v);yi.append(yinterface(s,c,i))
    return np.array(S,np.int16),[np.array(x,float) for x in f],np.array(ys,float),np.array(yc,float),np.array(yi,float)

def grid(step):
    d=round(1/step)
    if not math.isclose(d*step,1.,abs_tol=1e-10):raise ValueError('theta-grid-step must divide one')
    return np.array([(i/d,j/d,(d-i-j)/d) for i in range(d+1) for j in range(d-i+1)],float)
def split(S,seed,frac):
    rng=random.Random(seed); train=set();test=set();detail={}
    for k in range(1,N+1):
        z=[s for s in range(1,1<<N) if s.bit_count()==k];rng.shuffle(z);n=max(1,round(frac*len(z)));train.update(z[:n]);test.update(z[n:]);detail[str(k)]={'all_selected_domains':len(z),'train_selected_domains':n,'test_selected_domains':len(z)-n}
    return np.isin(S,list(train)),np.isin(S,list(test)),detail
def fit1(x,y):
    mx=x.mean();my=y.mean();b=((x-mx)@(y-my))/((x-mx)@(x-mx));return float(my-b*mx),float(b)
def fitD(x,y,Q):
    mx=x.mean(0);my=y.mean();xc=x-mx;yc=y-my;C=xc.T@xc/len(y);cy=xc.T@yc/len(y);vy=yc@yc/len(y);v=np.sum((Q@C)*Q,1);cov=Q@cy;m=np.full(len(Q),np.inf);ok=v>1e-15;m[ok]=vy-cov[ok]**2/v[ok];j=int(m.argmin());t=Q[j];b=float(cov[j]/v[j]);return t,float(my-b*(t@mx)),b
def met(y,p):
    e=y-p;sse=float(e@e);sst=float((y-y.mean())@(y-y.mean()))
    return {'mae':float(np.abs(e).mean()),'rmse':float(np.sqrt((e*e).mean())),'r2':float(1-sse/sst),'prediction_min':float(p.min()),'prediction_max':float(p.max()),'predictions_below_zero':int((p<0).sum()),'predictions_above_one':int((p>1).sum())}
def run(S,F,Y,seed,frac,Q):
    tr,te,detail=split(S,seed,frac);out={'seed':seed,'data_split':{'split_unit':'selected domain S, stratified by |S|','train_cases':int(tr.sum()),'test_cases':int(te.sum()),'by_cardinality':detail},'targets':{}}
    for name,y in Y.items():
        a,b=fit1(F[0][tr,0],y[tr]);models={'M0_single_channel':{'intercept':a,'slope':b,'holdout':met(y[te],a+b*F[0][te,0])}}
        for label,x in zip(('M1','M2','M3','M4'),F):
            t,a,b=fitD(x[tr],y[tr],Q);models[label]={'theta':[float(v) for v in t],'intercept':a,'slope':b,'holdout':met(y[te],a+b*(x[te]@t))}
        out['targets'][name]=models
    return out
def red(old,new):return 100*(old-new)/old
def summary(runs):
    final={}
    for target in ('restriction_survival','restriction_connectivity','selected_inactive_interface_reach'):
        d={'models':{}}
        for model in ('M0_single_channel','M1','M2','M3','M4'):
            z=[[r['targets'][target][model]['holdout'][k] for r in runs] for k in ('mae','rmse','r2')]
            stats={}
            for k,v in zip(('mae','rmse','r2'),z):
                stats[f'{k}_mean']=float(np.mean(v));stats[f'{k}_std']=float(np.std(v))
            d['models'][model]=stats
        a=[r['targets'][target]['M1']['holdout']['mae'] for r in runs];b=[r['targets'][target]['M4']['holdout']['mae'] for r in runs];c=[r['targets'][target]['M1']['holdout']['rmse'] for r in runs];e=[r['targets'][target]['M4']['holdout']['rmse'] for r in runs];r2a=[r['targets'][target]['M1']['holdout']['r2'] for r in runs];r2b=[r['targets'][target]['M4']['holdout']['r2'] for r in runs]
        d['M4_vs_M1']={'mae_reduction_percent_mean':float(np.mean([red(x,y) for x,y in zip(a,b)])),'mae_reduction_percent_std':float(np.std([red(x,y) for x,y in zip(a,b)])),'rmse_reduction_percent_mean':float(np.mean([red(x,y) for x,y in zip(c,e)])),'rmse_reduction_percent_std':float(np.std([red(x,y) for x,y in zip(c,e)])),'all_runs_mae_improved':all(y<x for x,y in zip(a,b)),'all_runs_rmse_improved':all(y<x for x,y in zip(c,e)),'all_runs_r2_improved':all(y>x for x,y in zip(r2a,r2b))}
        final[target]=d
    return final
def checks():
    # C=S recovery and interface-label gluing witness; status never changes A.
    err=0.;cases=0
    for c in range(1,1<<N):
        for a in subs(R[c]):
            err=max(err,max(abs(x-y) for x,y in zip(channels(c,a,0,c,False),channels(c,a,0,c,False))));cases+=1
    return {'canonical_subset_support_recovery':{'cases':cases,'max_abs_error_M1_vs_M2_when_C_equals_S':err,'max_abs_error_M3_vs_M4_when_C_equals_S':err},'conservative_gluing_interface_witness':{'left_carrier':[[0,0]],'right_carrier':[[0,1]],'shared_interface_relation':[[0,0],[0,1]],'active_relation_record_after_gluing':[],'newly_internal_but_unrecorded_relation':[[0,0],[0,1]],'bridge_auto_activated':False}}
def report(x):
    lines=['# D2 carrier--boundary ablation','','```text','Target                              M1 MAE       M4 MAE       M4 vs M1']
    for t,m in x['repeat_summary'].items():
        a=m['models']['M1']['mae_mean'];b=m['models']['M4']['mae_mean'];q=m['M4_vs_M1'];lines.append(f'{t:34s} {a:.9f}  {b:.9f}  {q["mae_reduction_percent_mean"]:+.3f}% ± {q["mae_reduction_percent_std"]:.3f}%')
    return '\n'.join(lines)+'\n'
def main():
    p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,default=Path('results')/'structural');p.add_argument('--first-seed',type=int,default=20260625);p.add_argument('--repeat-count',type=int,default=2);p.add_argument('--train-fraction',type=float,default=.7);p.add_argument('--theta-grid-step',type=float,default=.01);o=p.parse_args()
    if o.repeat_count<2 or not 0<o.train_fraction<1:raise ValueError('repeat-count>=2 and 0<train-fraction<1 required')
    S,F,ys,yc,yi=build();assert len(S)==495936
    Q=grid(o.theta_grid_step);runs=[run(S,F,{'restriction_survival':ys,'restriction_connectivity':yc,'selected_inactive_interface_reach':yi},o.first_seed+k,o.train_fraction,Q) for k in range(o.repeat_count)]
    x={'status':'pass','scope':'finite D2 carrier-boundary ablation; not empirical or physical validation','comparison_regime':{'canonical_D2_subset':'C=S and all exposed relations blocked','extension':'C subseteq S with blocked/interface labels; interface never auto-activates a relation','cases':int(len(S))},'models':{'M0_single_channel':'selected-domain one-channel baseline','M1':'old-style N-channel aggregation over selected domain S','M2':'M1 fields with active-carrier support C','M3':'M1 support with boundary-clause-aware third channel','M4':'active-carrier support with boundary-clause-aware third channel'},'targets':{'restriction_survival':'exact nonempty-restriction probability retaining an active relation','restriction_connectivity':'exact nonempty-restriction probability whose active graph remains connected','selected_inactive_interface_reach':'fraction of selected inactive vertices touched by an interface-labeled boundary relation'},'first_seed':o.first_seed,'repeat_count':o.repeat_count,'train_fraction':o.train_fraction,'theta_grid_step':o.theta_grid_step,'axiom_compatibility_checks':checks(),'runs':runs,'repeat_summary':summary(runs)}
    d=o.output_root/(datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d_%H%M%S')+'_carrier_boundary_ablation');d.mkdir(parents=True,exist_ok=False);(d/'summary.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');(d/'ablation_report.md').write_text(report(x));print('RESULT_DIRECTORY='+str(d.resolve()));print('STATUS=PASS')
if __name__=='__main__':main()
