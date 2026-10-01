# 微笑阿姨 · 10 轮细化 V4

15 厘米人物：短侧分发型、椭圆眼镜、自然微笑、胸口蝴蝶结与艺术滑板。16 个装配分件，另附 2 个配合测试件。

**在线 3D 预览：** [https://tiansongyu.github.io/crazy_mama/](https://tiansongyu.github.io/crazy_mama/)

直接用支持 WebGL 的浏览器打开即可查看，无需安装 FreeCAD。可拖动旋转、滚轮缩放、查看正面 / 背面、逐件隐藏和拆分。

- [10 轮迭代记录](10轮迭代记录.md)
- [离线交互预览](交互预览.html)
- [FreeCAD 装配模型](Aunt_Figure_V4.FCStd)
- [FreeCAD 拆分模型](Aunt_Figure_Exploded.FCStd)
- [STEP 模型](Aunt_Figure_Assembly.step)
- [打印与装配说明](打印与装配说明.md)
- [装配与连接图](装配与连接图.pdf)

打印 STL 在 `print_stl/`，保留装配坐标的 STL 在 `stl/`。原版保留在独立目录中。本版尚未实物打印；面部根据单张模糊照片与指定造型补全。

## GitHub Pages

网站首页为 `index.html`，内容与 `交互预览.html` 一致，模型数据内嵌，不依赖外部 CDN。`.nojekyll` 用于直接发布静态文件。

仓库的 Pages 发布源为 **main / /(root)**。推送到 `main` 后会自动更新上述在线地址。`source/package_previews.py` 会同时生成在线首页与离线预览。
