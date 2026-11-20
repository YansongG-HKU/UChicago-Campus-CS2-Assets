"""Rebuild only the modern south annex of Bartlett Hall; Blender 4.3.2.
blender -b --disable-autoexec PORTAL_SKYLIGHT.blend --python-exit-code 1 --python bartlett_south_annex.py -- NEW.blend
"""
import bmesh, bpy, hashlib, struct, sys
from collections import Counter
from pathlib import Path

NAMES=('BartlettHall','BartlettHall_LOD1','BartlettHall_LOD2')
BEFORE=(59954,19410,498)
REMOVE=(145,145,26)
SOURCE_SHA='a6f2315b112352d5efdb822b808ddfbff16c0a0e3be16e2c34b806afd6556bb5'
# Geometry fingerprint permits an independent replay of the first script even if
# the compressed .blend wrapper changes. Coordinates, oriented topology and UV.
FINGERPRINTS=(
    '388fd02fa4c235d1395a8cefaba2a54af793902f4acf8c35d37d0c845577a900',
    '1b453bdac15c03d805bf9a1cb20999ad40720bd8edb687b2bec0589571671e55',
    '93e5067e2a38fd61087cd71cfe2a7a4ca58a0755f5f18df82892d136724ca289',
)
FRONT=-39.428
REAR=-28.89
SIDE=9.984
ROOF=6.46
TOWER_X=(7.055,10.514)
TOWER_F=-39.958
TOWER_R=-36.50

def fingerprint(m):
    h=hashlib.sha256()
    for v in m.vertices:h.update(struct.pack('<3f',*v.co))
    for p in m.polygons:
        h.update(struct.pack('<3I',len(p.vertices),p.material_index,p.use_smooth))
        h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    for uv in m.uv_layers.active.data:h.update(struct.pack('<2f',*uv.uv))
    return h.hexdigest()

def remove_proxy(bm,lod):
    fs=[]
    for f in bm.faces:
        xs,ys,zs=zip(*(tuple(v.co) for v in f.verts))
        back=any(max(abs(y-d) for y in ys)<1e-5 for d in (-29.03,-29.06)) and f.normal.y>.99
        if max(map(abs,xs))<=6.65001 and max(zs)<=7.52501 and (min(ys)<-31 or back):
            fs.append(f)
    assert len(fs)==REMOVE[lod] and all(len(f.verts)==3 for f in fs)
    vs={v for f in fs for v in f.verts}
    bmesh.ops.delete(bm,geom=fs,context='FACES')
    assert all(not v.is_valid or v.link_faces for v in vs)

class Shape:
    def __init__(self,bm,lod):
        self.bm=bm;self.lu=bm.loops.layers.uv.active;self.lod=lod;self.faces=[]
        self.points={}
    def pt(self,p):
        p=tuple(round(x,6) for x in p)
        if p not in self.points:self.points[p]=self.bm.verts.new(p)
        return self.points[p]
    def face(self,coords,style='stone'):
        f=self.bm.faces.new([self.pt(p) for p in coords]);f.material_index=0
        self.faces.append(f); f.normal_update()
        reg={'stone':(.037,.04,.463,.462),'trim':(.030,.56,.220,.70),
             'roof':(.04,.62,.22,.70),'dark':(.03,.79,.17,.92),
             'door':(.77,.52,.98,.72),'trimdark':(.11,.53,.18,.61)}
        if self.lod==2:
            reg.update(door=(.785,.769,.958,.886),dark=(.81,.765,.875,.80),
                       trim=(.24,.135,.40,.208),roof=(.22,.166,.397,.20),
                       trimdark=(.23,.20,.41,.221))
        u,v,U,V=reg['door' if style=='gate' else style]
        n=f.normal
        ax=2 if abs(n.z)<.65 else 1
        wu=[p[1 if abs(n.x)>.75 else 0] for p in coords]; vv=[p[ax] for p in coords]
        du=max(wu)-min(wu); dv=max(vv)-min(vv)
        if style=='gate':
            # One constant vertical mapping across the curved opening; no stepped UV rows.
            u,v,U,V=(.770,.548,.980,.635) if self.lod<2 else (.795,.771,.955,.805)
            for lp,c in zip(f.loops,coords):
                lp[self.lu].uv=(u+(U-u)*(c[0]+3.6576)/7.3152,v+(V-v)*c[2]/4.78)
            return
        if style=='stone' and all(abs(c[1]-FRONT)<.000001 for c in coords):
            # Continuous site-scaled courses between openings. Repeat the
            # existing stone tile at X=-4,+4 along mortar junctions.
            left=-12 if max(wu)<=-4 else (4 if min(wu)>=4 else -4)
            for lp,c in zip(f.loops,coords):
                lp[self.lu].uv=(.002+.496*(c[0]-left)/8,.002+.496*c[2]/8)
            return
        if style=='stone':
            U=u+(U-u)*min(1,max(.1,du/7));V=v+(V-v)*min(1,max(.1,dv/7))
        for lp,uu,vo in zip(f.loops,wu,vv):
            lp[self.lu].uv=(u+(U-u)*((uu-min(wu))/du if du>1e-8 else .5),
                            v+(V-v)*((vo-min(vv))/dv if dv>1e-8 else .5))
    def close(self):
        bmesh.ops.recalc_face_normals(self.bm,faces=self.faces)
        edges={e for f in self.faces for e in f.edges}
        assert all(len(e.link_faces)==2 and e.is_contiguous for e in edges)
        bmesh.ops.triangulate(self.bm,faces=self.faces,quad_method='FIXED',ngon_method='EAR_CLIP')
        edges={e for v in self.points.values() for e in v.link_edges}
        assert all(len(e.link_faces)==2 and e.is_contiguous for e in edges)
        assert all(f.calc_area()>1e-8 for v in self.points.values() for f in v.link_faces)
        return len({f for v in self.points.values() for f in v.link_faces})

def prism(bm,lod,ring,bottom,top,wall='stone',lid='trim'):
    sh=Shape(bm,lod)
    a=[(*p,bottom) for p in ring];b=[(*p,top) for p in ring]
    sh.face(a[::-1],wall);sh.face(b,lid)
    for i in range(len(ring)):
        j=(i+1)%len(ring)
        sh.face([a[i],a[j],b[j],b[i]],wall)
    return sh.close()

def chopped_rect(x0,x1,y0,y1,c):
    return [(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]

def build_core(bm,lod):
    w=3.6576
    half=[(0,4.78),(1.25,4.56),(2.73,4.34),(3.16,4.20),(3.43,3.99),(3.58,3.76),(w,3.46)]
    if lod==1:half=[half[i] for i in (0,2,4,6)]
    if lod==2:half=[half[i] for i in (0,2,6)]
    main=[(-x,z) for x,z in reversed(half[1:])]+half
    side=[(-5.815,2.30),(-4.805,2.30)]
    arches=[(side,.26,.045),(main,.4572,.018)]
    xs=[-SIDE,-7.0]+[x for x,z in side]+[-4.0]+[x for x,z in main]+[4.0,7.0,SIDE]
    rec={x:z for a,_,_ in arches for x,z in a}
    def f(x,z):return (x,FRONT,z)
    def b(x,z):return (x,REAR,z)
    sh=Shape(bm,lod)
    for i in range(len(xs)-1):
        x,X=xs[i:i+2]
        ho=next(((a,depth,sill) for a,depth,sill in arches if a[0][0]<=x<X<=a[-1][0]),None)
        sh.face([f(x,ROOF),f(X,ROOF),b(X,ROOF),b(x,ROOF)],'roof')
        sh.face([b(x,0),b(X,0),f(X,0),f(x,0)],'stone')
        sh.face([b(x,0),b(X,0),b(X,ROOF),b(x,ROOF)])
        if ho:
            a,depth,sill=ho
            y=FRONT+depth
            sh.face([f(x,rec[x]),f(X,rec[X]),f(X,ROOF),f(x,ROOF)])
            sh.face([f(x,0),f(X,0),f(X,sill),f(x,sill)])
            sh.face([f(x,rec[x]),(x,y,rec[x]),(X,y,rec[X]),f(X,rec[X])],'trim')
            sh.face([f(x,sill),f(X,sill),(X,y,sill),(x,y,sill)],'trimdark')
            sh.face([(x,y,sill),(X,y,sill),(X,y,rec[X]),(x,y,rec[x])],'gate' if depth>.4 else 'door')
            if x==a[0][0]:
                sh.face([f(x,sill),(x,y,sill),(x,y,rec[x]),f(x,rec[x])],'trim')
            if X==a[-1][0]:
                sh.face([f(X,rec[X]),(X,y,rec[X]),(X,y,sill),f(X,sill)],'trim')
        else:
            ring=[f(x,0),f(X,0)]
            for a,_,sill in arches:
                if X==a[0][0]:ring += [f(X,sill),f(X,rec[X])]
            ring += [f(X,ROOF),f(x,ROOF)]
            for a,_,sill in arches:
                if x==a[-1][0]:ring += [f(x,rec[x]),f(x,sill)]
            sh.face(ring)
    sh.face([f(-SIDE,0),f(-SIDE,ROOF),b(-SIDE,ROOF),b(-SIDE,0)])
    sh.face([f(SIDE,0),b(SIDE,0),b(SIDE,ROOF),f(SIDE,ROOF)])
    return sh.close()

def new_annex(bm,lod):
    count=build_core(bm,lod)
    def outline(x0,x1,y0,y1,c):
        return chopped_rect(x0,x1,y0,y1,c) if lod<2 else [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    for sign in (-1,1):
        x0,x1=sorted(v*sign for v in TOWER_X)
        # 2022 sampled DSM–DTM: west 10.34–10.41m, east 10.41–10.49m.
        top=10.38 if sign<0 else 10.45
        count+=prism(bm,lod,outline(x0,x1,TOWER_F,TOWER_R,.23),0,top-.12 if lod<2 else top)
        if lod<2:
            count+=prism(bm,lod,outline(x0-.04,x1+.04,TOWER_F-.045,TOWER_R+.045,.26),top-.20,top,'trim','trim')
            x=(x0+x1)/2
            count+=prism(bm,lod,chopped_rect(x-.21,x+.21,TOWER_F-.013,TOWER_F+.023,.006),6.83,9.51,'dark','dark')
    # Break horizontal lines around the two openings; no trim in the opening.
    if lod<2:
        y=FRONT+.4572
        for x,height in ((-1.8288,4.44),(0,4.76),(1.8288,4.44)):
            count+=prism(bm,lod,outline(x-.018,x+.018,y-.023,y+.009,.004),.029,height,'dark','dark')
        for z in (1.04,2.69):
            count+=prism(bm,lod,outline(-3.625,3.625,y-.017,y+.010,.004),z,z+.070,'dark','dark')
    for x0,x1 in ((-7.36,-5.90),(-4.72,-3.88),(3.88,7.36)):
        if lod<2:count+=prism(bm,lod,outline(x0,x1,FRONT-.16,FRONT+.035,.025),.12,.59,'stone','trim')
        if lod<2:count+=prism(bm,lod,chopped_rect(x0,x1,FRONT-.19,FRONT+.045,.025),1.01,1.13,'trim','trim')
    for z0,z1 in (((5.36,5.50),(6.26,6.65)) if lod<2 else ((6.26,6.65),)):
        count+=prism(bm,lod,outline(-7.38,7.38,FRONT-.125,FRONT+.04,.027),z0,z1,'trim','trim')
    return count

def main():
    src=Path(bpy.data.filepath).resolve()
    if '--' not in sys.argv: 
        print(tuple(fingerprint(bpy.data.objects[n].data) for n in NAMES));return
    out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
    if src==out or out.exists() or out.suffix!='.blend' or not out.parent.is_dir():
        raise ValueError('Output must be a new .blend in a valid directory')
    meshes=[bpy.data.objects[n].data for n in NAMES]
    if hashlib.sha256(src.read_bytes()).hexdigest()!=SOURCE_SHA and tuple(map(fingerprint,meshes))!=FINGERPRINTS:
        raise ValueError('Incorrect Bartlett portal+skylight candidate')
    for lod,(name,before) in enumerate(zip(NAMES,BEFORE)):
        o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
        assert o.matrix_world.is_identity and m.users==1 and len(m.loop_triangles)==before
        bm=bmesh.new();bm.from_mesh(m);bm.normal_update()
        remove_proxy(bm,lod)
        added=new_annex(bm,lod)
        bm.to_mesh(m);bm.free();m.update();m.calc_loop_triangles()
        assert len(m.loop_triangles)==before-REMOVE[lod]+added
        assert all(t.area>1e-9 for t in m.loop_triangles)
        print(name,'old removed',REMOVE[lod],'added',added,'total',len(m.loop_triangles))
    bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
main()
