import bpy,math,random
from mathutils import Vector,Matrix
from math import sin,cos,pi
random.seed(80)
s=bpy.context.scene;s.frame_set(1)
rotor=s.objects['ANIMATION • rotating platform']
# Clear only the old horse assets and their poles.
for o in [v for v in s.objects if v.name.startswith('Horse ') and 'mount' in v.name]:
 for ch in list(o.children_recursive):bpy.data.objects.remove(ch,do_unlink=True)
 bpy.data.objects.remove(o,do_unlink=True)
for o in list(s.objects):
 if o.name.startswith(('Carousel brass mounting pole','Pole decorative socket','Pole spiral engraving')):bpy.data.objects.remove(o,do_unlink=True)
# Widen structural pieces; preserve original figures separately.
for c in s.collection.children:
 if c.name.startswith(('01_','02_')):
  for o in c.objects:
   if o==rotor:continue
   o.matrix_basis=Matrix.Diagonal((1.55,1.55,1,1)) @ o.matrix_basis
   if c.name.startswith('02_'):o.location.z+=.75
for o in s.objects:
 if o.name=='Swan gondola':o.location=(0,-2.55,2)
 if o.name=='Royal carriage bench':o.location=(2.55,0,1.5)
col=bpy.data.collections.new('20 Sculpted Carousel Horses');s.collection.children.link(col)
def mat(name,c,met=0,rough=.36):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=met;p.inputs['Roughness'].default_value=rough;return m
coats=[mat('Horse enamel • warm ivory',(.72,.66,.53)),mat('Horse enamel • silver dapple',(.31,.35,.38)),mat('Horse enamel • chestnut',(.27,.085,.028)),mat('Horse enamel • ebony',(.035,.025,.022))]
manes=[mat('Mane • dark walnut',(.045,.016,.008)),mat('Mane • charcoal',(.017,.019,.022)),mat('Mane • umber',(.09,.026,.008)),mat('Mane • golden flax',(.46,.26,.08))]
gold=mat('Horse harness • antique gold',(.7,.4,.11),.75,.28)
black=mat('Horse eye and hoof',(.008,.007,.006),0,.22)
white=mat('Eye glint',(.9,.85,.7))
cloths=[mat('Saddle • oxblood',(.26,.012,.025)),mat('Saddle • cobalt',(.012,.065,.23)),mat('Saddle • emerald',(.016,.13,.085)),mat('Saddle • plum',(.17,.024,.14))]
leather=mat('Saddle dark leather',(.045,.014,.008))
def put(o,name,m):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def uv(name,p,sc,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=14,location=p);o=put(bpy.context.object,name,m);o.scale=sc
 for f in o.data.polygons:f.use_smooth=True
 return o
def mesh(name,v,f,m):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(name,d);col.objects.link(o);d.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 return o
def curve(name,pts,m,r=.02):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=16;d.bevel_depth=r;d.bevel_resolution=3;sp=d.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,v in zip(sp.bezier_points,pts):p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);col.objects.link(o);d.materials.append(m);return o
def capsule(name,a,b,r1,r2,m):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u);vs=[];fs=[]
 for j in range(9):
  t=j/8;r=r1*(1-t)+r2*t;c=a.lerp(b,t)
  for k in range(16):q=k*2*pi/16;vs.append(c+r*(u*cos(q)+v*sin(q)))
 for j in range(8):
  for k in range(16):p=j*16+k;fs.append((p,j*16+(k+1)%16,(j+1)*16+(k+1)%16,p+16))
 fs.extend([tuple(reversed(range(16))),tuple(range(128,144))]);return mesh(name,vs,fs,m)
def torus(name,center,rx,rz,m,r=.015,y=None):
 x,yy,z=center;return curve(name,[(x+rx*cos(k*2*pi/32),yy,z+rz*sin(k*2*pi/32)) for k in range(33)],m,r)
def build_horse(style):
 start=set(col.objects);m=coats[style];hair=manes[style];body=[]
 body.append(uv('Anatomy • ribcage',(0,0,.04),(.72,.285,.36),m))
 body.append(uv('Anatomy • shoulder',(.43,0,.14),(.31,.30,.40),m))
 body.append(uv('Anatomy • powerful hindquarter',(-.49,0,.10),(.34,.30,.36),m))
 # Continuous tapered arched neck with a broad chest and fine throat latch.
 vs=[];fs=[];rings=[(.36,.15,.29,.25),(.44,.34,.28,.23),(.52,.56,.24,.20),(.66,.79,.20,.17),(.80,.98,.165,.145),(.87,1.11,.15,.13)]
 for x,z,rx,ry in rings:
  for j in range(24):a=2*pi*j/24;vs.append((x+rx*cos(a),ry*sin(a),z))
 for k in range(len(rings)-1):
  for j in range(24):a=k*24+j;fs.append((a,k*24+(j+1)%24,(k+1)*24+(j+1)%24,a+24))
 fs.extend([tuple(reversed(range(24))),tuple(range(120,144))]);body.append(mesh('Anatomy • curved tapered neck',vs,fs,m))
 body.append(uv('Anatomy • sculpted cheek',(.94,0,1.09),(.225,.16,.23),m))
 body.append(capsule('Anatomy • long horse face',(.98,0,1.18),(1.32,0,.95),.14,.10,m))
 body.append(uv('Anatomy • soft muzzle',(1.35,0,.92),(.16,.12,.105),m))
 for yy in [-.105,.105]:
  ear=uv('Anatomy • pointed ear',(.81,yy,1.37),(.065,.045,.20),m);ear.rotation_euler[1]=-.25;body.append(ear)
 # Four anatomically differentiated, articulated galloping limbs.
 for side in [-1,1]:
  yy=side*.22;phase=(style%2)*.12
  if side==-1:
   front=[(.46,yy,-.03),(.67,yy,-.38),(1.02,yy,-.32+phase),(1.18,yy,-.43+phase)]
   back=[(-.50,yy,-.05),(-.76,yy,-.35),(-1.00,yy,-.61),(-1.24,yy,-.62)]
  else:
   front=[(.46,yy,-.03),(.48,yy,-.47),(.24,yy,-.76),(.33,yy,-.89)]
   back=[(-.50,yy,-.05),(-.27,yy,-.36),(-.47,yy,-.67),(-.31,yy,-.86)]
  for leg in [front,back]:
   for j in range(3):body.append(capsule('Anatomy • leg taper',leg[j],leg[j+1],[.125,.075,.052][j],[.085,.052,.045][j],m))
   for j in [1,2]:body.append(uv('Anatomy • knee and fetlock',leg[j],(.078,.072,.083),m))
   hoof=uv('Hoof • sculpted dark hoof',leg[-1],(.115,.085,.085),black);hoof.rotation_euler[1]=-.25
 # Fuse underlying anatomy into one sculptable mesh.
 bpy.ops.object.select_all(action='DESELECT')
 for o in body:o.select_set(True)
 bpy.context.view_layer.objects.active=body[0];bpy.ops.object.join();o=body[0];o.name='Horse unified sculpt • style %d'%style
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 rem=o.modifiers.new('Sculpt union','REMESH');rem.mode='VOXEL';rem.voxel_size=.024;bpy.ops.object.modifier_apply(modifier=rem.name)
 sm=o.modifiers.new('Soft carved transitions','SMOOTH');sm.factor=.65;sm.iterations=4
 # Eyelids, nostrils, mouth crease, ear interiors, flowing mane.
 for side in [-1,1]:
  uv('Eye socket',(.995,side*.147,1.16),(.064,.022,.052),m)
  uv('Glossy expressive eye',(1.006,side*.166,1.167),(.033,.015,.030),black)
  uv('Eye highlight',(1.016,side*.179,1.178),(.009,.006,.009),white)
  uv('Inset nostril',(1.395,side*.099,.948),(.039,.014,.024),black)
  curve('Muzzle mouth crease',[(1.20,side*.106,.865),(1.34,side*.115,.855),(1.45,side*.07,.883)],hair,.008)
  uv('Ear interior',(.82,side*.115,1.40),(.032,.034,.115),hair)
  curve('Bridle cheekpiece',[(.81,side*.18,1.27),(.95,side*.19,1.07),(1.29,side*.135,.90)],cloths[style],.022)
  torus('Bridle bit ring',(1.23,side*.14,.89),.045,.045,gold,.012)
  curve('Loose swept reins',[(1.23,side*.15,.90),(.59,side*.38,.53),(-.10,side*.30,.40)],gold,.014)
  curve('Saddle breast collar',[(.22,side*.28,.34),(.58,side*.29,.05),(.51,side*.21,-.15)],cloths[style],.035)
 # Long curved mane locks follow the arched neckline and overlap the shoulder.
 for j in range(22):
  t=j/21;x=.32+.5*t;z=.30+.97*t
  lock=curve('Mane • flowing carved lock',[(x-.09,0,z+.06),(x-.22,-.04,z+.05),(x-.31,-.08,z-.10),(x-.26,-.10,z-.25)],hair,.055)
  for p,r in zip(lock.data.splines[0].bezier_points,[.85,1,.7,.08]):p.radius=r
 for j in range(5):
  curve('Forelock • curled crest',[(.80,(j-2)*.025,1.34),(.99,(j-2)*.026,1.35),(1.05,(j-2)*.02,1.23)],hair,.031)
 for j in range(16):
  yy=(j-7.5)*.017
  lock=curve('Tail • flowing tapered strand',[(-.68,yy,.24),(-1.03,yy*.9,.28),(-1.37,yy*.7,.08),(-1.50,yy*.6,-.29),(-1.34,yy*.5,-.60)],hair,.037)
  for p,r in zip(lock.data.splines[0].bezier_points,[1,1,.8,.5,.04]):p.radius=r
 # Ornamental saddle blanket draped over the back, scalloped lower edges.
 vs=[];fs=[]
 for j in range(25):
  x=-.39+.67*j/24
  for k in range(33):
   a=pi*k/32;vs.append((x,.32*cos(a),-.035+.435*sin(a)+.025*cos(j*pi/6)*(abs(cos(a))**10)))
 for j in range(24):
  for k in range(32):q=j*33+k;fs.append((q,q+1,q+34,q+33))
 mesh('Saddle • embroidered blanket',vs,fs,cloths[style])
 for x in [-.39,.28]:curve('Blanket golden border',[(x,.326*cos(k*pi/40),-.025+.44*sin(k*pi/40)) for k in range(41)],gold,.018)
 for side in [-1,1]:
  curve('Blanket lower braided border',[(-.39+.67*j/30,side*.326,-.025+.025*cos(j/30*4*pi)) for j in range(31)],gold,.017)
  for x in [-.28,-.10,.09]:uv('Blanket gold jewel',(x,side*.335,.07),(.028,.015,.047),gold)
  curve('Stirrup leather',[(0,side*.28,.32),(-.04,side*.40,-.32)],leather,.025)
  torus('Stirrup polished iron',(-.04,side*.40,-.40),.10,.12,gold,.018)
 uv('Saddle leather seat',(-.06,0,.435),(.27,.20,.065),leather)
 for x,z in [(-.32,.49),(.21,.51)]:uv('Saddle raised pommel',(x,0,z),(.067,.21,.09),cloths[style])
 return list(set(col.objects)-start)
prototypes=[build_horse(i) for i in range(4)]
# 12 outside + 8 inside; shared mesh datablocks keep twenty detailed horses manageable.
roots=[]
for i in range(20):
 outer=i<12;j=i if outer else i-12;count=12 if outer else 8;radius=6.35 if outer else 4.05;a=2*pi*j/count+(0 if outer else pi/8)
 root=bpy.data.objects.new('Horse %02d • %s ring'%(i+1,'outer' if outer else 'inner'),None);col.objects.link(root);root.parent=rotor;root.location=(radius*cos(a),radius*sin(a),2.55);root.rotation_euler[2]=a+pi/2
 for src in prototypes[i%4]:
  o=src.copy();o.data=src.data;col.objects.link(o);o.parent=root
 root.driver_add('location',2).driver.expression='2.55+0.24*sin(6.28318530718*(frame-1)/144+%s)'%(i*1.618)
 root['horse_number']=i+1;root['ring']='outer' if outer else 'inner';roots.append(root)
 # brass vertical rod from deck to roof, independent of bobbing horse
 p=(radius*cos(a),radius*sin(a))
 pole=curve('Mounting pole %02d'%(i+1),[(p[0],p[1],.86),(p[0],p[1],6.95)],gold,.035);pole.parent=rotor
 for z in [.9,6.9]:
  o=uv('Pole gilt socket',(p[0],p[1],z),(.09,.09,.035),gold);o.parent=rotor
for proto in prototypes:
 for o in proto:bpy.data.objects.remove(o,do_unlink=True)
# Retain smooth circular movement at a gentler speed for the enlarged ride.
s.frame_end=360;rotor.animation_data_clear();rotor.driver_add('rotation_euler',2).driver.expression='6.28318530718*(frame-1)/360'
for i,root in enumerate(roots):root.animation_data.drivers[0].driver.expression='2.55+0.24*sin(6.28318530718*(frame-1)/120+%s)'%(i*1.618)
s.camera.location=(17,-25,13.5);s.camera.rotation_euler=(Vector((0,0,4))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=47
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='AREA':o.data.energy*=1.65
# Additional broad warm illumination for the wider rings.
d=bpy.data.lights.new('Outer ring warm fill','AREA');d.energy=1500;d.shape='DISK';d.size=10;o=bpy.data.objects.new('Outer ring warm fill',d);s.collection.objects.link(o);o.location=(0,-4,6.5)
s.render.resolution_x=1600;s.render.resolution_y=1150;s.cycles.samples=40
s.render.filepath='/Volumes/ZHITAI/黑客松/Carousel3D/carousel_20_preview'
s.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='/Volumes/ZHITAI/黑客松/Carousel3D/carousel_20.blend')
result={'file':bpy.data.filepath,'horses':len(roots),'outer':12,'inner':8,'diameter':16.275,'objects':len(s.objects)}
