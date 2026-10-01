def right_hand_front(x,z):
    ell=[((53.2,-2.2,81.4),(3.4,2.3,4.2)),((50.4,-3.4,82),(1.3,1.5,2.3))]
    ell += [((fx,-2.7,fz),(1.05,1.5,2.7)) for fx,fz in [(50.8,78.1),(52.2,77.4),(53.6,77.7),(54.8,78.5)]]
    ys=[]
    for (cx,cy,cz),(rx,ry,rz) in ell:
        t=1-((x-cx)/rx)**2-((z-cz)/rz)**2
        if t>0:ys.append(cy-ry*math.sqrt(t))
    return min(ys) if ys else -3.8

def hand_detail_tools(which):
    if which!='right':return []
    result=[]
    for x in (50.8,52.2,53.6,54.8):
        points=[]
        for dx,dz in [(-.42,.03),(0,0),(.42,.03)]:
            z=79.3+dz;points.append((x+dx,right_hand_front(x+dx,z)-.055,z))
        result.append(tube(points,.18/SCALE))
    return result

def bow_detail(shape,cx,cy,cz):
    for sign in (-1,1):
        points=[]
        for dx,dz in [(3.7,.70),(2.9,.25),(2.0,-.25)]:
            x=cx+sign*dx;z=cz+dz
            u=(x-(cx+sign*3.1))/3.2;v=(z-(cz+.15))/2.05
            y=cy-.85-1.25*math.sqrt(max(.05,1-u*u-v*v))-.04
            points.append((x,y,z))
        shape=safe_detail(shape,tube(points,.18/SCALE),'soft ribbon fold')
    return shape

def add_micro_fit_test(coupon,pin):
    radius=.85*SCALE
    for x,clearance in [(5,.15),(13,.20),(21,.25)]:
        coupon.Shape=coupon.Shape.cut(Part.makeCylinder(radius+clearance,3.3,V(x,2,8.1),V(0,0,-1)))
    small=Part.makeCylinder(radius,2.8*SCALE,V(36,7.5,7))
    end=7+2.8*SCALE
    edges=[e for e in small.Edges if e.Vertexes and all(abs(v.Point.z-end)<1e-5 for v in e.Vertexes)]
    small=small.makeChamfer(.15,edges)
    pin.Shape=pin.Shape.fuse(small)
    coupon.Label='T01 • Main joints + spectacle micro-fit / 大小接头测试块'
    pin.Label='T02 • Ø6 D key + Ø1.42 glasses pin / 双向试配针'
    for obj in [coupon,pin]:
        if 'AssemblyInstructions' not in obj.PropertiesList:obj.addProperty('App::PropertyString','AssemblyInstructions','Print')
    coupon.AssemblyInstructions='Rear row: Ø6 D-key holes. Front row y=2: Ø1.42 glasses-pin holes. Both rows use radial clearances .15/.20/.25 mm from left to right.'
    pin.AssemblyInstructions='Ø6 D key below handle; Ø1.42 spectacle test pin above handle with 0.15 mm tip chamfer.'
