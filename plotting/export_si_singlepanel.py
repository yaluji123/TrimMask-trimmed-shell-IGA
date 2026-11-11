"""Standalone SI assets from existing plotting CSVs. No physics or replay."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,math,os,sys
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='1'
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
# Workspace collection root omitted; rendering uses frozen local CSV refs only.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def budget():
 p=R/'resource_guard.py';assert sha(p)=='837ab5e8caab3828bc7777a6beb24e6a0f631de99897d3b3a98531617305b6a6'
 s=importlib.util.spec_from_file_location('si_plot_resource_only',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.LIMIT=8<<30;cap=g.install()
 import ctypes
 k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
 return cap
def freeze():
 raise RuntimeError('This public bundle uses frozen local CSV inputs. Workspace input-collection is not a public rendering route.')

def main():
 a=argparse.ArgumentParser();a.add_argument('--freeze-inputs',action='store_true');a.add_argument('--panel');a.add_argument('--out',type=Path);a.add_argument('--execute-render',action='store_true');a=a.parse_args()
 if a.freeze_inputs:return freeze()
 if not a.execute_render:return print('PLAN_ONLY')
 assert a.out and not a.out.exists()and a.out.resolve().is_relative_to(R);cap=budget();cfg=json.loads((R/'SI_SINGLEPANEL_INPUTS_v1.json').read_text(encoding='utf-8'));used=[]
 def data(k):
  ref=cfg['data'][k];p=(R/Path(ref['path'])).resolve();assert p.is_relative_to(R)and sha(p)==ref['sha256']and p.stat().st_size==ref['bytes'];used.append(ref);return rows(p)
 import numpy as np,matplotlib as mpl
 mpl.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.lines import Line2D
 from matplotlib import ticker
 plt.rcParams.update({'font.family':'Times New Roman','font.size':7.5,'axes.labelsize':7.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.linewidth':.6,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
 p=a.panel;w=72;h=65;info={}
 if p=='S1':
  d=data('S1');assert len(d)==4;w=144;h=65;f,ax=plt.subplots(figsize=(w/25.4,h/25.4));f.subplots_adjust(left=.13,right=.98,bottom=.30,top=.96)
  for k,(label,key,color)in enumerate([('Historical export','historical_export_ratio','#D55E00'),('Registered reference','registered_reference_ratio','#444444'),('Current rounded export','current_rounded_export_ratio','#0072B2')]):
   v=[float(r[key])for r in d];assert all(0<=v<=1.09 for v in v);ax.bar(np.arange(4)+(k-1)*.23,v,width=.23,label=label,color=color)
  ax.axhline(1,color='#555555',ls='--',lw=.6);ax.set(xticks=np.arange(4),xticklabels=[r['element']for r in d],ylim=(0,1.09),xlabel='Cell identifier',ylabel='Retained UV area / full cell area');f.legend(*ax.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.54,.035),ncol=3,frameon=False,columnspacing=1.2);info=dict(cells=4,series=3,current_values_rounded=True)
 elif p.startswith('S2'):
  d=data('S2');assert len(d)==4;i='abc'.index(p[-1]);key,label,color,ylim,ticks=[('weak_percent_display','Full physical weak defect (%)','#17365D',(0,1.6),[0,.4,.8,1.2,1.6]),('raw_force_relative_L2','Relative force residual','#6B6B6B',(0,1.3),[0,.4,.8,1.2]),('raw_common_axis_moment_relative_L2','Relative moment residual','#6B6B6B',(0,.12),[0,.04,.08,.12])][i]
  f,ax=plt.subplots(figsize=(w/25.4,h/25.4));f.subplots_adjust(left=.25,right=.97,bottom=.22,top=.95);v=[float(r[key])for r in d];assert all(ylim[0]<=x<=ylim[1]for x in v);ax.plot([int(r['refinement'])for r in d],v,color=color,lw=1.2 if i==0 else .9,marker='o',ms=3);ax.set(xlim=(.8,4.2),ylim=ylim,xticks=[1,2,3,4],yticks=ticks,xlabel='Refinement level',ylabel=label);ax.yaxis.grid(True,color='#DDDDDD',lw=.35);info=dict(points=4,metric=key,raw_strong_failure_status_preserved=True)
 elif p.startswith('S3'):
  methods=['duffy_ref','ear7','clipper7','automatic_clipper7','automatic_ear7','ear3','fixed_mask6','fixed_mask12','fixed_mask24'];display=['Duffy','Signed Ear7','Fitted7','Auto fitted7','Auto Ear7','Signed Ear3','Mask 6','Mask 12','Mask 24'];colors={'duffy_ref':'#444444','ear7':'#9A4D8E','automatic_ear7':'#9A4D8E','clipper7':'#0F4D92','automatic_clipper7':'#0F4D92','ear3':'#B64342','fixed_mask6':'#767676','fixed_mask12':'#767676','fixed_mask24':'#767676'}
  def style(n):
   m='s'if n.startswith('fixed_mask')else'^'if n=='ear3'else'D'if n=='duffy_ref'else'o';filled=n in('automatic_clipper7','automatic_ear7','ear3','duffy_ref');return dict(color=colors[n],marker=m,s=10 if n.startswith('automatic')else 30,facecolors=colors[n]if filled else'white',linewidths=.8,zorder=5 if filled else 4)
  if p[-1]in'abc':
   d=data('S3_accuracy');assert len(d)==9 and set(r['method']for r in d)==set(methods);h=88;f,ax=plt.subplots(figsize=(w/25.4,h/25.4));f.subplots_adjust(left=.26,right=.97,bottom=.37,top=.96);key,label=[('displacement_relative_L2_upper','Displacement L2\nupper bound (%)'),('energy_seminorm_relative_upper','Energy seminorm\nupper bound (%)'),('independent_material_half_energy_gap_upper','Material-energy gap\nupper bound (%)')]['abc'.index(p[-1])];positive=[];excluded=[]
   for r in d:
    value=float(r[key]);assert math.isfinite(value)and value>=0
    if value==0:excluded.append(dict(method=r['method'],metric=key,reason='actual_exact_zero_not_drawn_on_log_axis'));continue
    x=int(r['all_accepted_bulk_kernel_visits_reported']);ax.scatter([x],[100*value],**style(r['method']));positive.append(100*value)
   ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Accepted kernel visits (thousands)');ax.set_ylabel(label);ax.set_ylim(10**math.floor(math.log10(min(positive+[.1])*.6)),10**math.ceil(math.log10(max(positive+[.1])*1.5)));xs=[int(r['all_accepted_bulk_kernel_visits_reported'])for r in d];ax.set_xlim(min(xs)/1.4,max(xs)*1.4);ax.xaxis.set_major_locator(ticker.LogLocator(base=10,subs=(1,2,5)));ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v,p:f'{v/1000:g}'));ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v,p:f'{v:g}'));ax.axhline(.1,color='#4D4D4D',lw=.7,ls=(0,(3,2)));ax.yaxis.grid(True,color='#DDDDDD',lw=.4,ls=':');handles=[Line2D([],[],color=colors[n],marker=style(n)['marker'],ls='',mfc=style(n)['facecolors'],ms=3 if n.startswith('automatic')else 5,label=l)for n,l in zip(methods,display)];f.legend(handles=handles,loc='lower center',bbox_to_anchor=(.54,.018),ncol=3,frameon=False,columnspacing=.65,handletextpad=.25);info=dict(all_configurations=9,actual_log_exclusions=excluded,metric=key,no_numeric_jitter_or_curve_fit=True)
  else:
   raw=data('S3_times');stats=data('S3_statistics');h=70;f,ax=plt.subplots(figsize=(w/25.4,h/25.4));f.subplots_adjust(left=.24,right=.97,bottom=.25,top=.94);timed=['automatic_clipper7','clipper7','fixed_mask12'];summary={(r['method'],r['metric']):r for r in stats};clocks=[('solve_and_export_command_ms',-.14,'#0F4D92','o','Command clock'),('trimTotal_segment_wall_ms',.14,'#767676','s','trimTotal clock')]
   for metric,offset,color,marker,label in clocks:
    for i,method in enumerate(timed):
     r=summary[method,metric];x=i+offset;values=[float(z[metric])for z in raw if z['method']==method];assert len(values)==3;ax.scatter([x]*3,values,color=color,marker='.',s=12,alpha=.65,zorder=3);ax.errorbar([x],[float(r['mean'])],yerr=[float(r['sample_SD_ddof1'])],fmt=marker,color=color,ms=4,capsize=2,lw=.8,label=label if i==0 else None,zorder=4)
   lower=min(0,min(float(summary[m,k]['mean'])-float(summary[m,k]['sample_SD_ddof1'])for m in timed for k in [x[0]for x in clocks]));ax.set_ylim(bottom=lower);ax.set_xticks(range(3),['Auto fitted7','Fixed fitted7','Mask 12']);ax.set_ylabel('Observed time (ms)');ax.set_xlabel('3 runs/family; mean ± sample SD');ax.legend(loc='center left',bbox_to_anchor=(.04,.56),frameon=False);info=dict(raw_runs=9,clock_series=2,mean_and_SD_read_from_original_table=True)
 else:raise ValueError(p)
 f.canvas.draw();texts=[t for t in f.findobj(mpl.text.Text)if t.get_text().strip()];assert min(t.get_fontsize()for t in texts)>=6.5;a.out.mkdir(parents=True);stem=a.out/p
 for ext in ['pdf','svg']:f.savefig(stem.with_suffix('.'+ext))
 f.savefig(stem.with_suffix('.png'),dpi=600);f.savefig(stem.with_suffix('.tiff'),dpi=1000,pil_kwargs={'compression':'tiff_lzw'});plt.close(f)
 out={'panel':p,'physical_data_recomputed':False,'combined_PNG_cropped':False,'panel_letters_or_headings_embedded':False,'native_width_mm':w,'native_height_mm':h,'minimum_actual_text_pt':min(t.get_fontsize()for t in texts),'inputs':used,'outputs':[pin(stem.with_suffix('.'+x))for x in ['pdf','svg','png','tiff']],'resources':cap,**info};(a.out/'ASSET.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(p,'EXPORTED_PENDING_QA',flush=True)
if __name__=='__main__':main()
