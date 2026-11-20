"""Compare the Git LFS source archive with its exact checked-in split LOD FBXs."""
import json
import sys
from pathlib import Path

import bpy

folder, inventory, campus, output = sys.argv[sys.argv.index('--')+1:]
report = {}
for row in json.loads(Path(inventory).read_text()):
    if row['campus'] != campus:
        continue
    source = Path(row['source'])
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    source_meshes = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.calc_loop_triangles()
            source_meshes[obj.name] = len(obj.data.loop_triangles)
    original = json.loads((Path(folder)/campus/'_readback'/(row['asset'] + '.json')).read_text())
    comparisons = []
    for fbx, contents in original['fbx'].items():
        for mesh in contents['meshes']:
            name, triangles = mesh['name'], mesh['triangles']
            equivalent = source_meshes.get(name)
            if equivalent is None:
                match = source_meshes.get(name+'_Base')
                if match is not None:
                    equivalent = match
            comparisons.append({'fbx':fbx,'name':name,'source':equivalent,'split_fbx':triangles,
                                'identical_triangle_count':equivalent == triangles})
    report[row['asset']] = {'source_sha256': row['source_sha256'], 'source_meshes':source_meshes, 'comparisons':comparisons}
    print(campus, row['asset'],len(comparisons),sum(not r['identical_triangle_count'] for r in comparisons),flush=True)
Path(output).write_text(json.dumps(report,indent=2)+'\n')
