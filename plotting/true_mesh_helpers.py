"""Existing geometry-only plotting: actual trimmed knots and STRI65 topology."""
from pathlib import Path
import json,hashlib
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bound(ref):
 base=Path(__file__).resolve().parent;p=(base/Path(ref['path'])).resolve();assert p.is_relative_to(base)and p.is_file()and p.stat().st_size==ref['bytes'];assert H(p)==ref['sha256'];return p
def locate(point,poly):
 x,y=point;inside=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ax,ay=a;bx,by=b;cross=(x-ax)*(by-ay)-(y-ay)*(bx-ax)
  if cross==0 and min(ax,bx)<=x<=max(ax,bx)and min(ay,by)<=y<=max(ay,by):return 0
  if(ay>y)!=(by>y)and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
 return 1 if inside else -1
def clip_iso_intervals(axis,fixed,minimum,maximum,outer,holes):
 """Exact supplied-float polygon edges; no snap, interpolation of fields or grid sampling."""
 cuts={float(minimum),float(maximum)}
 for poly in[outer,*holes]:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if a[axis]==b[axis]:
    if fixed==a[axis]:cuts.update([float(a[1-axis]),float(b[1-axis])])
   elif min(a[axis],b[axis])<=fixed<=max(a[axis],b[axis]):
    t=(fixed-a[axis])/(b[axis]-a[axis]);cuts.add(float(a[1-axis]+t*(b[1-axis]-a[1-axis])))
 cuts=sorted(x for x in cuts if minimum<=x<=maximum);out=[]
 for a,b in zip(cuts,cuts[1:]):
  if a==b:continue
  mid=(a+b)/2;p=[fixed,mid]if axis==0 else[mid,fixed]
  if locate(p,outer)>=0 and all(locate(p,h)<=0 for h in holes):out.append((a,b))
 return out
def knot_lines(refs):
 import numpy as np
 from scipy.interpolate import BSpline
 all_lines=[];owners=[];counts=[]
 for ref in refs:
  d=json.loads(bound(ref).read_text());nu=int(d['controls_u']);nv=int(d['controls_v']);cp=np.array(d['control_global_Vg']).reshape(nu,nv,3);wt=np.array(d['weights']).reshape(nu,nv);hom=np.concatenate([cp*wt[:,:,None],wt[:,:,None]],axis=2);ku=np.array(d['knots_u']);kv=np.array(d['knots_v']);pu=int(d['degree_u']);pv=int(d['degree_v']);U=np.unique(ku[pu:-pu]);V=np.unique(kv[pv:-pv]);outer=d['outer_loop']or[[U[0],V[0]],[U[-1],V[0]],[U[-1],V[-1]],[U[0],V[-1]]]
  start=len(all_lines)
  for axis,values,other in[(0,U,V),(1,V,U)]:
   for fixed in values:
    for lo,hi in clip_iso_intervals(axis,fixed,other[0],other[-1],outer,d['hole_loops']):
     t=np.unique(np.r_[lo,other[(other>lo)&(other<hi)],hi])
     if len(t)<2:continue
     if axis==0:h=BSpline(ku,hom,pu,axis=0)(fixed);q=BSpline(kv,h,pv,axis=0)(t)
     else:h=BSpline(kv,hom,pv,axis=1)(fixed);q=BSpline(ku,h,pu,axis=0)(t)
     q=q[:,:3]/q[:,3,None]
     all_lines.extend(np.stack([q[:-1],q[1:]],axis=1));owners.extend([int(d['shell_handle'])]*(len(q)-1))
  counts.append(dict(owner=d['shell_handle'],controls=nu*nv,knot_u=len(U),knot_v=len(V),trimmed_segments=len(all_lines)-start,all_registered_trim_retained=True))
 return np.asarray(all_lines),np.asarray(owners),counts
def FE_mesh(ref):
 import numpy as np
 p=bound(ref);nodes={};elements=[];mode=None;inpart=False;instance=False
 with p.open()as f:
  for line in f:
   s=line.strip()
   if not s or s.startswith('**'):continue
   if s.startswith('*'):
    up=s.upper()
    if up.startswith('*PART,'):inpart=True
    elif up.startswith('*END PART'):inpart=False
    if up.startswith('*INSTANCE,'):instance=True;mode='INSTANCE';continue
    if up.startswith('*END INSTANCE'):instance=False
    mode='NODE'if inpart and up=='*NODE'else'ELEMENT'if inpart and up.startswith('*ELEMENT')and'TYPE=STRI65'in up else None
    continue
   if instance:raise ValueError('Instance transform needs explicit display adapter; not silently ignored')
   if mode=='NODE':v=s.split(',');nodes[int(v[0])]=[float(x)for x in v[1:4]]
   elif mode=='ELEMENT':v=[int(x)for x in s.split(',')if x.strip()];assert len(v)==7;elements.append(v[1:])
 labels=np.array(sorted(nodes));xyz=np.array([nodes[int(i)]for i in labels]);conn=np.searchsorted(labels,np.asarray(elements,dtype='int64'));assert np.array_equal(labels[conn],np.asarray(elements));corners=xyz[conn[:,:3]]
 edges=np.concatenate([conn[:,[0,3,1]],conn[:,[1,4,2]],conn[:,[2,5,0]]]);ids=np.sort(edges[:,[0,2]],axis=1);_,idx=np.unique(ids,axis=0,return_index=True);edges=edges[np.sort(idx)];polylines=xyz[edges];segments=np.concatenate([polylines[:,:2],polylines[:,1:]],axis=0)
 return segments,corners,dict(nodes=len(labels),elements=len(conn),unique_T6_edges=len(edges),complete_mesh=True,coordinate_merging=False)
def mesh(cfg,family,role,root):
 import numpy as np
 out=Path(root)/'geometry_cache';out.mkdir(exist_ok=True);p=out/f'{family}_{role}.npz';meta=p.with_suffix('.json')
 if p.exists():
  m=json.loads(meta.read_text());assert H(p)==m['npz_sha256'];z=np.load(p,allow_pickle=False);return z['segments'],z['faces'],m
 if role=='native':
  seg,owner,counts=knot_lines(cfg['true_mesh']['geometries'][family]);faces=np.empty((0,3,3));m=dict(role='actual_registered_trim_knot_spans',counts=counts,source=cfg['true_mesh']['geometries'][family])
 else:seg,faces,counts=FE_mesh(cfg['true_mesh']['FE_h2'][family]);m=dict(role='actual_complete_STRI65_h2_mesh',counts=counts,source=cfg['true_mesh']['FE_h2'][family])
 np.savez_compressed(p,segments=seg,faces=faces);m.update(npz_sha256=H(p),segments=len(seg));meta.write_text(json.dumps(m,indent=2)+'\n');return seg,faces,m
def project_segments(ax,segments):
 import numpy as np
 from mpl_toolkits.mplot3d import proj3d
 disp=segments[:,:,[2,0,1]];x,y,z=proj3d.proj_transform(*disp.reshape(-1,3).T,ax.get_proj());return np.stack([x,y],axis=1).reshape(-1,2,2)
def add_lines(ax,segments,linewidth=.03,alpha=.25):
 from matplotlib.collections import LineCollection
 ax.computed_zorder=False;c=LineCollection(project_segments(ax,segments),colors=[(0,0,0,alpha)],linewidths=linewidth,rasterized=True,zorder=3);c.do_3d_projection=lambda:0.;ax.add_collection(c);return c
def FE_faces(ax,faces):
 import numpy as np
 from mpl_toolkits.mplot3d import proj3d
 from matplotlib.collections import PolyCollection
 d=faces[:,:,[2,0,1]];x,y,z=proj3d.proj_transform(*d.reshape(-1,3).T,ax.get_proj());v=np.stack([x,y],axis=1).reshape(-1,3,2);order=np.argsort(z.reshape(-1,3).mean(1))[::-1];c=PolyCollection(v[order],facecolors='#B3B8BC',edgecolors='none',rasterized=True,antialiaseds=False,zorder=1);c.do_3d_projection=lambda:0.;ax.add_collection(c)
def inset(fig,segments,window):
 import numpy as np
 from matplotlib.collections import LineCollection
 cen=np.array(window['center_xyz_mm']);r=window['half_width_mm'];near=np.all(np.abs(segments[:,:,1]-cen[1])<1e-4,axis=1);s=segments[near][:,:,[0,2]];lo=cen[[0,2]]-r;hi=cen[[0,2]]+r;hit=np.all(s.max(1)>=lo,axis=1)&np.all(s.min(1)<=hi,axis=1);s=s[hit];a=fig.add_axes([.025,.715,.27,.26]);a.add_collection(LineCollection(s,color='#252525',lw=.25));a.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),aspect='equal',xticks=[],yticks=[]);a.text(.5,-.10,'40 mm',transform=a.transAxes,ha='center',va='top',fontsize=7.5);return dict(center_xyz_mm=cen.tolist(),half_width_mm=r,all_intersecting_plane_segments=len(s),result_dependent_selection=False)
