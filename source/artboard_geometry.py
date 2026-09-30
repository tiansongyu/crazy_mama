# Logical dimensions before the common pose transform and final uniform scale.
# Central foot support and connector geometry retain the previous edition's datum.
def art_kick(x):
    return 8.0*(max(abs(x)-80.0,0.0)/30.0)**2

def art_concave(y):
    return 1.8*(max(abs(y)-15.0,0.0)/13.0)**2

def art_height(x,y):
    return 7.0+art_kick(x)+art_concave(y)

def art_section(x):
    k=art_kick(x);bottom=.88*k
    left=[V(x,y,7+k+art_concave(y)) for y in [-36,-32,-28,-24,-20,-17,-15]]
    right=[V(x,y,7+k+art_concave(y)) for y in [15,17,20,24,28,32,36]]
    a=Part.BSplineCurve();a.interpolate(Points=left)
    b=Part.BSplineCurve();b.interpolate(Points=right)
    edges=[a.toShape(),Part.makeLine(left[-1],right[0]),b.toShape(),
           Part.makeLine(right[-1],V(x,36,bottom)),
           Part.makeLine(V(x,36,bottom),V(x,-36,bottom)),
           Part.makeLine(V(x,-36,bottom),left[0])]
    return Part.Wire(edges)

def art_pipe(points,r,closed=False):
    curve=Part.BSplineCurve();curve.interpolate(Points=[V(*p) for p in points],PeriodicFlag=closed)
    edge=curve.toShape()
    profile=Part.Wire([Part.makeCircle(r,V(*points[0]),edge.tangentAt(edge.FirstParameter))])
    return Part.Wire([edge]).makePipeShell([profile],True,False)

def art_distance(x,y,path):
    best=1e6
    for a,b in zip(path,path[1:]):
        dx=b[0]-a[0];dy=b[1]-a[1]
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy+1e-12)))
        best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
    return best

def art_color(c):
    depth=art_height(c.x,c.y)-c.z
    if .035<depth<1.15 and any(art_distance(c.x,c.y,p)<1.25 for p in ART_PATHS):
        return (.89,.66,.27)
    return RED

def build_artboard():
    middle=Part.Face(art_section(-80)).extrude(V(160,0,0))
    left=Part.makeLoft([art_section(x) for x in [-120,-110,-104,-98,-92,-86,-82,-80,-79.98]],True,False)
    right=Part.makeLoft([art_section(x) for x in [79.98,80,82,86,92,98,104,110,120]],True,False)
    body=middle.fuse(left).fuse(right)
    outline=Part.makeBox(164,56,40,V(-82,-28,-1))
    outline=outline.fuse(Part.makeCylinder(28,40,V(-82,0,-1))).fuse(Part.makeCylinder(28,40,V(82,0,-1)))
    body=body.common(outline)
    if not body.isValid() or len(body.Solids)!=1:raise RuntimeError('Curved deck loft failed')
    # Soften the perimeter before splitting the board or creating joints.
    try:
        rounded=body.makeFillet(.75/SCALE,body.Edges)
        if rounded.isValid() and len(rounded.Solids)==1:body=rounded
    except Exception as e:log('Perimeter fillet skipped: '+str(e))
    paths=[];closed=[]
    for lo,hi in [(-78,-9),(9,78)]:
        for sign in [-1,1]:
            xy=[(lo+(hi-lo)*i/40,sign*(22.5+1.45*math.sin(2*math.pi*i/40))) for i in range(41)]
            paths.append(xy);closed.append(False)
    for cx in [-94,94]:
        flower=[]
        for i in range(70):
            a=2*math.pi*i/70;r=6.0+2.0*math.cos(5*a)
            flower.append((cx+r*math.cos(a),r*math.sin(a)))
        paths.append(flower);closed.append(True)
    radius=.65/SCALE;depth=.55/SCALE
    plain=body.copy();lower=plain.copy();lower.translate(V(0,0,-depth))
    top_skin=plain.cut(lower)
    for i,(xy,isclosed) in enumerate(zip(paths,closed)):
        pts=[(x,y,art_height(x,y)+radius-depth) for x,y in xy]
        if isclosed:
            # Project closed rosettes vertically into the deck's top skin.
            # This avoids self-intersecting swept pipes at tight petal turns.
            cx=sum(p[0] for p in xy)/len(xy);cy=sum(p[1] for p in xy)/len(xy)
            wires=[]
            for delta in [radius,-radius]:
                points=[]
                for x,y in xy:
                    r=math.hypot(x-cx,y-cy);factor=(r+delta)/r
                    points.append(V(cx+(x-cx)*factor,cy+(y-cy)*factor,-1))
                curve=Part.BSplineCurve();curve.interpolate(Points=points,PeriodicFlag=True)
                wires.append(Part.Wire([curve.toShape()]))
            ring=Part.Face(wires[0]).cut(Part.Face(wires[1]))
            tool=ring.extrude(V(0,0,35)).common(top_skin)
        else:tool=art_pipe(pts,radius,False)
        candidate=body.cut(tool)
        if not candidate.isValid() or len(candidate.Solids)!=1:
            log('Engraving diagnostic '+str(i)+' valid='+str(candidate.isValid())+' solids='+str([s.Volume for s in candidate.Solids]))
            raise RuntimeError('Engraving failed '+str(i))
        if body.Volume-candidate.Volume<1:raise RuntimeError('Engraving did not intersect '+str(i))
        body=candidate
        log('Engraved artistic path '+str(i+1))
    display_paths=[p+[p[0]] if c else p for p,c in zip(paths,closed)]
    metadata={'outline':'Rounded popsicle deck, sculptural miniature without added wheels',
        'board_length_mm':220*SCALE,'board_width_mm':56*SCALE,
        'central_thickness_mm':7*SCALE,'tip_rise_mm':8*SCALE,
        'edge_concave_rise_mm':1.8*SCALE,'engraving_depth_mm':.55,
        'engraving_nominal_width_mm':1.3,'flat_support_half_width_mm':15*SCALE,
        'pattern':'Four flowing rail lines and two five-petal rosettes',
        'paths_logical_xy':display_paths,
        'geometry_reference':'https://elementbrand.co.uk/product-guides/skate/buying/choose-skateboard-deck.html'}
    with open(ROOT+'/source/artboard_parameters.json','w') as f:json.dump(metadata,f,indent=2)
    return body,display_paths
