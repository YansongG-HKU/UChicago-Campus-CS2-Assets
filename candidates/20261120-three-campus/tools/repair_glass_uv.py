"""Unwrap only collapsed UV faces of game-shader glass into unoccupied UV cells."""
import array
import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
from io_scene_fbx import encode_bin, parse_fbx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glass_uv import EPSILON, measure
from portable_readback import encode_node, read_blender, sha, typed_tree_hash

GRID = 128

def child(node, name):
    return next(e for e in node.elems if e.id == name)

def find_groups(indices, normals, repair):
    adjacent = {int(face):set() for face in np.flatnonzero(repair)}
    edges = {}
    for face in adjacent:
        row = indices[face]
        for a,b in zip(row, list(row[1:])+[row[0]]):
            ends = tuple(sorted((int(a),int(b))))
            for prev in edges.get(ends,[]):
                if np.dot(normals[prev], normals[face]) >= 0.999999:
                    adjacent[face].add(prev)
                    adjacent[prev].add(face)
            edges.setdefault(ends,[]).append(face)
    remaining = set(adjacent)
    while remaining:
        first=min(remaining)
        remaining.remove(first)
        group=[first]
        for face in group:
            more=sorted(adjacent[face]&remaining)
            remaining.difference_update(more)
            group.extend(more)
        yield group

def chart(corners, normal):
    edges = np.roll(corners,-1,axis=1)-corners
    lengths = np.linalg.norm(edges.reshape(-1,3),axis=1)
    tangent = edges.reshape(-1,3)[np.argmax(lengths)]
    tangent /= np.linalg.norm(tangent)
    bitangent = np.cross(normal,tangent)
    uv = corners @ np.column_stack((tangent,bitangent))
    uv -= uv.min(axis=(0,1))
    size = uv.max(axis=(0,1))
    assert np.all(size > 0)
    return uv,size

def reserve(used, width, height):
    rectangles = np.pad(used.cumsum(0,dtype=np.int32).cumsum(1,dtype=np.int32),((1,0),(1,0)))
    fits = rectangles[height:,width:] - rectangles[:-height,width:] - rectangles[height:,:-width] + rectangles[:-height,:-width]
    spots=np.argwhere(fits==0)
    if not len(spots):
        return None
    y,x=spots[0]
    used[y:y+height,x:x+width]=True
    return np.array([x+1,y+1],dtype=np.float64)/GRID

def apply(path, expected_bad, expected):
    root, version = parse_fbx.parse(str(path))
    assert version==7500 and sha(path)==expected['sha256']
    geo=child(child(root,b'Objects'),b'Geometry')
    indexed=np.asarray(child(geo,b'PolygonVertexIndex').props[0]).reshape(-1,3).copy()
    assert np.all(indexed[:,:2]>=0) and np.all(indexed[:,2]<0)
    indexed[:,2]=~indexed[:,2]
    positions=np.asarray(child(geo,b'Vertices').props[0]).reshape(-1,3)
    corners=positions[indexed]
    normals=np.cross(corners[:,1]-corners[:,0],corners[:,2]-corners[:,0])
    lengths=np.linalg.norm(normals,axis=1)
    assert np.all(lengths>0)
    normals/=lengths[:,None]
    layers=[c for c in geo.elems if c.id==b'LayerElementUV']
    assert len(layers)==1
    layer=layers[0]
    assert child(layer,b'MappingInformationType').props[0] == b'ByPolygonVertex'
    assert child(layer,b'ReferenceInformationType').props[0] == b'IndexToDirect'
    values=child(layer,b'UV').props[0]
    index=child(layer,b'UVIndex').props[0]
    resolved=np.asarray(values).reshape(-1,2)[np.asarray(index)].reshape(-1,3,2).astype(np.float32)
    ab=resolved[:,1]-resolved[:,0]
    ac=resolved[:,2]-resolved[:,0]
    area=np.abs(ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0])*.5
    repair=area<=EPSILON
    assert repair.sum()==expected_bad,(path,repair.sum(),expected_bad)
    used=np.zeros((GRID,GRID),dtype=np.bool_)
    for uv in resolved[~repair]:
        lo=np.maximum(0,np.floor(uv.min(axis=0)*GRID).astype(int)-1)
        hi=np.minimum(GRID,np.ceil(uv.max(axis=0)*GRID).astype(int)+1)
        used[lo[1]:hi[1],lo[0]:hi[0]]=True
    charts=[]
    for group in find_groups(indexed,normals,repair):
        uv,size=chart(corners[group], normals[group[0]])
        charts.append((group,uv,size))
    for group,uv,size in sorted(charts,key=lambda x:(-len(x[0]),x[0])):
        for span in (15,11,8,5):
            scaled=size/max(size)*(span/GRID)
            width,height=np.ceil(scaled*GRID).astype(int)+2
            origin=reserve(used,width,height)
            if origin is not None:
                break
        if origin is None:
            raise ValueError(f'No unoccupied UV area for {group} in {path}')
        output=uv/max(size)*(span/GRID)+origin
        for face,points in zip(group,output):
            for corner,point in enumerate(points):
                index[face*3+corner]=len(values)//2
                values.extend(point.astype(np.float64).tolist())
    after=np.asarray(values).reshape(-1,2)[np.asarray(index)].reshape(-1,3,2).astype(np.float32)
    assert np.array_equal(resolved[~repair],after[~repair])
    assert np.all((after>=0)&(after<=1))
    tree=typed_tree_hash(root)
    temp=path.with_suffix('.uv.pending.fbx')
    with encode_bin.FBXElem.enable_multithreading_cm():
        code=encode_node(root)
    encode_bin.write(str(temp),code,version)
    round_trip, actual_version=parse_fbx.parse(str(temp))
    assert typed_tree_hash(round_trip)==tree and actual_version==version
    uv_quality=measure(temp)
    assert all(not i['zero_area_uv_count'] and not i['overlapping_pairs'] for i in uv_quality),(path,uv_quality)
    check=read_blender(temp,[])
    assert check['finished'] and check['images']==expected['images']
    for old,new in zip(expected['meshes'],check['meshes'],strict=True):
        assert {k:v for k,v in old.items() if k!='uv'} == {k:v for k,v in new.items() if k!='uv'}
    temp.replace(path)
    return ({**expected,**check,'geometry_uv_tree_sha256':tree,'sha256':sha(path),'bytes':path.stat().st_size},
            {'previous_sha256':expected['sha256'],'final_sha256':sha(path),
             'isolated_charts':len(charts),'corner_uv_triangles_repaired':int(repair.sum()),
             'original_nondegenerate_uv_exact':True,'reimported_uv_quality':uv_quality})

def main():
    p=argparse.ArgumentParser()
    p.add_argument('candidates',type=Path)
    p.add_argument('readback',type=Path)
    p.add_argument('diagnosis',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    stage=a.candidates.resolve()
    outcome={}
    for relative,result in json.loads(a.diagnosis.read_text()).items():
        bad=sum(row['zero_area_uv_count'] for row in result)
        if not bad:
            continue
        campus,asset,name=Path(relative).parts
        data=a.readback/campus/(asset+'.json')
        record=json.loads(data.read_text())
        path=stage/relative
        try:
            final,receipt=apply(path,bad,record['fbx'][name])
        except Exception as error:
            import traceback
            temp=path.with_suffix('.uv.pending.fbx')
            if temp.exists():
                temp.unlink()
            outcome[relative]={'unresolved':str(error),'traceback':traceback.format_exc()}
            print('UNRESOLVED',relative,str(error),flush=True)
            continue
        record['fbx'][name]=final
        record['files'][name]={'bytes':final['bytes'],'sha256':final['sha256']}
        record.setdefault('glass_uv_repair',[]).append({'file':name,**receipt})
        record['after_bytes']=sum(f['bytes'] for f in record['files'].values())
        data.write_text(json.dumps(record,indent=2)+'\n')
        outcome[relative]=receipt
        print('REPAIRED',relative,bad,flush=True)
    a.output.write_text(json.dumps(outcome,indent=2)+'\n')

if __name__=='__main__':
    main()
