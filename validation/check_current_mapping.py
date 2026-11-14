"""Check saved current mapping counters and residuals. No solver or CAD host is run."""
from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parent.parent
report=[]
for name in ['panel_4x','hull_uniform_8x','hull_local_16x']:
 p=ROOT/'validation/current_mapping'/name
 s=json.loads((p/'mapping_summary.json').read_text())
 def rows(n):
  with (p/n).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
 registry=rows('registry.csv');points=rows('points.csv');residuals=rows('map_residuals.csv')
 n=s['attempt_GP_count'];assert n==s['final_GP_count']==len(points)
 assert s['capture_complete'] and not s['fatal_latch'] and not s['legacy_opaque_entries'] and not s['cache_opaque_entries']
 assert len(registry)==s['registry_entries']==s['visited_entries']
 assert sorted(int(r['uid'])for r in points)==list(range(1,n+1))
 entries={int(r['entry'])for r in registry};assert {int(r['entry'])for r in points}<=entries
 assert all(r['bypass']=='false'for r in points)
 assert all(r['accepted']=='true' and math.isfinite(float(r['residual'])) and 0<float(r['tolerance']) and float(r['residual'])<=float(r['tolerance'])for r in residuals)
 report.append(dict(case=name,paired_requests=n,unaccepted_requests=n-len(points),visited_relations=s['visited_entries'],registered_relations=len(registry),residual_check_rows=len(residuals),maximum_residual_mm=max(float(r['residual'])for r in residuals)))
print(json.dumps(dict(status='SAVED_CURRENT_MAPPING_ACCOUNTING_CHECKED',scope='Paired requests, not internal iterations or geometric arclength coverage',cases=report),indent=2))
