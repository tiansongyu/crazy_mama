if 'Photo_Figure_Artboard_Exploded' in App.listDocuments():App.closeDocument('Photo_Figure_Artboard_Exploded')
offsets={'P01_Board_Left':(-15,0,0),'P02_Board_Right':(15,0,0),'P03_Dowel_1':(0,-40,5),'P03_Dowel_2':(0,-40,5),'P04_Leg':(-12,0,12),'P05_Leg':(12,0,12),'P06_Torso':(0,0,27),'P07_LeftArm':(-34,0,30),'P08_RightArm':(34,0,30),'P09_Head':(0,0,65),'P10_Collar':(0,0,47),'P11_Hair':(38,0,70),'P12_PaddleLower':(-32,0,8),'P13_PaddleUpper':(-32,0,33),'P14_Bow':(0,-38,28)}
expl=App.newDocument('Photo_Figure_Artboard_Exploded')
for old in parts:
    ob=expl.addObject('PartDesign::Feature',old.Name);ob.Label=old.Label;ob.Shape=old.Shape.copy();ob.Placement.Base=V(*offsets[old.Name])
    ob.ViewObject.ShapeColor=old.ViewObject.ShapeColor;ob.ViewObject.DiffuseColor=old.ViewObject.DiffuseColor;ob.ViewObject.DisplayMode='Flat Lines'
expl.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();Gui.updateGui();expl.saveAs(ROOT+'/Photo_Figure_Artboard_Exploded.FCStd')
App.setActiveDocument(doc.Name)
assembly.Visibility=True
for obj in parts:obj.Visibility=True;obj.ViewObject.DisplayMode='Flat Lines'
for obj in [co,tp]:obj.Visibility=False
guides.Visibility=False
direction=V(.26,-.91,.31);rightv=V(.96,.275,0);up=direction.cross(rightv)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(rightv,up,direction,'ZXY').Q)
Gui.activeDocument().activeView().fitAll()
for _ in range(3):Gui.updateGui();QtCore.QCoreApplication.processEvents()
doc.save()
Gui.activeDocument().activeView().saveImage(ROOT+'/previews/freecad_refined.png',1500,1300,'White')
log('FINALIZE_COMPLETE')
