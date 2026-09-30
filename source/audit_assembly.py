intersections=[]
for i,a in enumerate(parts):
    for b in parts[i+1:]:
        if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
        common=a.Shape.common(b.Shape)
        if abs(common.Volume)>.01:intersections.append({'a':a.Name,'b':b.Name,'volume_mm3':round(abs(common.Volume),5)})
with open(ROOT+'/source/interference_audit.json','w') as f:json.dump(intersections,f,indent=2)
log('INTERFERENCE_AUDIT '+str(intersections))
