from pathlib import Path
import json, math, numpy as np, trimesh, vtk
from PIL import Image, ImageDraw, ImageFont
from vtk.util.numpy_support import numpy_to_vtk

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'source/parts_manifest.json').read_text())
design=json.loads((ROOT/'source/design_parameters.json').read_text())
SCALE=design['scale']
ART=json.loads((ROOT/'source/artboard_parameters.json').read_text())
parts=[p for p in manifest if p['id'].startswith('P')]
OFFSETS={'P01_Board_Left':[-15,0,0],'P02_Board_Right':[15,0,0],
 'P03_Dowel_1':[0,-40,5],'P03_Dowel_2':[0,-40,5],
 'P04_Leg':[-12,0,12],'P05_Leg':[12,0,12],'P06_Torso':[0,0,27],
 'P07_LeftArm':[-34,0,30],'P08_RightArm':[34,0,30],
 'P09_Head':[0,0,65],'P10_Collar':[0,0,47],'P11_Hair':[38,0,70],
 'P12_PaddleLower':[-32,0,8],'P13_PaddleUpper':[-32,0,33],'P14_Bow':[0,-38,28]}

def color_triangles(mesh,p):
    centers=mesh.triangles_center/SCALE
    if p['id'] not in ['P01_Board_Left','P02_Board_Right']:centers[:,0]+=design.get('pose_shear',0)*(centers[:,2]-7)
    colors=np.tile(np.array(p['color'][:3])*255,(len(centers),1))
    n=p['id']
    if n in ['P04_Leg','P05_Leg']:
        colors[:]=[29,37,52]
        colors[centers[:,2]<18.7]=[194,130,102]
        colors[centers[:,2]<14.85]=[17,18,20]
    if n=='P07_LeftArm': colors[(centers[:,0]<-25.3)&(centers[:,2]<102.5)]=[194,130,102]
    if n=='P08_RightArm': colors[centers[:,2]<84.4]=[194,130,102]
    if n=='P09_Head':
        angle=-math.radians(design['head_yaw_deg']);cy=math.cos(angle);sy=math.sin(angle)
        local=centers.copy();local[:,0]=29+(centers[:,0]-29)*cy-centers[:,1]*sy;local[:,1]=(centers[:,0]-29)*sy+centers[:,1]*cy
        for x in [26.6,34.8]:
            mask=(abs(local[:,0]-x)<1.1)&(abs(local[:,2]-164.2)<.39)&(local[:,1]<-6.4)
            colors[mask]=[65,54,48]
        smile_z=156+1.4*((local[:,0]-30.5)/3.4)**2
        mask=(abs(local[:,0]-30.5)<3.5)&(abs(local[:,2]-smile_z)<.43)&(local[:,1]<-7.0)
        colors[mask]=[124,68,63]
    if n in ['P01_Board_Left','P02_Board_Right']:
        x,y,z=centers.T
        height=7+8*(np.maximum(abs(x)-80,0)/30)**2+1.8*(np.maximum(abs(y)-15,0)/13)**2
        depth=height-z
        near=np.zeros(len(centers),dtype=bool)
        for path in ART['paths_logical_xy']:
            path=np.array(path);a=path[:-1];d=path[1:]-a;ll=(d*d).sum(axis=1)
            for start in range(0,len(centers),1000):
                xy=centers[start:start+1000,:2]
                delta=xy[:,None,:]-a[None,:,:]
                t=np.clip((delta*d[None,:,:]).sum(axis=2)/(ll[None,:]+1e-12),0,1)
                distance=((delta-t[:,:,None]*d[None,:,:])**2).sum(axis=2).min(axis=1)
                near[start:start+len(xy)] |= distance<1.25**2
        colors[near & (depth>.035) & (depth<1.15)]=[227,168,69]
    return colors.astype(np.uint8)

meshes={p['id']:trimesh.load(ROOT/'stl'/(p['id']+'.stl')) for p in manifest}
validation=[]
for p in manifest:
    m=meshes[p['id']]
    validation.append({'id':p['id'],'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'connected_shells':len(m.split()),'triangles':len(m.faces),'dimensions_mm':m.extents.round(3).tolist()})
    if not (m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1): raise RuntimeError('Failed mesh '+p['id'])
(ROOT/'source/mesh_validation.json').write_text(json.dumps(validation,indent=2))

def poly_from_mesh(mesh,colors):
    pd=vtk.vtkPolyData(); points=vtk.vtkPoints(); points.SetData(numpy_to_vtk(mesh.vertices,deep=True)); pd.SetPoints(points)
    cells=vtk.vtkCellArray(); data=np.column_stack([np.full(len(mesh.faces),3),mesh.faces]).astype(np.int64)
    cells.SetCells(len(mesh.faces),numpy_to_vtk(data.ravel(),deep=True,array_type=vtk.VTK_ID_TYPE)); pd.SetPolys(cells)
    scalars=numpy_to_vtk(colors,deep=True,array_type=vtk.VTK_UNSIGNED_CHAR); scalars.SetName('Color'); pd.GetCellData().SetScalars(scalars)
    return pd

def render(path,exploded=False,front=False,rear=False,detail=False):
    ren=vtk.vtkRenderer(); ren.SetBackground(.955,.962,.973)
    for p in parts:
        pd=poly_from_mesh(meshes[p['id']],color_triangles(meshes[p['id']],p))
        normals=vtk.vtkPolyDataNormals(); normals.SetInputData(pd); normals.SetFeatureAngle(65); normals.SplittingOn(); normals.ConsistencyOn()
        mapper=vtk.vtkPolyDataMapper(); mapper.SetInputConnection(normals.GetOutputPort()); mapper.SetScalarModeToUseCellData(); mapper.SetColorModeToDirectScalars()
        actor=vtk.vtkActor(); actor.SetMapper(mapper)
        if p['id'] in ['P01_Board_Left','P02_Board_Right']:
            mapper.SetInputData(pd);actor.GetProperty().SetInterpolationToFlat()
        actor.GetProperty().SetAmbient(.26); actor.GetProperty().SetDiffuse(.72); actor.GetProperty().SetSpecular(.13); actor.GetProperty().SetSpecularPower(35)
        if exploded: actor.SetPosition(OFFSETS[p['id']])
        ren.AddActor(actor)
    cam=ren.GetActiveCamera(); target=[10,-1,125] if detail else [0,0,100 if exploded else 74]
    cam.SetFocalPoint(target)
    cam.SetPosition((target[0]+25,-600,target[2]+16) if detail else (0,-700,target[2]+8) if front else (-245,650,target[2]+270) if rear else (245,-650,target[2]+270))
    cam.SetViewUp(0,0,1); cam.ParallelProjectionOn(); cam.SetParallelScale(32 if detail else 137 if exploded else 99)
    light=vtk.vtkLight(); light.SetLightTypeToSceneLight(); light.SetPosition(-180,-380,450); light.SetFocalPoint(0,0,85); light.SetIntensity(.7); ren.AddLight(light)
    win=vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(1700,1400); win.SetMultiSamples(8); win.AddRenderer(ren); win.Render()
    cap=vtk.vtkWindowToImageFilter(); cap.SetInput(win); cap.Update(); writer=vtk.vtkPNGWriter(); writer.SetFileName(str(path)); writer.SetInputConnection(cap.GetOutputPort()); writer.Write(); win.Finalize()
    im=Image.open(path).convert('RGB'); draw=ImageDraw.Draw(im)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    draw.text((70,42),'PHOTO FIGURE  /  ARTBOARD V3',font=ImageFont.truetype(font,29),fill='#354052')
    draw.text((70,88),'DETAIL VIEW  |  smiling face / chest bow / collar' if detail else 'EXPLODED ASSEMBLY  |  %d detachable pieces'%len(parts) if exploded else 'ASSEMBLED MODEL  |  183 mm board / 150 mm nominal height',font=ImageFont.truetype(font,19),fill='#6b7583')
    draw.text((70,1344),'Photo-based proportions  •  Sculpted clothing & face  •  Keyed joints  •  0.20 mm radial clearance',font=ImageFont.truetype(font,17),fill='#6b7583')
    im.save(path)

render(ROOT/'previews/assembled_render.png')
render(ROOT/'previews/exploded_render.png',exploded=True)
render(ROOT/'previews/front_render.png',front=True)
render(ROOT/'previews/rear_render.png',rear=True)
render(ROOT/'previews/details_render.png',detail=True)

# Export standalone STL files on the build plane. Original assembly-space STL
# remains available separately, and no shape is scaled.
printdir=ROOT/'print_stl'; printdir.mkdir(exist_ok=True)
for p in manifest:
    m=meshes[p['id']].copy()
    if p['id'].startswith('P03_Dowel'):
        m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0]))
    if p['id']=='P12_PaddleLower':
        axis=np.array(design['pole_axis']); axis=axis/np.linalg.norm(axis)
        m.apply_transform(trimesh.geometry.align_vectors(axis,[0,0,1]))
    if p['id']=='P13_PaddleUpper':
        axis=np.array(design['pole_axis']); axis=axis/np.linalg.norm(axis)
        m.apply_transform(trimesh.geometry.align_vectors(axis,[0,0,1]))
    m.apply_translation([-m.bounds[:,0].mean(),-m.bounds[:,1].mean(),-m.bounds[0,2]])
    m.export(printdir/(p['id']+'.stl'))

# Decimated meshes are ONLY used by the offline browser preview.
viewer=[]
for p in parts:
    pd=poly_from_mesh(meshes[p['id']],color_triangles(meshes[p['id']],p))
    dec=vtk.vtkQuadricDecimation(); dec.SetInputData(pd); dec.SetTargetReduction(.76); dec.Update()
    out=pd if p['id'] in ['P01_Board_Left','P02_Board_Right','P12_PaddleLower','P13_PaddleUpper'] else dec.GetOutput()
    from vtk.util.numpy_support import vtk_to_numpy
    verts=vtk_to_numpy(out.GetPoints().GetData()); faces=vtk_to_numpy(out.GetPolys().GetData()).reshape(-1,4)[:,1:]
    mm=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    viewer.append({'id':p['id'],'label':p['label'],'v':verts.round(3).tolist(),'n':mm.vertex_normals.round(5).tolist(),'f':faces.tolist(),'c':color_triangles(mm,p).tolist(),'offset':OFFSETS[p['id']]})
(ROOT/'source/viewer_data.json').write_text(json.dumps(viewer,separators=(',',':'),ensure_ascii=False))
print('Validated',len(manifest),'watertight meshes; rendered five previews; created print_stl and offline viewer data.')

# Dedicated deck views show the actual curvature and printable engraving.
def render_deck_view(path,side=False):
    ren=vtk.vtkRenderer();ren.SetBackground(.955,.962,.973)
    for p in parts:
        if p['id'] not in ['P01_Board_Left','P02_Board_Right']:continue
        pd=poly_from_mesh(meshes[p['id']],color_triangles(meshes[p['id']],p))
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(pd);normals.SetFeatureAngle(65);normals.ConsistencyOn()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.SetScalarModeToUseCellData();mapper.SetColorModeToDirectScalars()
        actor=vtk.vtkActor();actor.SetMapper(mapper);mapper.SetInputData(pd);actor.GetProperty().SetInterpolationToFlat();actor.GetProperty().SetAmbient(.30);actor.GetProperty().SetDiffuse(.70);actor.GetProperty().SetSpecular(.18);actor.GetProperty().SetSpecularPower(35);ren.AddActor(actor)
    cam=ren.GetActiveCamera();cam.SetFocalPoint(0,0,6);cam.SetPosition((0,-700,17) if side else (140,-210,300));cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(34 if side else 67)
    light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(-140,-250,400);light.SetFocalPoint(0,0,6);ren.AddLight(light)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1700,410 if side else 850);win.SetMultiSamples(8);win.AddRenderer(ren);win.Render()
    cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(cap.GetOutputPort());writer.Write();win.Finalize()
render_deck_view(ROOT/'previews/deck_top.png')
render_deck_view(ROOT/'previews/deck_side.png',True)
canvas=Image.new('RGB',(1700,1470),'#f4f5f8');draw=ImageDraw.Draw(canvas);font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
draw.text((70,35),'艺术滑板 V3 · 曲面与可打印花纹',font=ImageFont.truetype(font,34),fill='#354052')
draw.text((70,87),'圆头轮廓 / 双端上翘约 6.7 mm / 横向浅凹约 1.5 mm / 流线与花瓣浅刻',font=ImageFont.truetype(font,22),fill='#6b7583')
canvas.paste(Image.open(ROOT/'previews/deck_top.png'),(0,135))
draw.text((70,995),'侧面轮廓：中央站立区域平整，两端连续翘起',font=ImageFont.truetype(font,24),fill='#354052')
canvas.paste(Image.open(ROOT/'previews/deck_side.png'),(0,1040))
draw.text((70,1430),'刻槽深约 0.55 mm、宽约 1.3 mm；金色为补漆示意。脚部插孔与板体拼接结构保留。',font=ImageFont.truetype(font,20),fill='#6b7583')
canvas.save(ROOT/'previews/artboard_detail.png')
