from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
plan=[
 ('面部曲面连续性与细节采样','fixed_parameterization'),
 ('柔和下颌与自然颈部过渡','soft_jaw'),
 ('参考照片的贴头短发与灰棕发色','compact_hair'),
 ('收敛鼻翼、面颊与唇部体积','restrained_features'),
 ('克制而亲切的笑容与眼神','warm_smile'),
 ('减轻镜框厚重感与鼻梁连接','slender_glasses'),
 ('恢复原图宽松上衣的腰胸比例','loose_blouse'),
 ('自然手指关节与掌部细节','hand_detail'),
 ('蝴蝶结丝带褶线与装饰层次','bow_detail'),
 ('面部曲面收尾、眼镜定位销强化与导入倒角','print_refinement')]
n=int(sys.argv[1]);assert 1<=n<=10
if n>1:assert (R/'iterations'/('%02d'%(n-1))/'report.json').exists()
cfg={'round':n,'title':plan[n-1][0]}
for title,key in plan[:n]:cfg[key]=True
(R/'source/iteration_config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
(R/'source/request.py').write_text("exec(compile(open(ROOT+'/source/update_aunt.FCMacro').read(),ROOT+'/source/update_aunt.FCMacro','exec'),globals())\n")
(R/'source/iteration_plan.json').write_text(json.dumps([{'round':i+1,'title':t,'key':k} for i,(t,k) in enumerate(plan)],ensure_ascii=False,indent=2)+'\n')
print('Queued round %d / 10: %s'%(n,plan[n-1][0]))
