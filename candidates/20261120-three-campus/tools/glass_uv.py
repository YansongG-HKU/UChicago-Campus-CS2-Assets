"""Measure positive-area UV overlap in the actual glass shader FBXs."""
import argparse
import json
from pathlib import Path
import sys

import bpy

EPSILON = 1e-9

def cross(a,b,c):
    return (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x)

def overlap(a,b):
    poly = list(a)
    if cross(*b) < 0:
        b=[b[0],b[2],b[1]]
    for start,end in zip(b, b[1:]+b[:1]):
        if not poly:
            return 0.0
        clipped=[]
        previous = poly[-1]
        prev_d = cross(start,end,previous)
        for current in poly:
            d=cross(start,end,current)
            if (d>=0) != (prev_d>=0):
                clipped.append(previous+(current-previous)*(prev_d/(prev_d-d)))
            if d>=0:
                clipped.append(current)
            previous,prev_d=current,d
        poly=clipped
    return abs(sum(p.x*q.y-q.x*p.y for p,q in zip(poly,poly[1:]+poly[:1])))*.5

def measure(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path),use_image_search=False)
    mesh=next(o.data for o in bpy.data.objects if o.type=='MESH')
    mesh.calc_loop_triangles()
    layers=[]
    for layer in mesh.uv_layers:
        bounds = []
        collapsed=[]
        for t in mesh.loop_triangles:
            poly = [layer.uv[i].vector.copy() for i in t.loops]
            area=abs(cross(*poly))*0.5
            if area <= EPSILON:
                collapsed.append(t.index)
                continue
            x,y=zip(*poly)
            bounds.append((min(x),max(x),min(y),max(y),poly,t.index))
        overlaps=[]
        active=[]
        for lo_x,hi_x,lo_y,hi_y,poly,idx in sorted(bounds,key=lambda item:item[0]):
            active=[v for v in active if v[1] > lo_x]
            for _,_,lo,hi,other,n in active:
                if hi <= lo_y or lo >= hi_y:
                    continue
                area=overlap(poly,other)
                if area > EPSILON:
                    overlaps.append([n,idx,round(area,12)])
            active.append((lo_x,hi_x,lo_y,hi_y,poly,idx))
        layers.append({'name':layer.name,'triangles':len(mesh.loop_triangles),
                       'zero_area_uv_count':len(collapsed),
                       'overlapping_pairs':len(overlaps),'example_pairs':overlaps[:10]})
    return layers

def main():
    p=argparse.ArgumentParser()
    p.add_argument('candidates',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    files=sorted(a.candidates.resolve().glob('*/*/*_Gls.fbx'))
    data={path.relative_to(a.candidates.resolve()).as_posix():measure(path) for path in files}
    a.output.write_text(json.dumps(data,indent=2)+'\n')
    for c in ('Chicago','Columbia','Penn'):
        rows={key:layers for key,layers in data.items() if key.startswith(c+'/')}
        print(c,len(rows),sum(any(x['overlapping_pairs'] for x in layers) for layers in rows.values()),
              sum(any(x['zero_area_uv_count'] for x in layers) for layers in rows.values()),flush=True)

if __name__ == "__main__":
    main()
