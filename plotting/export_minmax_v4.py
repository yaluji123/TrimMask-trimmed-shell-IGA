"""One native figure asset from frozen plot data. No solve/field evaluation/ODB/replay.

Default plan. Each invocation exports exactly one panel on its own Figure canvas.
No existing combined PNG is opened or cropped. Original model PNGs are exact whole
source media and are separately labelled setup schematics, never current final meshes.
"""
from pathlib import Path
import argparse,csv,json,hashlib,sys,os,collections,math,importlib.util
csv.field_size_limit(16<<20) # frozen projection CSV retains long provenance JSON fields.
for key in['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[key]='1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def read(path):
 p=(HERE/Path(path)).resolve();assert p.is_relative_to(HERE);return json.loads(p.read_text(encoding='utf-8-sig'))
def rows(path):
 with Path(path).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def bound(ref):
 p=(HERE/Path(ref['path'])).resolve();assert p.is_relative_to(HERE)and p.is_file()and p.stat().st_size==ref['bytes']and sha(p)==ref['sha256'];return p
def budget():
 p=HERE/'resource_guard.py';assert sha(p)=='837ab5e8caab3828bc7777a6beb24e6a0f631de99897d3b3a98531617305b6a6'
 s=importlib.util.spec_from_file_location('single_plot_resource_only',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.LIMIT=8<<30;cap=g.install()
 import ctypes
 k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
 return cap
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--panel',required=True);p.add_argument('--out',type=Path);p.add_argument('--execute-render',action='store_true');a=p.parse_args()
 if not a.execute_render:print(json.dumps({'status':'PLAN_ONLY_NATIVE_SINGLEPANEL_NO_RENDER','panel':a.panel}));return
 assert a.out is not None and a.out.resolve().is_relative_to(HERE)and not a.out.exists();cap=budget();cfg=read(HERE/'PLOT_INPUTS.json');used=[]
 def B(ref):q=bound(ref);used.append(ref);return q
 import numpy as np,matplotlib
 matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection,LineCollection
 from matplotlib.patches import Polygon,Rectangle,Patch
 from matplotlib.colors import BoundaryNorm
 from matplotlib.ticker import ScalarFormatter,NullFormatter
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 import true_mesh_helpers_v2 as hm
 palette=B(cfg['source_pins']['palette']['snapshot']);s=importlib.util.spec_from_file_location('frozen_abaqus_palette',palette);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
 plt.rcParams.update({'font.family':'Times New Roman','font.size':7.5,'axes.labelsize':7.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.linewidth':.6,'savefig.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
 key=a.panel;fig=None;record={'panel':key,'physical_data_recomputed':False,'combined_PNG_cropped':False,'panel_letters_or_headings_embedded':False,'font_target_pt':7.5,'minimum_required_pt':6.5};width=72;height=65
 def canvas(w=72,h=65,left=.18,right=.97,bottom=.22,top=.95):
  f,ax=plt.subplots(figsize=(w/25.4,h/25.4));f.subplots_adjust(left=left,right=right,bottom=bottom,top=top);return f,ax
 def bar(f,norm,limits,label,rect):
  bx=f.add_axes(rect);cb=f.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=c.abaqus12_matplotlib_banded_colormap()),cax=bx);v=c.abaqus_legend_boundaries(*limits);cb.set_ticks(v);labels=[format(x,'.9g'if i in(0,len(v)-1)else'.4g')for i,x in enumerate(v)];cb.set_ticklabels(labels);record['colorbar_ticks']=list(v);record['colorbar_tick_text']=labels;cb.ax.tick_params(labelsize=7.5,length=2,pad=1.5);bx.set_title(label,loc='left',fontsize=7.5,pad=7);return bx
 def maxtext(f,value,xyz,unit,node_set=False):
  label='node set'if node_set else'sample';f.text(.10,.025,'Min('+label+'): '+format(record['Min'],'.9g')+' '+unit+'\nMax('+label+'): '+format(value,'.9g')+' '+unit+'\nat ('+', '.join(format(x,'.3f')for x in xyz)+') mm',fontsize=7.5,ha='left',va='bottom')
 if key=='F2a':
  height=65;fig,ax=canvas(72,height,left=.22,right=.95,bottom=.25,top=.95);ref=cfg['true_mesh']['triangle_coarse_IGA_geometry'];B(ref);seg,_,counts=hm.knot_lines([ref]);g=read(ref['path']);cp=np.asarray(g['control_global_Vg']).reshape(int(g['controls_u']),int(g['controls_v']),3)
  with np.load(B(cfg['F2']['coarse_P2_npz']),allow_pickle=False)as z:registered_origin=z['origin']
  seg=seg.copy();cp=cp.copy();seg[:,:,:2]-=registered_origin;cp[:,:,:2]-=registered_origin;record['registered_plot_origin_from_P2_npz']=registered_origin.tolist();ax.add_collection(LineCollection(seg[:,:,:2],colors='#454545',linewidths=.35));ax.scatter(cp[:,:,0],cp[:,:,1],s=2,color='#0072B2');poly=np.asarray(seg[:,:,:2]).reshape(-1,2);xmin,ymin=poly.min(0);xmax,ymax=poly.max(0);top=poly[np.argmax(poly[:,1])];ax.plot([xmin,xmax],[ymin,ymin],color='#0072B2',lw=1.4)
  for s in[.15,.4,.65,.9]:at=np.array([xmin,ymin])*(1-s)+top*s;ax.annotate('',xy=(at[0]+.09*(xmax-xmin),at[1]),xytext=at,arrowprops=dict(arrowstyle='-|>',color='#C00000',lw=.8))
  ax.set(aspect='equal',xlim=(xmin-.03*(xmax-xmin),xmax+.03*(xmax-xmin)),ylim=(ymin-.03*(ymax-ymin),ymax+.03*(ymax-ymin)),xlabel='x (mm)',ylabel='y (mm)');fig.text(.18,.025,'300 N/mm along +x\nBottom clamped',fontsize=7.5);record.update(kind='ACTUAL_FIRST_IGA_LEVEL_CONTROL_NET_AND_TRIMMED_KNOT_SPANS',mesh_counts=counts,actual_level=1)
 elif key in['F2b','F2c','F2d']:
  q=cfg['F2'];data=B(q['coarse_P2_npz']if key=='F2b'else q['npz'])
  if key=='F2b':
   with np.load(data,allow_pickle=False)as z:xy=z['points'];conn=z['triangles']
   assert len(xy)==2145 and len(conn)==1024
  else:
   with np.load(data,allow_pickle=False)as z:xy=z['points'];tri=z['triangles'];conn=z['P2_connectivity'];vec=z['IGA_U']if key=='F2c'else z['FEM_U']
   assert len(xy)==525825 and len(tri)==1048576 and len(conn)==262144
  if key=='F2b':
   fig,ax=canvas();edges=xy[conn[:,:3]][:,[0,1,1,2,2,0]].reshape(-1,2,2);ax.add_collection(LineCollection(edges,colors='#666666',linewidths=.08,rasterized=True));xmin,xmax=xy[:,0].min(),xy[:,0].max();ymin,ymax=xy[:,1].min(),xy[:,1].max();ax.plot([xmin,xmax],[ymin,ymin],color='#0072B2',lw=1.4);top=xy[int(np.argmax(xy[:,1]))]
   for t in[.15,.4,.65,.9]:at=np.array([xmin,ymin])*(1-t)+top*t;ax.annotate('',xy=(at[0]+.09*(xmax-xmin),at[1]),xytext=at,arrowprops=dict(arrowstyle='-|>',color='#C00000',lw=.8))
   ax.set_xlim(xmin-.03*(xmax-xmin),xmax+.03*(xmax-xmin));ax.set_ylim(ymin-.03*(ymax-ymin),ymax+.03*(ymax-ymin));ax.set_aspect('equal');ax.set(xlabel='x (mm)',ylabel='y (mm)');fig.text(.18,.025,'300 N/mm along +x\nBottom clamped',fontsize=7.5);record.update(kind='ACTUAL_COMPLETE_P2_FIRST_REFERENCE_LEVEL_SETUP',P2_cells=len(conn),all_nodes_retained_in_source=len(xy),first_reference_level=32,final_contour_reference_nodes_remain=525825)
  else:
   import matplotlib.tri as mtri
   height=72;fig,ax=canvas(72,height,left=.44,right=.98,bottom=.27,top=.94);record.update(plotted_vector_array_sha256=__import__('hashlib').sha256(np.ascontiguousarray(vec).tobytes()).hexdigest(),plotted_array_key='IGA_U'if key=='F2c'else'FEM_U');value=np.linalg.norm(vec,axis=1);limits=[float(value.min()),float(value.max())];norm=BoundaryNorm(c.abaqus_legend_boundaries(*limits),12);ax.tripcolor(mtri.Triangulation(xy[:,0],xy[:,1],tri),value,cmap=c.abaqus12_matplotlib_banded_colormap(),norm=norm,shading='gouraud',rasterized=True);ax.set_aspect('equal');ax.set(xlabel='x (mm)',ylabel='y (mm)');bar(fig,norm,limits,'U, Magnitude\n[mm]',[.025,.31,.022,.56]);i=int(np.argmax(value));j=int(np.argmin(value));record.update(Min=float(value[j]),Min_xyz_mm=xy[j].tolist());maxtext(fig,float(value[i]),xy[i],'mm',True);record.update(kind='FIXED_NODE_DISPLACEMENT_FIELD',points=len(xy),limits=limits,Max=float(value[i]),Max_xyz_mm=xy[i].tolist())
 elif key=='F3a':
  height=35;width=144;fig=plt.figure(figsize=(width/25.4,height/25.4));ax=fig.add_axes([.005,.01,.63,.98],projection='3d');patches=cfg['F3']['patches_from_original_source'];legend=[]
  for label,vertices,color in patches:ax.add_collection3d(Poly3DCollection([vertices],facecolors=color,edgecolors='#303030',lw=.7,alpha=.62));legend.append(Patch(facecolor=color,edgecolor='#303030',label={'P1':'P1 / owner 0: horizontal','P2':'P2 / owner 1: vertical','P3':'P3 / owner 2: inclined'}[label]))
  ax.plot([0,100],[0,0],[0,0],color='#111111',lw=2.4);fig.legend(handles=legend,loc='center left',bbox_to_anchor=(.65,.52),frameon=False,fontsize=7.5);ax.set(xlim=(-7,107),ylim=(-55,68),zlim=(-12,70));ax.set_box_aspect((114,123,82),zoom=1.1);ax.set_proj_type('ortho');ax.view_init(elev=23,azim=-56);ax.set_axis_off();record.update(kind='ORIGINAL_NATIVE_SOURCE_PATCH_ARRANGEMENT_NOT_CROPPED',BC_or_load_graphics=False)
 elif key.startswith('F3'):
  i='bcdefg'.index(key[-1]);keys=['largest_all3_pair_displacement_RMS_mm','largest_all3_pair_common_axis_rotation_RMS_rad','energy_absolute_percent_display','fixed_PATCH2_peak_vector_percent_display','raw_force_relative_L2','raw_common_axis_moment_relative_L2'];labels=['Maximum displacement jump (mm)','Maximum rotation jump (rad)','Energy difference (%)','Peak vector difference (%)','Relative force residual','Relative moment residual'];data=rows(B(cfg['F3']['metrics']));height=57;fig,ax=canvas(72,height,left=.24,bottom=.23,top=.78);v=[float(r[keys[i]])for r in data];upper=max(v)*1.15
  for graph,color,marker,label in zip(['all','1ec2','1ec5','1ec8'],['#0072B2','#D55E00','#009E73','#CC79A7'],['o','s','^','D'],['All relations','Omit 1EC2','Omit 1EC5','Omit 1EC8']):
   part=sorted([r for r in data if r['omit']==graph],key=lambda r:int(r['refinement']));assert len(part)==4;ax.plot([int(r['refinement'])for r in part],[float(r[keys[i]])for r in part],color=color,marker=marker,ms=3,lw=.9,label=label)
  ax.set(xlim=(.8,4.2),ylim=(0,upper),xticks=[1,2,3,4],xlabel='Refinement level',ylabel=labels[i]);fmt=ScalarFormatter(useMathText=False);fmt.set_powerlimits((-3,3));ax.yaxis.set_major_formatter(fmt);ax.yaxis.grid(True,color='#DDDDDD',lw=.35);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.61,.995),ncol=2,frameon=False,handlelength=1.4,columnspacing=.8);record.update(kind='EXISTING_ALL16_METRIC_CURVES',metric=keys[i],points=16)
 elif key in['F4a','F4b']:
  family='triangle'if key=='F4a'else'public_plate';data=sorted([r for r in rows(B(cfg['F4']['table']))if r['family']==family],key=lambda r:int(r['h']));x=[int(r['actual_DOF'])for r in data];y=[float(r['max_U_on_all_fixed_P2_nodes_mm'])for r in data];ref=float(data[0]['finite_P2_node_max_U_mm']);height=65;fig,ax=canvas(72,height,left=.25,bottom=.24,top=.88);ax.plot(x,y,color='#0F4D92',marker='o',ms=3,lw=.9,label='IGA on fixed P2 nodes');ax.axhline(ref,color='#767676',ls=(0,(3,2)),lw=.8,label='Finite P2 reference');ax.set_xscale('log');ax.set_xticks(x,[str(v)for v in x]);ax.xaxis.set_minor_formatter(NullFormatter());ax.set(xlabel='Displacement DOF',ylabel='Maximum |U| on\nreference nodes (mm)');pad=max((max(y+[ref])-min(y+[ref]))*.18,max(y+[ref])*.001);ax.set_ylim(min(y+[ref])-pad,max(y+[ref])+pad);ax.set_xlim(min(x)/1.3,max(x)*1.3)
  for row in data:ax.annotate(row['h']+'×',(int(row['actual_DOF']),float(row['max_U_on_all_fixed_P2_nodes_mm'])),xytext=(0,7 if int(row['h'])==1 else-9),textcoords='offset points',ha='center',va='bottom'if int(row['h'])==1 else'top',fontsize=7.5)
  ax.set_position([.25,.24,.72,.57]);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.61,.995),frameon=False,fontsize=7.5);record.update(kind='EXISTING_REFERENCE_NODE_MAX_CURVE',family=family,all_levels=len(data))
 elif key.startswith('F5')or key.startswith('F6'):
  q=cfg['F5_F6'];g=read(B(q['geometry']));cut=rows(B(q['cut']));cp=np.asarray(g['control_global_Vg']).reshape(-1,3);origin=cp[0];A=cp[(g['controls_u']-1)*g['controls_v']]-origin;Bv=cp[g['controls_v']-1]-origin
  def world(uv):uv=np.asarray(uv);return origin+uv[...,0,None]*A+uv[...,1,None]*Bv
  if key.startswith('F5'):
   k='abc'.index(key[-1]);fig,ax=canvas(72,72,left=.18,bottom=.35 if key[-1]in'ab'else .27,top=.96);accepted=[int(r['acceptedIntegrationPoints'])for r in cut];v=[float(r['activeArea'])/float(r['cellArea'])for r in cut]if k==0 else accepted;limits=[min(v),max(v)]if k<2 else[0,1];norm=BoundaryNorm(c.abaqus_legend_boundaries(*limits),12)
   for cell in g['cells']:u0,u1,v0,v1=cell['bounds'];ax.add_patch(Rectangle((u0,v0),u1-u0,v1-v0,fc='#F2F2F2',ec='#DDDDDD',lw=.15))
   cmap=plt.get_cmap(c.abaqus12_matplotlib_banded_colormap())
   for i,row in enumerate(cut):u0,u1,v0,v1=g['cells'][int(row['element'])]['bounds'];ax.add_patch(Rectangle((u0,v0),u1-u0,v1-v0,fc=cmap(norm(v[i]))if k<2 else'#D55E00',ec='#B0B0B0',lw=.15))
   for hole in g['hole_loops']:ax.add_patch(Polygon(hole,fc='white',ec='#333333',lw=.3))
   for element in[555,556,591,592]:u0,u1,v0,v1=g['cells'][element]['bounds'];ax.add_patch(Rectangle((u0,v0),u1-u0,v1-v0,fc='none',ec='#C00000',lw=.9))
   ax.set(aspect='equal',xlim=(0,1),ylim=(0,1),xticks=[0,.5,1],yticks=[0,.5,1],xlabel='u',ylabel='v')
   if k<2:
    height=72;bx=fig.add_axes([.18,.18,.70,.024]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=c.abaqus12_matplotlib_banded_colormap()),cax=bx,orientation='horizontal');cb.set_ticks([limits[0],(limits[0]+limits[1])/2,limits[1]]);cb.set_ticklabels([format(x,'.9g')for x in[limits[0],(limits[0]+limits[1])/2,limits[1]]]);cb.ax.tick_params(labelsize=7.5);record['limits']=limits;record['Min']=min(v);record['Max']=max(v);record['plotted_scalar_scope']='98 actual cut-cell values; other cells grey uncolored background';fig.text(.10,.015,'Min(cut cells): '+format(min(v),'.9g')+'\nMax(cut cells): '+format(max(v),'.9g'),fontsize=7.5)
   else:fig.text(.18,.035,'Positive fitted7: '+str(len(cut))+' cut cells\nFallback: '+str(sum(int(r['fallback'])for r in cut))+' cells',fontsize=7.5)
   record.update(kind='EXISTING_DIAGNOSTIC_MAP_NOT_PHYSICS',cut_cells=len(cut),categorical_rule_panel=k==2)
  else:
   groups=collections.defaultdict(list)
   for row in rows(B(q['samples'])):groups[int(row['element_id'])].append(row)
   polygons=[];values=[];xy=[]
   for element,group in groups.items():
    verts=sorted([r for r in group if r['sample_kind']=='vertex'],key=lambda r:int(r['local_vertex']));center=[r for r in group if r['sample_kind']=='center'];assert len(center)==1
    if len(verts)==4:verts=[verts[i]for i in[0,1,3,2]]
    polygons.append([[float(r['x']),float(r['y'])]for r in verts]);values.append(float(center[0]['umag']));xy.append([float(center[0]['x']),float(center[0]['y'])])
   width=144;height=77;fig,ax=canvas(width,height,left=.09 if key=='F6a'else .21,bottom=.25,top=.90);norm=BoundaryNorm(c.abaqus_legend_boundaries(float(min(values)),float(max(values))),12);pc=PolyCollection(polygons,facecolors='#E4E4E4'if key=='F6a'else None,edgecolors='#A0A0A0'if key=='F6a'else'none',lw=.15 if key=='F6a'else 0,cmap=c.abaqus12_matplotlib_banded_colormap(),norm=norm,rasterized=True,antialiased=False)
   if key=='F6b':pc.set_array(np.asarray(values))
   ax.add_collection(pc)
   for hole in g['hole_loops']:ax.add_patch(Polygon(world(hole)[:,:2],fc='white',ec='#333333',lw=.3))
   corners=world([[0,0],[1,0],[1,1],[0,1]])[:,:2];ax.add_patch(Polygon(corners,fill=False,ec='black',lw=.5));xmin,ymin=corners.min(0);xmax,ymax=corners.max(0);span=xmax-xmin;ax.plot([xmin,xmin],[ymin,ymax],color='#0072B2',lw=1.4)
   for y in np.linspace(ymin+.2*(ymax-ymin),ymax-.2*(ymax-ymin),3):ax.annotate('',xy=(xmax+.09*span,y),xytext=(xmax,y),arrowprops=dict(arrowstyle='-|>',lw=.8,color='#C00000'))
   ax.set(aspect='equal',xlim=(xmin-.02*span,xmax+.13*span),ylim=(ymin-.03*(ymax-ymin),ymax+.03*(ymax-ymin)),xlabel='x (mm)',ylabel='y (mm)')
   if key=='F6b':bar(fig,norm,[float(min(values)),float(max(values))],'U, Magnitude\n[mm]',[.025,.28,.016,.52]);i=int(np.argmax(values));j=int(np.argmin(values));record.update(Min=values[j],Min_xyz_mm=xy[j]);maxtext(fig,values[i],xy[i],'mm');record.update(Max=values[i],Max_xyz_mm=xy[i],limits=[float(min(values)),float(max(values))])
   record.update(kind='EXISTING_COMPLETE_DISPLAY_POLYGONS_OR_CENTROID_FIELD',polygons=len(polygons),CSV_rows=10280,field_points=2249)
 elif key in['F7a','F7b','F8a','F8b']:
  family='panel'if key.startswith('F7')else'hull';q=cfg['engineering'][family];tr=rows(B(q['triangles']));xyz=np.asarray([[[float(r[ax+str(i)+'_mm'])for ax in'xyz']for i in(1,2,3)]for r in tr]);display=xyz[:,:,[2,0,1]];height=62;fig=plt.figure(figsize=(72/25.4,height/25.4));ax=fig.add_axes([.01,.15,.98,.84],projection='3d');ax.add_collection3d(Poly3DCollection(display,facecolors='#7E858C',edgecolors=[(0,0,0,0)],lw=0,rasterized=True,antialiaseds=False,shade=True));lo=display.reshape(-1,3).min(0);hi=display.reshape(-1,3).max(0);span=hi-lo;pad=.04*max(span);ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),zlim=(lo[2]-pad,hi[2]+pad));ax.set_box_aspect(np.maximum(span,1));ax.set_proj_type('ortho');ax.view_init(elev=35.264389682754654,azim=45);ax.set_axis_off()
  # The geometry is the already retained undeformed carrier; these symbols are
  # setup annotations, never claimed to be current integration/final FE meshes.
  ax.computed_zorder=False;ax.collections[0].set_zorder(1)
  role='native'if key[-1]=='a'else'reference';segments,FEtri,meshmeta=hm.mesh(cfg,family,role,HERE)
  if role=='reference':ax.collections[0].remove();hm.FE_faces(ax,FEtri)
  hm.add_lines(ax,segments,linewidth=.055,alpha=.55);zoom=hm.inset(fig,segments,cfg['true_mesh']['opening_corner_window'][family]);record.update(actual_mesh=meshmeta,opening_window=zoom)
  used.extend(cfg['true_mesh']['geometries'][family]if role=='native'else[cfg['true_mesh']['FE_h2'][family]])
  if family=='panel':
   for end,color in[(lo[0],'#0072B2'),(hi[0],'#C00000')]:
    for y in np.linspace(lo[1],hi[1],5):ax.scatter([end],[y],[lo[2]],marker='x',s=10,color=color,linewidths=.7,depthshade=False,zorder=6)
   fig.text(.03,.025,'End motion: −0.5 mm along z\nBlue: fixed end, red: prescribed end',fontsize=7.5)
  else:
   for k,end in enumerate([lo[0],hi[0]],1):
    center=np.array([end,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2]);corners=np.array([[end,y,z]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]])
    for corner in corners:ax.plot(*np.stack([center,corner]).T,color='#B58500',lw=.5,ls='--'if k==2 else'-',zorder=5)
    from mpl_toolkits.mplot3d import proj3d
    ax.scatter(*center,color='#0072B2',marker='x',s=12,depthshade=False,zorder=6)
    px,py,_=proj3d.proj_transform(*center,ax.get_proj());ax.annotate('RP'+str(k),xy=(px,py),xycoords='data',xytext=(10,16)if k==1 else(-27,-16),textcoords='offset points',fontsize=7.5,color='#202020',zorder=10,bbox=dict(facecolor='white',edgecolor='none',pad=.6))
   fig.text(.03,.025,'End rotations: ±0.0012 rad about z\nEnd sections coupled to reference points',fontsize=7.5)
  record.update(kind='ACTUAL_CURRENT_IGA_TRIMMED_KNOT_MESH_OR_COMPLETE_STRI65H2_MESH_WITH_BC',family=family,geometry_source='complete retained original carrier triangles',display_triangles=len(tr),mesh_type_is_actual_discretization_not_display_carrier=True)
 elif key.startswith('F7')or key.startswith('F8'):
  family='panel'if key.startswith('F7')else'hull';q=cfg['engineering'][family];tr=rows(B(q['triangles']));kind='native_fields'if key[-1]in'ce'or key in('F7delta','F8delta')else'reference_fields';data=rows(B(q[kind]));ct=read(B(q['contract']));assert len(tr)==len(data)==q['points'];assert [r['element_1x']for r in tr]==[r['element_1x']for r in data];xyz=np.asarray([[[float(r[ax+str(i)+'_mm'])for ax in'xyz']for i in(1,2,3)]for r in tr]);display=xyz[:,:,[2,0,1]];delta=key in('F7delta','F8delta');disp=key[-1]in'cd'or delta;value=np.asarray([float(r['U_magnitude_mm'])if disp else max(float(r['SNEG_Mises_MPa']),float(r['SPOS_Mises_MPa']))for r in data]);
  if delta:
   refdata=rows(B(q['reference_fields']));assert [r['element_1x']for r in data]==[r['element_1x']for r in refdata];difference=np.array([[float(r[k])-float(s[k])for k in['ux_mm','uy_mm','uz_mm']]for r,s in zip(data,refdata)]);value=np.linalg.norm(difference,axis=1);record.update(reviewer_only=True,quantity='pointwise |uIGA-uFE|',new_solve_or_resampling=False,all_vector_components_used=True)
  limits=[float(value.min()),float(value.max())];height=72;fig=plt.figure(figsize=(72/25.4,height/25.4));ax=fig.add_axes([.37,.23,.62,.70],projection='3d');norm=BoundaryNorm(c.abaqus_legend_boundaries(*limits),12);ax.add_collection3d(Poly3DCollection(display,facecolors=plt.get_cmap(c.abaqus12_matplotlib_banded_colormap())(norm(value)),edgecolors='none',lw=0,rasterized=True,antialiaseds=False));lo=display.reshape(-1,3).min(0);hi=display.reshape(-1,3).max(0);span=hi-lo;pad=.03*max(span);ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),zlim=(lo[2]-pad,hi[2]+pad));ax.set_box_aspect(np.maximum(span,1));ax.set_proj_type('ortho');ax.view_init(elev=35.264389682754654,azim=45);ax.set_axis_off();meshrole='native'if kind=='native_fields'else'reference';segments,_,meshmeta=hm.mesh(cfg,family,meshrole,HERE);hm.add_lines(ax,segments,linewidth=.018,alpha=.12);record['mesh_overlay']=meshmeta;used.extend(cfg['true_mesh']['geometries'][family]if meshrole=='native'else[cfg['true_mesh']['FE_h2'][family]]);bar(fig,norm,limits,'|ΔU|\n[mm]'if delta else'U, Magnitude\n[mm]'if disp else'S, Mises\nMax. faces [MPa]',[.025,.25,.022,.56]);i=int(np.argmax(value));j=int(np.argmin(value));record.update(Min=float(value[j]),Min_xyz_mm=xyz[j].mean(0).tolist());peak=float(value[i]);position=xyz[i].mean(0);maxtext(fig,peak,position,'mm'if disp else'MPa');record.update(kind='REVIEWER_ONLY_POINTWISE_VECTOR_DIFFERENCE'if delta else'EXISTING_UNAVERAGED_FIXED_CENTROID_FIELD',family=family,points=len(data),limits=limits,Max=peak,Max_xyz_mm=position.tolist(),reference_finite_not_truth=True)
 else:raise ValueError('unknown panel '+key)
 if key=='F2a':
  outline=hm.registered_outer_points(ref)[:,:2]-registered_origin;outline=np.vstack([outline,outline[0]]);ax.plot(outline[:,0],outline[:,1],color='#303030',lw=.7);carrier=cp[:,:,:2].reshape(-1,2);low=carrier.min(0);high=carrier.max(0);pad=.03*(high-low);ax.set_xlim(low[0]-pad[0],high[0]+pad[0]);ax.set_ylim(low[1]-pad[1],high[1]+pad[1]);record['actual_registered_trim_outline']=True
 assert fig is not None
 if 'Max'in record:assert record['limits'][1]==record['Max']and record['limits'][0]==record['Min'];record['individual_range_equals_actual_Min_Max']=True;record['numeric_label_format']='.9g for both endpoint ticks and Min/Max'
 fig.canvas.draw();texts=[t for t in fig.findobj(matplotlib.text.Text)if t.get_text().strip()];assert texts and min(t.get_fontsize()for t in texts)>=6.5
 a.out.mkdir(parents=True);stem=a.out/key
 for ext in['pdf','svg','png','tiff']:fig.savefig(stem.with_suffix('.'+ext),dpi=600 if ext!='tiff'else 1000,**({'pil_kwargs':{'compression':'tiff_lzw'}}if ext=='tiff'else{}))
 plt.close(fig);record.update(native_width_mm=width,native_height_mm=height,min_actual_text_pt=min(t.get_fontsize()for t in texts),inputs=used,resources=cap,outputs=[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size}for f in sorted(a.out.iterdir())if f.is_file()]);(a.out/'ASSET.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');print(json.dumps({'status':'NATIVE_SINGLEPANEL_EXPORTED_PENDING_PDF_AND_VISUAL_QA','panel':key,'output':str(a.out)}))
if __name__=='__main__':main()
