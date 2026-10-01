from pathlib import Path
import json
from PIL import Image,ImageOps,ImageDraw,ImageFont

R=Path(__file__).resolve().parents[1]
reports=[json.loads((R/'iterations'/f'{n:02d}'/'report.json').read_text()) for n in range(1,11)]
assert [p['round'] for p in reports]==list(range(1,11))
assert all(p['watertight_meshes']==18 and p['interference_count']==0 for p in reports)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
F=lambda size:ImageFont.truetype(font,size)
titles=['面部曲面','下颌与颈部','短发与发色','五官体积','自然笑容','轻巧眼镜','宽松上衣','手指浅纹','蝴蝶结褶线','曲面收尾与定位销']
notes=['统一曲线参数、消除异常起伏','柔和下颌，改善颈部衔接','贴近原图短发，减小蓬松度','收敛鼻翼、面颊和唇部体积','嘴角小幅上扬，保持亲切感','缩窄镜框，修正鼻梁曲线','保留照片中自然宽松的身形','指关节浅刻，保持手掌整体','双结环增加浅褶线，装饰克制','额头至下颌平顺化；加粗销并倒角']
sheet=Image.new('RGB',(1800,3740),'#eef1f6');draw=ImageDraw.Draw(sheet)
draw.text((55,30),'微笑阿姨 · 10 轮实际模型迭代',font=F(44),fill='#26354a')
draw.text((55,97),'约 15 cm｜保留原图衣形与板上姿态｜每轮保存网格预览与检查记录',font=F(25),fill='#5a687a')
for n in range(1,11):
    x=40+880*((n-1)%2);y=155+710*((n-1)//2)
    draw.rounded_rectangle((x,y,x+840,y+675),radius=18,fill='white')
    draw.text((x+24,y+18),f'{n:02d}  {titles[n-1]}',font=F(32),fill='#26354a')
    p=R/'iterations'/f'{n:02d}'
    if n<=6:
        im=Image.open(p/'face.png').convert('RGB').crop((455,145,1225,805))
    elif n==7:
        im=Image.open(p/'assembly.png').convert('RGB').crop((440,250,1180,1010))
    elif n==10:
        im=Image.open(p/'focus.png').convert('RGB').crop((130,135,1570,1280))
    else:
        im=Image.open(p/'focus.png').convert('RGB').crop((220,135,1500,1280))
    im=ImageOps.contain(im,(790,535));sheet.paste(im,(x+(840-im.width)//2,y+77+(535-im.height)//2))
    draw.text((x+24,y+625),notes[n-1],font=F(22),fill='#536176')
draw.text((55,3720-36),'实际 CAD / STL 渲染，颜色为上色示意；不是精确肖像扫描，尚未实物试打。',font=F(23),fill='#667386')
sheet.save(R/'previews/ten_iterations.png')

lines=['# 微笑阿姨 · 10 轮迭代记录','','已完成 10 轮。在约 150 mm 总高内保留原图的粉色宽松上衣、深色长裤、黑鞋、握杆与板上姿态。喜剧感来自轻轻上扬的嘴角、椭圆眼镜和胸口小蝴蝶结，身体与头部比例保持克制。','','每一轮均执行 FreeCAD 实体检查、STL 封闭性/面朝向/正体积/单连通检查和装配体积干涉检查。每轮为 16 个装配分件、2 个配合测试件，检查通过后才进入下一轮。预览均来自当轮实际导出的 STL。','','| 轮次 | 修改 | 预览 | 检查记录 |','|---|---|---|---|']
for n,p in enumerate(reports,1):
    preview='face.png' if n<=6 else 'assembly.png' if n==7 else 'focus.png'
    lines.append(f"| {n:02d} | {p['title']} | [查看](iterations/{n:02d}/{preview}) | [18 件通过，干涉 0](iterations/{n:02d}/report.json) |")
lines += ['','![十轮对比](previews/ten_iterations.png)','','## 第 10 轮完成后的模型','','- [FreeCAD 装配文件](Aunt_Figure_V4.FCStd)、[拆分文件](Aunt_Figure_Exploded.FCStd)、[STEP](Aunt_Figure_Assembly.step)。','- [离线交互预览](交互预览.html)：可旋转、查看背面、逐件隐藏和拆分。','- [打印与装配说明](打印与装配说明.md)、[装配连接图](装配与连接图.pdf)。','- 镜框宽约 0.70 mm，定位销名义直径 1.42 mm、长度 2.33 mm，销端倒角约 0.15 mm；新增小销试配孔。','- 配合名义径向余量 0.20 mm；人物轴线相对板面法线约 8°，相对中央板面约 82°。','','## 保留记录与限制','','`iterations/01` 至 `10` 保留当轮预览、主要生成代码、参数和零件网格指纹；最终可打印 STL 在 `print_stl/`。每轮记录不是一套独立的原生 CAD 备份，原生模型与打印文件对应第 10 轮最终版。','','第 6 轮初次检查发现眼镜鼻梁曲线处的微小网格重叠，修正连接曲线并重新导出后通过检查；失败结果没有作为已完成轮次。','','图中发色、眼睛、嘴唇、衣服与刻槽颜色为上色建议，STL 不携带颜色。单张模糊照片的精确五官与背面无法直接恢复，模型保留适度的艺术化补全。未进行真实切片、打印或实物装配，先打印大小接头测试件。','']
(R/'10轮迭代记录.md').write_text('\n'.join(lines))
(R/'source/ten_iteration_summary.json').write_text(json.dumps({'completed_rounds':10,'reports':reports},ensure_ascii=False,indent=2)+'\n')
print('Created ten-iteration contact sheet and linked review record.')
