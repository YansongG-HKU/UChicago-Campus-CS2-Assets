#!/usr/bin/env python3
"""Classify existing 101-scene evidence; does not edit models or claim runtime acceptance."""
import collections,csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
A=json.loads((ROOT/'candidates/20261118-technical/evidence/source_audit.json').read_text())
P=json.loads((ROOT/'maintenance/packed-image-inventory-20261118.json').read_text())
assert len(A)==len(P)==101
images={r['source']:r['images'] for r in P};texture=[];lod=[]
for s in A:
 ims=images[s['source']];unique={i['sha']:i for i in ims}
 groups=collections.defaultdict(list)
 for i in ims:groups[i['sha']].append(i)
 duplicates=[g for g in groups.values() if len(g)>1]
 texture.append({'source':s['source'],'image_references':len(ims),'unique_image_contents':len(unique),'embedded_payload_bytes':sum(i['bytes'] for i in ims),'duplicate_embedded_payload_bytes':sum((len(g)-1)*g[0]['bytes'] for g in duplicates),'action':'retain source; content-bundle already deduplicates external files; image-datablock consolidation needs colorspace/alpha/export-name validation' if duplicates else 'no within-scene byte-identical image duplication'})
 for f in s['families']:
  main=next((m for m in f['meshes'] if m['name']==f['family']),None)
  l2=next((m for m in f['meshes'] if m['name']==f['family']+'_LOD2'),None)
  n=l2['triangles'] if l2 else None
  band='not_applicable' if n is None else 'within_500' if n<=500 else 'near_501_550' if n<=550 else 'moderate_551_1000' if n<=1000 else 'high_over_1000'
  lod.append({'source':s['source'],'family':f['family'],'lod1_ratio':f.get('lod1_ratio'),'lod1_over_half':bool((f.get('lod1_ratio') or 0)>=.5),'lod2_triangles':n,'classification':band,'action':'no blind decimation; compare silhouette and texture at transition distance' if (n or 0)>500 or (f.get('lod1_ratio') or 0)>=.5 else 'retain; static recommendation check does not establish game acceptance'})
for name,rows in [('texture-sharing-review-101.csv',texture),('lod-followup-136.csv',lod)]:
 with (ROOT/'maintenance'/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)
summary={'scope':'Reuse full 101-scene audit at 3c368437dd9df0f7a4589ce3e8f452bf7de1e164; no additional geometry or texture edits.','scenes':len(texture),'family_records':len(lod),'scenes_with_internal_duplicate_image_bytes':sum(r['duplicate_embedded_payload_bytes']>0 for r in texture),'internal_duplicate_embedded_payload_bytes':sum(r['duplicate_embedded_payload_bytes'] for r in texture),'lod2_classes':dict(collections.Counter(r['classification'] for r in lod)),'lod1_over_half_records':sum(r['lod1_over_half'] for r in lod),'lod2_over_500_unique_family_names':len({r['family'] for r in lod if (r['lod2_triangles'] or 0)>500}),'editor_verified':False}
(ROOT/'maintenance/followup-classification-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
