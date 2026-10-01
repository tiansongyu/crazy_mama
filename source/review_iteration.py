from pathlib import Path
import json,shutil,hashlib,datetime
R=Path(__file__).resolve().parents[1]
state=json.loads((R/'source/current_iteration_complete.json').read_text())
cfg=json.loads((R/'source/iteration_config.json').read_text())
assert state['round']==cfg['round'] and state['interference_count']==0
destination=R/'iterations'/('%02d'%cfg['round']);destination.mkdir(exist_ok=True)
# Reuse the actual printable meshes and the standard scene, without rerunning CAD.
src=(R/'source/render_and_validate.py').read_text().split("render(ROOT/'previews/assembled_render.png')")[0]
g={'__file__':str(R/'source/render_and_validate.py')}
exec(compile(src,str(R/'source/render_and_validate.py'),'exec'),g)
g['render'](destination/'face.png',detail=True)
g['render'](destination/'assembly.png')
if cfg['round']==8:g['render'](destination/'focus.png',detail=True,target_override=[37.3,-3,66.5],zoom_override=6,caption='ROUND 08 | subtle finger-joint creases')
if cfg['round']==9:g['render'](destination/'focus.png',detail=True,target_override=[8.9,-12,107.5],zoom_override=7,caption='ROUND 09 | restrained ribbon folds')
if cfg['round']==10:g['render'](destination/'focus.png',rear=True,target_override=[10.5,-5,137.4],zoom_override=11,only_parts=['P15_Glasses'],caption='ROUND 10 | reinforced locating pins and lead-in chamfers')
validation=json.loads((R/'source/mesh_validation.json').read_text())
assert len(validation)==18 and all(p['watertight'] and p['consistent_winding'] and p['positive_volume'] and p['connected_shells']==1 for p in validation)
report={'round':cfg['round'],'title':cfg['title'],'config':cfg,'checked_at':datetime.datetime.now().isoformat(),
        'assembly_parts':16,'watertight_meshes':18,'interference_count':0,
        'head_stl_sha256':hashlib.sha256((R/'stl/P09_Head.stl').read_bytes()).hexdigest(),
        'hair_stl_sha256':hashlib.sha256((R/'stl/P11_Hair.stl').read_bytes()).hexdigest(),
        'glasses_stl_sha256':hashlib.sha256((R/'stl/P15_Glasses.stl').read_bytes()).hexdigest(),
        'torso_stl_sha256':hashlib.sha256((R/'stl/P06_Torso.stl').read_bytes()).hexdigest(),
        'right_hand_stl_sha256':hashlib.sha256((R/'stl/P08_RightArm.stl').read_bytes()).hexdigest(),
        'bow_stl_sha256':hashlib.sha256((R/'stl/P14_Bow.stl').read_bytes()).hexdigest()}
(destination/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name in ['iteration_config.json','aunt_geometry.py','update_aunt.FCMacro','build_refined.FCMacro','iteration_details.py']:
    shutil.copy2(R/'source'/name,destination/name)
for name in ['mesh_validation.json','parts_manifest.json','interference_audit.json']:
    shutil.copy2(R/'source'/name,destination/name)
print(json.dumps({'round':cfg['round'],'title':cfg['title'],'status':'geometry, mesh and assembly checks passed','preview':str(destination/'face.png')},ensure_ascii=False))
