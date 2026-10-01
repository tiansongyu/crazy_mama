# Mature female portrait refinement. All dimensions here precede final scaling.
AUNT_CFG=json.load(open(ROOT+'/source/iteration_config.json')) if os.path.exists(ROOT+'/source/iteration_config.json') else {}
FEMALE_ROWS=[((30.5,0,153.0),4.7,5.1,4.4),((30.7,0,154.5),6.1,6.0,5.5),
 ((30.9,0,156.0),7.5,6.9,6.8),((31,0,157.2),8.2,7.3,7.5),
 ((31,0,158.6),9.0,7.7,8.1),((31,0,160),9.7,8.05,8.6),
 ((31,0,161.5),10.15,8.2,8.9),((31,0,163),10.25,8.25,9.1),
 ((31,0,164.3),10.3,8.2,9.25),((31,0,165.5),10.3,8.15,9.35),
 ((31,0,167),10.4,8.1,9.45),((31,0,169),10.4,8.05,9.4),
 ((31,0,171),10.05,7.8,9.25),((31,0,173),9.3,7.2,8.6),
 ((31,0,175),7.8,6.0,7.0),((31,0,176.5),5.6,4.25,5.0),
 ((31,0,177.6),2.7,2.1,2.5),((31,0,178),.4,.4,.4)]
if AUNT_CFG.get('soft_jaw'):
    FEMALE_ROWS[0]=((30.5,0,153.0),5.2,5.45,4.6)
    FEMALE_ROWS[1]=((30.7,0,154.5),6.5,6.2,5.7)

def gauss(t,s):return math.exp(-(t/s)**2)

def female_bump(x,z):
    d=x-31.0
    cheek=.62*(gauss(d-4.9,2.7)+gauss(d+4.9,2.7))*gauss(z-161.0,2.2)
    nose=(1.05*gauss(z-163,2.2)+2.10*gauss(z-160.4,.95))*gauss(d,.98)
    alae=.62*(gauss(d-1.20,.6)+gauss(d+1.20,.6))*gauss(z-160.0,.63)
    lips=.39*gauss(d,2.4)*gauss(z-156.8,.42)
    lips+=.32*(gauss(d-.78,.85)+gauss(d+.78,.85))*gauss(z-157.5,.34)
    chin=.30*gauss(d,2.9)*gauss(z-154.5,.9)
    eyes=-.31*(gauss(d-4.1,1.75)+gauss(d+4.1,1.75))*gauss(z-164.5,.70)
    brows=.19*(gauss(d-4.1,2.0)+gauss(d+4.1,2.0))*gauss(z-166.0,.55)
    if AUNT_CFG.get('restrained_features'):
        cheek*=.75;nose*=.80;alae*=.78;lips*=.72;chin*=.65
    return cheek+nose+alae+lips+chin+eyes+brows

def female_wire(row):
    c,rx,front,back=row;points=[]
    for i in range(128):
        a=2*math.pi*i/128;co=math.cos(a);si=math.sin(a)
        x=c[0]+rx*co;y=c[1]+(front if si<0 else back)*si
        if si<0:y-=female_bump(x,c[2])*(-si)**4
        points.append(V(x,y,c[2]))
    curve=Part.BSplineCurve()
    if AUNT_CFG.get('fixed_parameterization'):
        curve.interpolate(Points=points,Parameters=[2*math.pi*i/128 for i in range(129)],PeriodicFlag=True)
    else:curve.interpolate(Points=points,PeriodicFlag=True)
    return Part.Wire([curve.toShape()])

def female_front(x,z):
    c,rx,fr,ba=interp(FEMALE_ROWS,z);u=min(.999,abs((x-c[0])/rx));w=math.sqrt(1-u*u)
    return c[1]-fr*w-female_bump(x,z)*w**4

def oval_frame(cx,angle):
    # Oval rims are sturdy continuous rings; lenses are open for FDM printing.
    rx,rz,rim=(4.05,2.40,.84) if AUNT_CFG.get('slender_glasses') else (3.95,2.90,1.0)
    outer=Part.Face(ellipse_wire((cx,-9.3,164.7),rx,rz,V(0,-1,0)))
    inner=Part.Face(ellipse_wire((cx,-9.3,164.7),rx-rim,rz-rim,V(0,-1,0)))
    ring=outer.cut(inner).extrude(V(0,1.05,0))
    ring.rotate(V(cx,-9.3,164.7),V(0,0,1),angle)
    return ring

def build_aunt_parts():
    face_rows=FEMALE_ROWS
    if AUNT_CFG.get('fixed_parameterization'):
        zs=sorted(set([r[0][2] for r in FEMALE_ROWS]+[153+i*.5 for i in range(37)]))
        face_rows=[interp(FEMALE_ROWS,z) for z in zs]
    skull=Part.makeLoft([female_wire(r) for r in face_rows],True,AUNT_CFG.get('fixed_parameterization',False))
    ears=[ellipsoid((20.8,.15,162),(1.7,1.75,2.75)),ellipsoid((41.2,.15,162),(1.7,1.75,2.75))]
    neck=zloft([((29,0,150.5),5.5,5.5),((29.6,0,152.4),4.8,4.8),((30.4,0,154.8),4.3,4.6)]) if AUNT_CFG.get('soft_jaw') else Part.makeCylinder(5.5,4.6,V(29,0,150.5))
    head=union([skull,neck,d_pin((29,0,144.5),3.5,6.2)]+ears)
    for x in (26.9,35.1):
        fy=female_front(x,164.35)
        # Eyeballs and lids form a filled, gently narrowed smiling eye.
        head=safe_detail(head,ellipsoid((x,fy+.13,164.35),(1.50,.40,.52)),'soft eyelid','fuse')
        eye=[(x-1.32,female_front(x-1.32,164.4)-.09,164.4),(x,fy-.30,164.52),(x+1.32,female_front(x+1.32,164.4)-.09,164.4)]
        head=safe_detail(head,tube(eye,.16/SCALE),'smiling eyelid crease')
        brow=[(x-1.65,female_front(x-1.65,166.2)-.08,166.2),(x,female_front(x,166.5)-.07,166.5),(x+1.65,female_front(x+1.65,166.2)-.08,166.2)]
        head=safe_detail(head,tube(brow,.19/SCALE),'curved brow','fuse')
    smile=[]
    for i in range(9):
        x=27.55+6.9*i/8;z=156.95+(.70 if AUNT_CFG.get('warm_smile') else .55)*((x-31)/3.45)**2
        smile.append((x,female_front(x,z)-.02,z))
    head=safe_detail(head,tube(smile,.22/SCALE),'natural smiling lip line')
    for sign in (-1,1):
        pts=[]
        for dx,z in [(2.5,159.6),(3.1,158.8),(3.7,157.7)]:
            x=31+sign*dx;pts.append((x,female_front(x,z)-.04,z))
        head=safe_detail(head,tube(pts,.13/SCALE),'light nasolabial fold')
    for x in (30.1,31.9):
        head=safe_detail(head,ellipsoid((x,female_front(x,160.0)-.05,159.95),(.30,.33,.22)),'nostril detail')
    for x in (20.2,41.8):head=safe_detail(head,ellipsoid((x,-1.30,162),(.80,.65,1.50)),'ear recess')
    log('Aunt facial surfaces created')

    left=oval_frame(26.85,-18);right=oval_frame(35.15,18)
    bridge=tube([(30.55,-10.3,165.1),(31,-10.8,165.7),(31.45,-10.3,165.1)],.54 if AUNT_CFG.get('slender_glasses') else .62)
    temple_paths=[[(23.10,-8.05,164.7),(22.55,-6.3,165.7),(23,-5.45,166),
                   (21.50,-2.8,165.3),(20.65,.4,163.7)],
                  [(38.9,-8.05,164.7),(39.45,-6.3,165.7),(39,-5.45,166),
                   (40.5,-2.8,165.3),(41.35,.4,163.7)]]
    glasses=union([left,right,bridge]+[tube(p,.65) for p in temple_paths])
    pin_radius=.85 if AUNT_CFG.get('print_refinement') else .75
    for x in (23,39):
        pin=Part.makeCylinder(pin_radius,2.8,V(x,-5.65,166),V(0,1,0))
        if AUNT_CFG.get('print_refinement'):
            edges=[e for e in pin.Edges if e.Vertexes and all(abs(v.Point.y+2.85)<1e-5 for v in e.Vertexes)]
            pin=pin.makeChamfer(.15/SCALE,edges)
        glasses=glasses.fuse(pin)
    if not glasses.isValid() or len(glasses.Solids)!=1:raise RuntimeError('Glasses must form one connected frame')
    # Clearance channels and two locating sockets are hidden beside the temples.
    clearance_tools=[tube(p,.65+FIT) for p in temple_paths]
    for tool in clearance_tools:head=head.cut(tool)
    for x in (23,39):head=head.cut(Part.makeCylinder(pin_radius+FIT,3.1+AXIAL,V(x,-5.85,166),V(0,1,0)))
    head=head.cut(glasses)
    log('Glasses and two temple locating sockets created')

    # Closed crown with a side-parted, short swept silhouette; no bald cap.
    inner_rows=[(c,rx+FIT,fr+FIT,ba+FIT) for c,rx,fr,ba in FEMALE_ROWS]
    hair_rows=[]
    for c,rx,fr,ba in FEMALE_ROWS:
        z=c[2];bulge=1.7+.5*gauss(z-164,5)
        hair_rows.append(((c[0],c[1]+.15,z),rx+bulge,fr+1.65,ba+2.0))
    hair_rows[-2]=((31,.3,179.0),3.1,2.5,3.0)
    hair_rows[-1]=((31,.3,180.0),.4,.4,.4)
    if AUNT_CFG.get('compact_hair'):
        hair_rows=[((c[0],c[1]+.10,c[2]),rx+1.55,fr+1.55,ba+1.65) for c,rx,fr,ba in FEMALE_ROWS if c[2]<171]
        for z in [171,173,175,176.5,178,178.8,179.2,179.4]:
            t=max(.025,math.sqrt(max(0,1-((z-171)/8.4)**2)))
            hair_rows.append(((31,.10,z),11.65*t,9.40*t,10.95*t))
    outer=cloth_loft(hair_rows,power=2.04)
    hair=outer.cut(cloth_loft(inner_rows,power=2.02))
    hairline=[(17.5,153),(20,160),(22.2,168),(25.5,170.2),(28.5,171.6),
              (31.9,173.25),(34.3,172.5),(37.8,169.8),(40,165.7),(43,154.5),(45,153)]
    if AUNT_CFG.get('compact_hair'):
        hairline=[(17.5,153),(20,163),(22.2,170),(25.5,172.6),(29,173.8),
                  (32,174.2),(35,173.8),(38,171.8),(40.5,168),(43,159),(45,153)]
    curve=Part.BSplineCurve();curve.interpolate(Points=[V(x,-35,z) for x,z in hairline])
    edge=curve.toShape();a=V(17.5,-35,148);b=V(45,-35,148)
    opening=Part.Face(Part.Wire([edge,Part.makeLine(V(45,-35,153),b),Part.makeLine(b,a),Part.makeLine(a,V(17.5,-35,153))])).extrude(V(0,36.2,0))
    hair=hair.cut(opening).common(box(14,-30,158 if AUNT_CFG.get('compact_hair') else 155,35,60,32))
    for x in (20.8,41.2):hair=hair.cut(ellipsoid((x,.15,162),(1.7+FIT,1.75+FIT,2.75+FIT)))
    for tool in clearance_tools:hair=hair.cut(tool)
    # Soft engraved strand directions follow the shell, with a narrow side part.
    strands=[[(32.4,173.8),(32.9,175.1),(32.6,176.4),(31.8,177.5)],
             [(30.4,172.7),(28.5,174.0),(26.7,174.9)],
             [(28.6,172.0),(26.4,172.8),(24.7,173.0)],
             [(26.8,171.4),(24.8,171.5),(23.3,171.1)],
             [(34.5,173.1),(36.0,173.8),(37.1,173.1)],
             [(36.2,171.9),(37.8,172.0),(39.0,170.7)]]
    for i,path in enumerate(strands):
        pts=[(x,surface_front(hair_rows,x,z,2.04)-.02,z) for x,z in path]
        hair=safe_detail(hair,tube(pts,(.23 if i==0 else .17)/SCALE),'hair strand '+str(i))
    if not hair.isValid() or len(hair.Solids)!=1:raise RuntimeError('Short hair shell must be one solid')
    # Maintain a clean seating boundary even at small eyelid or ear details.
    hair=hair.cut(head).cut(glasses)
    log('Short side-parted hair shell created')
    meta={'head_rows':FEMALE_ROWS,'hair_rows':hair_rows,'head_yaw_deg':HEAD_YAW,
          'glasses_rim_width_mm':(.84 if AUNT_CFG.get('slender_glasses') else 1.0)*SCALE,'glasses_depth_mm':1.05*SCALE,
          'temple_arm_diameter_mm':1.3*SCALE,'glasses_pin_diameter_mm':2*pin_radius*SCALE,
          'glasses_pin_insertion_mm':2.8*SCALE,'glasses_radial_clearance_mm':.20,
          'iteration_config':AUNT_CFG,'style':'Mature female face, compact short side-part hair, oval spectacles, restrained smile',
          'source_limit':'Single blurry reference. Features are interpreted, not an exact portrait scan.'}
    with open(ROOT+'/source/aunt_parameters.json','w') as f:json.dump(meta,f,ensure_ascii=False,indent=2)
    return head_turn(head),head_turn(hair),head_turn(glasses)
