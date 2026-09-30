# crazy_mama · 艺术滑板人物 V3

15 厘米人物与艺术滑板的可拆分 3D 模型，支持旋转、缩放、正面 / 背面切换、部件隐藏和爆炸拆分。

**在线预览：** [https://tiansongyu.github.io/crazy_mama/](https://tiansongyu.github.io/crazy_mama/)

无需安装 FreeCAD，直接用支持 WebGL 的浏览器打开链接即可查看。也可下载仓库后，直接打开 `index.html` 或 `交互预览.html` 离线查看。

## 模型与说明

- [打印与装配说明](打印与装配说明.md)
- [装配与连接图](装配与连接图.pdf)
- [FreeCAD 装配模型](Photo_Figure_Artboard_V3.FCStd)
- [FreeCAD 拆分模型](Photo_Figure_Artboard_Exploded.FCStd)
- [STEP 装配模型](Photo_Figure_Artboard_Assembly.step)
- [打印 STL 文件](print_stl/)
- [预览效果图](previews/)

## GitHub Pages 发布

在仓库 **Settings → Pages** 中选择 **Deploy from a branch**，分支设为 **main**，目录设为 **/(root)**。保存后，GitHub 会发布上述在线预览地址；以后推送到 `main` 会自动更新网站。

`index.html` 是网站首页，`.nojekyll` 让 GitHub 直接发布静态文件。模型数据内嵌于 HTML，预览不依赖外部 CDN。所有下载链接均使用相对路径，适配仓库的 Pages 地址。

GitHub Free 需要公开仓库才能启用 Pages；私有仓库需要支持 Pages 的付费套餐。参见 [GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。在线链接需启用 Pages 并完成部署后才可访问。

重新生成模型预览时，`source/package_previews.py` 会同时更新 `交互预览.html` 和 `index.html`。
