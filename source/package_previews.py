from pathlib import Path
import json,math
from PIL import Image,ImageOps,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

R=Path(__file__).resolve().parents[1]
template=(R/'source/viewer_template.html').read_text()
data=(R/'source/viewer_data.json').read_text()
js=(R/'source/webgl_viewer.js').read_text()
start=template.index('<script>');end=template.index('</script>',start)
template=template[:start]+'<script>const DATA=__MESH_DATA__;\n'+js+template[end:]
template=template.replace('照片人物 · 可拆分 3D 模型','15 厘米人物 · 艺术滑板版 V3').replace('220 mm','183 mm').replace('≈180 mm','≈150 mm').replace('14 件','15 件')
template=template.replace('Surfer_Modular.FCStd','Photo_Figure_Artboard_V3.FCStd').replace('单张照片的简化立体重建，背面与厚度为补全设计。','身体相对板面法线约倾斜 8°，与板面约 82°。胸口蝴蝶结为独立分件。单张模糊照片的背面与五官为补全设计。')
template=template.replace('身体相对板面法线', '滑板双端上翘约 6.7 mm，两侧浅凹约 1.5 mm；板面流线与花瓣为实刻凹槽，金色为补漆示意。身体相对板面法线')
viewer_html=template.replace('__MESH_DATA__',data)
for name in ('交互预览.html', 'index.html'):
    (R/name).write_text(viewer_html, encoding='utf-8')

font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
f=ImageFont.truetype(font,36);small=ImageFont.truetype(font,24)
comparison=Image.new('RGB',(2200,1280),'#f1f3f7');d=ImageDraw.Draw(comparison)
d.text((50,25),'原照片与 15 厘米细化模型',font=f,fill='#253247')
reference=Image.open('/home/ubuntu/Pictures/zhen.jpg').convert('RGB')
model=Image.open(R/'previews/assembled_render.png').convert('RGB').crop((150,175,1560,1300))
for i,(im,title) in enumerate([(reference,'原照片（单角度、模糊）'),(model,'艺术滑板 V3 · 微笑 / 蝴蝶结 / 板面相对站姿')]):
    fitted=ImageOps.contain(im,(1040,1070));x=40+i*1090;y=117+(1070-fitted.height)//2
    comparison.paste(fitted,(x+(1040-fitted.width)//2,y));d.text((x,80),title,font=small,fill='#536176')
d.text((50,1220),'脸部与背面为保守补全；两侧仅作外观对照，不代表可从单张照片恢复精确三维尺寸。',font=small,fill='#6b778b')
comparison.save(R/'previews/photo_comparison.png')

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
pdf=canvas.Canvas(str(R/'装配与连接图.pdf'),pagesize=landscape(A4));W,H=landscape(A4)
def text(x,y,t,size=12):pdf.setFont('STSong-Light',size);pdf.setFillColorRGB(.15,.20,.28);pdf.drawString(x,y,t)
def line(x1,y1,x2,y2):pdf.setLineWidth(1);pdf.setStrokeColorRGB(.30,.37,.47);pdf.line(x1,y1,x2,y2)
def footer(n):text(34,22,'单位 mm | 示意不按比例 | 未实物试打 | 先打印配合测试件',10);text(W-60,22,str(n),10)
text(34,H-42,'15 厘米人物 V3 · 分件与连接',22)
text(34,H-67,'总高约 150 · 板体长宽约 183.3 × 46.7，中央厚 5.8 · 15 个装配分件 + 2 个测试件',12)
pdf.drawImage(str(R/'previews/assembled_render.png'),26,122,width=380,height=350,preserveAspectRatio=True,anchor='c')
pdf.drawImage(str(R/'previews/exploded_render.png'),418,122,width=380,height=350,preserveAspectRatio=True,anchor='c')
text(40,88,'胸口蝴蝶结独立打印，带防转 D 榫；双臂、双腿、头部、领圈和灰发片分别装配。',12)
text(40,62,'名义径向余量 0.20，常规轴向余量 0.30；先干装，再点胶。',12);footer(1);pdf.showPage()
text(34,H-42,'角度以板面为基准 · 接头名义尺寸',22)
text(42,490,'人物整体轴线相对板面法线约 8°（相对板面约 82°）',14)
x,y=160,246;L=208;dx=L*math.tan(math.radians(8))
pdf.setFillColorRGB(.80,.36,.48);pdf.rect(57,y-12,252,12,fill=1,stroke=0)
line(x,y,x,y+L);pdf.setStrokeColorRGB(.10,.48,.49);pdf.setLineWidth(3);pdf.line(x,y,x+dx,y+L)
pdf.setLineWidth(1);pdf.setStrokeColorRGB(.30,.37,.47)
pdf.circle(x+dx,y+L,8,fill=0,stroke=1);text(x-102,y+L-18,'板面法线',12);text(x+dx+12,y+L-8,'人物轴线',12)
text(x+12,y+88,'8°',14);text(64,y-37,'板面保持水平；夹角不以图片边缘为基准。',11)
text(392,457,'主要配合尺寸（成品名义值）',15)
specs=['板体圆销 Ø3.33，孔 Ø3.73；销长 12.83。','脚部 D 榫 Ø5，伸出约 3.92；孔深约 4.42。','腰部与颈部 D 榫 Ø5.83，插入约 5。','肩部 D 榫 Ø5，插入约 5；孔深约 5.3。','蝴蝶结 D 榫 Ø2.5，插入约 2.5。','杆外径 Ø3.5；接头 Ø1.83，孔 Ø2.23。','D 形平边定位、防转；调整后的方向以实体为准。']
for i,s in enumerate(specs):text(392,430-28*i,s,11)
text(42,155,'测试块：三个 Ø6 D 孔的径向余量依次为 0.15 / 0.20 / 0.25；试针为 Ø6。',12)
text(42,126,'角度用双脚支撑中心到头部中心的连线定义；膝盖、腰、肩保留自然局部姿态。',11)
text(42,98,'数字检查：17 个封闭单连通 STL；15 个装配实体，无检测到的体积干涉。',11)
text(42,71,'单张模糊照片无法恢复不可见的精确五官和背面；笑容与蝴蝶结为指定的新造型。',11)
footer(2);pdf.showPage()
text(34,H-42,'艺术滑板 V3 · 曲度与花纹',22)
pdf.drawImage(str(R/'previews/artboard_detail.png'),24,128,width=550,height=425,preserveAspectRatio=True,anchor='c')
for i,t in enumerate(['双端上翘约 6.7 mm','横向浅凹约 1.5 mm','浅刻深度约 0.55 mm','流线刻槽宽约 1.3 mm','中央脚下平面保留','原定位销和脚部 D 榫保留']):text(593,465-i*40,t,12)
text(40,95,'花纹为真实凹槽，可随 STL 打印；预览金色为槽内补漆建议。',12)
text(40,66,'板体中央底面朝下，翘起端部按需添加可拆支撑；拼接孔内避免不可取出的支撑。',11)
footer(3);pdf.save()
print('Generated offline WebGL viewer, photo comparison, and assembly PDF.')
