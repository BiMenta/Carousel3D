import bpy, math, random, os, json
from mathutils import Vector
from math import sin, cos, pi
random.seed(19)
OUT='/Volumes/ZHITAI/黑客松/CircusReference3D'
scene=bpy.data.scenes.new('Vintage Circus • Reference Reconstruction')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
groups={}
for name in ['01_Architecture','02_Tent_Canopy','03_Velvet_Drapery','04_Puppet_Theatre','05_Display_Podiums','06_Paper_Rosettes','07_Gilded_Ornaments','08_Pendant_Lanterns','09_Festoon_Lights','10_Lighting_Camera']:
    c=bpy.data.collections.new(name);scene.collection.children.link(c);groups[name[:2]]=c
G='01'
def put(o,name,mat=None):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    groups[G].objects.link(o)
    if mat:o.data.materials.append(mat)
    return o
def material(name,col,metal=0,rough=.65,noise=False,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    n=m.node_tree.nodes;p=next((v for v in n if v.type=='BSDF_PRINCIPLED'),None) or n.new('ShaderNodeBsdfPrincipled');out=next((v for v in n if v.type=='OUTPUT_MATERIAL'),None) or n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if emit:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
    if noise:
        t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=85;t.inputs['Detail'].default_value=3
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=.025
        m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return m
red=material('Velvet • oxblood',(.36,.025,.037),rough=.87,noise=True)
coral=material('Fabric • faded vermilion',(.57,.13,.105),noise=True)
teal=material('Velvet • deep petrol',(.018,.12,.115),rough=.88,noise=True)
gold=material('Antique gilt',(.65,.36,.12),.68,.31,True)
cream=material('Ivory linen',(.85,.64,.39),noise=True)
wood=material('Painted warm ochre wood',(.40,.19,.075),rough=.55,noise=True)
dark=material('Theatre interior',(.012,.009,.008))
floor=material('Terracotta floor',(.40,.16,.105),noise=True)
rug=material('Faded circular carpet',(.49,.32,.15),noise=True)
bulb=material('Warm fairy light', (1,.52,.18),rough=.22,emit=7)
glass=material('Lantern luminous ivory', (1,.42,.17),rough=.3,emit=2.2)
def mesh(name,vs,fs,mat,smooth=True):
    d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);groups[G].objects.link(o)
    if mat:d.materials.append(mat)
    if smooth:
        for p in d.polygons:p.use_smooth=True
    return o
def cube(name,loc,size,mat,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object,name,mat);o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:m=o.modifiers.new('Soft crafted edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def uv(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc);o=put(bpy.context.object,name,mat);o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(name,loc,r,depth,mat,verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=put(bpy.context.object,name,mat)
    m=o.modifiers.new('Rounded rim','BEVEL');m.width=.025;m.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def line(name,pts,mat,r=.018,cyclic=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3
    s=d.splines.new('POLY');s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts):p.co=(*v,1)
    s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,d);groups[G].objects.link(o);d.materials.append(mat);return o
def ring(name,x,y,z,r,mat,th=.03):return line(name,[(x+r*cos(i*2*pi/96),y+r*sin(i*2*pi/96),z) for i in range(96)],mat,th,True)
def curtain(name,x0,x1,y,bottom,top,mat,folds=16):
    vs=[];fs=[];N=100;M=18
    for j in range(M+1):
        v=j/M
        for i in range(N+1):
            u=i/N;x=x0+(x1-x0)*u
            z=bottom+(top-bottom)*v+.055*cos(u*folds*2*pi)*(1-v)
            vs.append((x,y+.12*cos(u*folds*2*pi)+.025*sin(v*pi*3+u*20),z))
    for j in range(M):
        for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
    o=mesh(name,vs,fs,mat);m=o.modifiers.new('Fabric thickness','SOLIDIFY');m.thickness=.015;return o
def swag(name,a,b,y,top,drop,mat):
    vs=[];fs=[];N=70;M=14
    for j in range(M+1):
        v=j/M
        for i in range(N+1):
            u=i/N;z=top-drop*sin(pi*u)**.7+v*(.20+.48*sin(pi*u))
            vs.append((a+(b-a)*u,y+.065*sin(v*9*pi+u*5)*sin(pi*u),z))
    for j in range(M):
        for i in range(N):k=j*(N+1)+i;fs.append((k,k+1,k+N+2,k+N+1))
    mesh(name,vs,fs,mat)
    line(name+' • lower braid',[(a+(b-a)*i/N,y-.025,top-drop*sin(pi*i/N)**.7) for i in range(N+1)],gold,.025)
    line(name+' • inner braid',[(a+(b-a)*i/N,y-.045,top-drop*sin(pi*i/N)**.7+.085) for i in range(N+1)],gold,.012)
def area(name,loc,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);groups['10'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def point(name,loc,power,color,r=.5):
    d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=r;o=bpy.data.objects.new(name,d);groups['10'].objects.link(o);o.location=loc

OUT='/Volumes/ZHITAI/黑客松/Carousel3D'
scene.name='Carousel • Gilded Midnight'
scene.render.fps=24;scene.frame_start=1;scene.frame_end=240
porcelain=material('Painted ivory horses',(.78,.69,.51),rough=.36)
mane=material('Carved chestnut mane',(.065,.026,.012),rough=.44)
navy=material('Royal blue saddle cloth',(.014,.07,.22),rough=.48)
ink=material('Obsidian eyes and hooves',(.009,.007,.008),rough=.25)
lightgold=material('Polished brass',(.74,.45,.14),.8,.24)
G='01'
def empty(name):
 o=bpy.data.objects.new(name,None);groups[G].objects.link(o);return o
rotor=empty('ANIMATION • rotating platform')
def par(o):o.parent=rotor;return o
for z,r,d,m in [(.12,5.25,.24,red),(.34,5.04,.23,red),(.58,4.85,.25,red),(.76,4.65,.14,wood)]:
 par(cyl('Stepped circular platform',(0,0,z),r,d,m,128));par(ring('Platform brass edge',0,0,z+d/2,r,lightgold,.035))
# Radial inlaid wood deck
for k in range(64):
 a=k*2*pi/64;b=(k+1)*2*pi/64
 vs=[(r*cos(t),r*sin(t),.842) for r,t in [(1,a),(4.61,a),(4.61,b),(1,b)]]
 par(mesh('Radial deck plank',vs,[(0,1,2,3)],wood if k%3 else coral,False))
 par(line('Deck plank seam',[(1*cos(a),1*sin(a),.85),(4.61*cos(a),4.61*sin(a),.85)],gold,.009))
for k in range(56):
 a=k*2*pi/56
 par(uv('Platform gilt leaf',(5.06*cos(a),5.06*sin(a),.34),(.075,.075,.04),gold))
# Central octagonal drum
G='04'
par(cyl('Central ornate drum',(0,0,3.65),1.02,5.65,red,12))
for z in [1,1.25,3.2,5.9,6.35]:par(ring('Central gilt cornice',0,0,z,1.08,gold,.09))
for k in range(12):
 a=k*2*pi/12
 par(line('Central column gilt vertical',[(1.04*cos(a),1.04*sin(a),1),(1.04*cos(a),1.04*sin(a),6.4)],gold,.038))
 for z in [1.5,2.6,3.7,4.8,5.9]:
  pts=[]
  for j in range(65):
   t=j/64*2.3*pi;r=.025+.23*j/64;u=r*cos(t);zz=z+r*sin(t)
   pts.append((1.035*cos(a)-u*sin(a),1.035*sin(a)+u*cos(a),zz))
  par(line('Gilded acanthus spiral',pts,gold,.025))
 for j in range(17):par(uv('Column incandescent bulb',(1.09*cos(a),1.09*sin(a),1.15+j*.3),(.045,.045,.045),bulb))
# canopy radial fabric
G='02'
for k in range(32):
 vs=[];fs=[]
 for j in range(26):
  t=j/25;r=.08+5.22*t;z=8.05-1.55*t**.7
  for i in range(7):
   a=(k+i/6)*2*pi/32;vs.append((r*cos(a),r*sin(a),z-.075*sin(pi*i/6)*sin(pi*t)))
 for j in range(25):
  for i in range(6):q=j*7+i;fs.append((q,q+1,q+8,q+7))
 mesh('Crimson ivory roof gore',vs,fs,red if k%2 else cream)
 a=k*2*pi/32
 line('Canopy golden seam',[(r*cos(a),r*sin(a),8.05-1.55*((r-.08)/5.22)**.7) for r in [.08+5.22*j/40 for j in range(41)]],gold,.015)
cyl('Roof finial stem',(0,0,8.18),.09,.4,gold)
uv('Roof finial orb',(0,0,8.43),(.15,.15,.21),gold)
# scalloped ornate oval fascia around canopy
for k in range(12):
 a=k*2*pi/12;pts=[]
 for j in range(81):
  t=j/80*2*pi;u=.5*sin(t);r=5.19;angle=a+u/1.05
  pts.append((r*cos(angle),r*sin(angle),6.45+.30*cos(t)))
 line('Scalloped canopy cartouche border',pts,gold,.055,True)
 # plaque is elliptical upright front facing radial direction
 vs=[(5.17*cos(a),5.17*sin(a),6.45)]
 for j in range(65):
  t=2*pi*j/64;ang=a+.45*sin(t);vs.append((5.17*cos(ang),5.17*sin(ang),6.45+.245*cos(t)))
 mesh('Burgundy oval painted canopy panel',vs,[(0,j,j+1) for j in range(1,65)],red)
 for j in range(22):
  t=j/22*2*pi;ang=a+.476*sin(t)
  uv('Fascia marquee bulb',(5.25*cos(ang),5.25*sin(ang),6.45+.29*cos(t)),(.052,.052,.052),bulb)
 # centre floral medallion
 uv('Fascia gold rosette',(5.24*cos(a),5.24*sin(a),6.45),(.12,.12,.12),gold)
 for j in range(14):
  t=j/13;aa=a-pi/12+t*pi/6
  uv('Undercanopy festoon bulb',(4.85*cos(aa),4.85*sin(aa),6.22-.18*sin(pi*t)),(.041,.041,.041),bulb)
 line('Radial canopy support',[(1*cos(a),1*sin(a),6.25),(5.15*cos(a),5.15*sin(a),6.3)],gold,.045)
# horse modelling in local space, later grouped tangentially
G='07'
def capsule(name,a,b,r,m):
 a=Vector(a);b=Vector(b);o=uv(name,(a+b)/2,(r,r,(b-a).length/2+r*.6),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def horse(idx,a,radius):
 before=set(scene.objects)
 root=empty('Horse %02d • animated mount'%idx)
 body=[]
 body.append(uv('Horse barrel',(0,0,0),(.68,.24,.32),porcelain))
 body.append(uv('Horse chest',(.43,0,.13),(.27,.255,.36),porcelain))
 body.append(capsule('Arched neck',(.42,0,.18),(.64,0,.9),.21,porcelain))
 body.append(uv('Horse head',(.77,0,1.04),(.28,.15,.22),porcelain))
 body.append(capsule('Horse muzzle',(.83,0,1.02),(1.06,0,.89),.115,porcelain))
 for y in [-.115,.115]:
  body.append(capsule('Pointed ears',(.66,y,1.18),(.65,y,1.42),.055,porcelain))
 for side in [-1,1]:
  yy=side*.18;lift=.12 if side>0 else 0
  legs=[[(.43,yy,-.09),(.73,yy,-.38+lift),(.97,yy,-.28+lift)], [(-.47,yy,-.04),(-.74,yy,-.40-lift),(-.48,yy,-.72-lift)]]
  for chain in legs:
   for j in range(2):body.append(capsule('Sculpted bent leg',chain[j],chain[j+1],.09 if j==0 else .065,porcelain))
   uv('Dark polished hoof',chain[-1],(.12,.085,.095),ink)
 # unify main anatomical volumes to smooth their intersections
 bpy.ops.object.select_all(action='DESELECT')
 for o in body:o.select_set(True)
 bpy.context.view_layer.objects.active=body[0];bpy.ops.object.join();o=body[0]
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 rem=o.modifiers.new('Unified carved anatomy','REMESH');rem.mode='VOXEL';rem.voxel_size=.036
 bpy.ops.object.modifier_apply(modifier=rem.name)
 sm=o.modifiers.new('Polished carving','SMOOTH');sm.factor=.8;sm.iterations=4
 for y in [-.147,.147]:
  uv('Horse black eye',(.84,y,1.09),(.039,.019,.039),ink)
  uv('Eye catchlight',(.85,y*1.1,1.10),(.011,.008,.011),cream)
  line('Red bridle cheek',[(.61,y,1.2),(.78,y*1.08,.9),(1.05,y*.74,.87)],red,.022)
  line('Golden reins',[(.93,y,.95),(.4,y*1.8,.55),(-.12,y*1.6,.35)],gold,.015)
 # sculpted flowing mane, layered waving locks
 for j in range(15):
  z=.25+j*.067;x=.43+.19*j/14
  line('Carved mane lock',[(x-.05,0,z+.16),(x-.22,.02,z+.1),(x-.29,-.01,z-.04),(x-.2,.01,z-.14)],mane,.065)
 for j in range(9):
  yy=(j-4)*.027
  line('Sweeping horse tail',[(-.54,yy,.12),(-.88,yy,.25),(-1.08,yy,-.08),(-1.02,yy,-.5),(-1.18,yy,-.65)],mane,.045)
 saddle=navy if idx%2 else red
 vs=[];fs=[]
 for j in range(21):
  x=-.40+j/20*.74
  for k in range(25):
   t=k/24*pi;vs.append((x,.29*cos(t),.04+.32*sin(t)))
 for j in range(20):
  for k in range(24):q=j*25+k;fs.append((q,q+1,q+26,q+25))
 mesh('Royal saddle blanket',vs,fs,saddle)
 for x in [-.4,.34]:line('Saddle cloth gilt piping',[(x,.295*cos(t*pi/40),.04+.325*sin(t*pi/40)) for t in range(41)],gold,.023)
 uv('Raised leather saddle',(-.05,0,.37),(.29,.19,.07),leather if 'leather' in globals() else wood)
 for side in [-1,1]:
  line('Hanging stirrup strap',[(-.08,side*.26,.2),(-.08,side*.32,-.2)],gold,.018)
  line('Stirrup loop',[(-.08+.10*cos(t*2*pi/24),side*.33,-.25+.12*sin(t*2*pi/24)) for t in range(25)],gold,.018)
 # parent newly-created parts; local geometry remains at origin
 for o in set(scene.objects)-before:
  if o!=root:o.parent=root
 root.parent=rotor;root.location=(radius*cos(a),radius*sin(a),2.35);root.rotation_euler[2]=a+pi/2
 for f,z in [(1,2.35+.25*sin(idx)),(61,2.35+.25*cos(idx)),(121,2.35-.25*sin(idx)),(181,2.35-.25*cos(idx)),(241,2.35+.25*sin(idx))]:root.location.z=z;root.keyframe_insert(data_path='location',frame=f)
 return root
for i in range(6):horse(i,i*2*pi/8,3.25)
# stationary-in-rotor brass poles support mounts
G='08'
for i in range(8):
 a=i*2*pi/8;x=3.25*cos(a);y=3.25*sin(a)
 par(cyl('Carousel brass mounting pole',(x,y,3.55),.035,5.4,lightgold,20))
 for z in [.89,6.14]:par(cyl('Pole decorative socket',(x,y,z),.095,.08,gold,24))
 pts=[(x+.038*cos(t*2*pi*20),y+.038*sin(t*2*pi*20),.9+5.25*t) for t in [j/600 for j in range(601)]]
 par(line('Pole spiral engraving',pts,gold,.008))
# Swan seat local geometry
G='06';before=set(scene.objects);sw=empty('Swan gondola')
uv('Swan rounded hull',(0,0,0),(.72,.35,.40),porcelain)
line('Swan elegant curved neck',[(.42,0,.1),(.72,0,.4),(.78,0,.85),(.60,0,1.12),(.43,0,1.07),(.43,0,.91)],porcelain,.13)
uv('Swan head',(.44,0,1.02),(.18,.13,.16),porcelain)
uv('Swan orange beak',(.29,0,.96),(.15,.07,.06),coral)
for side in [-1,1]:
 uv('Swan eye',(.40,side*.12,1.06),(.022,.012,.022),ink)
 for row in range(4):
  for k in range(7-row):
   o=uv('Layered carved swan feather',(-.48+k*.14,side*(.28+.012*row),.05+row*.1),(.22,.06,.10),porcelain);o.rotation_euler[1]=-.28
uv('Swan seat cushion',(-.10,0,.3),(.38,.23,.06),red)
for o in set(scene.objects)-before:
 if o!=sw:o.parent=sw
sw.parent=rotor;sw.location=(0,-3.25,2);sw.rotation_euler[2]=0
# gilded carriage at eighth station
G='05';before=set(scene.objects);car=empty('Royal carriage bench')
cube('Carriage red upholstered seat',(0,0,0),(1.15,.75,.22),red,.12)
cube('Carriage tall upholstered back',(0,.35,.47),(1.15,.16,.95),red,.18)
for x in [-.58,.58]:
 line('Carriage curved gilt arm',[(x,-.45,-.3),(x,-.48,.25),(x,-.3,.44),(x,.05,.27),(x,.36,.85)],gold,.075)
 for y in [-.25,.25]:
  line('Carriage decorative wheel',[(x,y+.22*cos(t*2*pi/40),-.38+.22*sin(t*2*pi/40)) for t in range(41)],gold,.035)
for x in [-.4,0,.4]:uv('Carriage button tuft',(x,.25,.5),(.035,.025,.035),gold)
line('Carriage crown rim',[(-.58,.35,.85),(-.45,.35,1.04),(0,.35,1.12),(.45,.35,1.04),(.58,.35,.85)],gold,.05)
for o in set(scene.objects)-before:
 if o!=car:o.parent=car
car.parent=rotor;car.location=(3.25*cos(7*pi/4),3.25*sin(7*pi/4),1.5);car.rotation_euler[2]=7*pi/4
# Seamless 10-second rotation and phase-offset 5-second horse bobbing.
rotor.animation_data_clear()
rotor.driver_add('rotation_euler',2).driver.expression='6.28318530718*(frame-1)/240'
for i in range(6):
 o=scene.objects['Horse %02d • animated mount'%i];o.animation_data_clear()
 o.driver_add('location',2).driver.expression='2.35+0.25*sin(6.28318530718*(frame-1)/120+%s)'%i
G='10'
# cobblestone-like procedural ground
stone=material('Midnight paved ground',(.035,.045,.065),rough=.85,noise=True)
cube('Display ground',(0,0,-.13),(200,200,.10),stone)
area('Warm carousel interior',(0,0,6.1),(0,0,0),1500,(1,.56,.24),5)
for k in range(6):
 a=k*2*pi/6;point('Warm marquee pool',(4*cos(a),4*sin(a),5.9),100,(1,.48,.18),.5)
area('Moonlight softbox',(-6,2,12),(0,0,3),1800,(.30,.46,1),8)
area('Front soft photographic fill',(6,-10,8),(0,0,3),1600,(1,.75,.51),7)
world=bpy.data.worlds.new('Blue hour');world.use_nodes=True
for n in world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs[0].default_value=(.018,.033,.08,1);n.inputs[1].default_value=.3
scene.world=world
camd=bpy.data.cameras.new('Carousel presentation');cam=bpy.data.objects.new('Carousel presentation',camd);groups[G].objects.link(cam);cam.location=(11,-16,10);cam.rotation_euler=(Vector((0,0,3.65))-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=46;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT+'/carousel_preview'
scene.view_settings.view_transform='AgX'
nt=bpy.data.node_groups.new('Carousel incandescent glow','CompositorNodeTree');scene.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=scene;gl=nt.nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Strength'].default_value=.23;out=nt.nodes.new('NodeGroupOutput');nt.links.new(rl.outputs['Image'],gl.inputs['Image']);nt.links.new(gl.outputs['Image'],out.inputs['Image'])
scene.frame_set(1)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/carousel.blend')
result={'saved':OUT+'/carousel.blend','objects':len(scene.objects),'horses':6,'swan':1,'carriage':1,'animation':'1-240 frames at 24fps'}
