# 第91项 · Goodspeed Hall 独栋候选

**已修 32 个悬浮构件实例（近/中档各5条腰线；近档19条低窗外饰、3件入口圆饰），并按现代正射统一三档屋脊。只通过云端离线复验，不是整栋实景通过或游戏可发布版。** 独栋和 HarperCourtyardAssembly 同名网格不是一个源，本次只改前者。

## 改动与复验

| 部位 | 原状 | 离线候选 |
|---|---|---|
| 两侧腰线 | 近、中各6条长带，后缘距外墙 20 mm | 每档5条后缘内移22 mm，保住向外轮廓；最下层东侧第6条保持原件（见下） |
| 低窗外饰条 | 近档19条外露后缘离外墙 45 mm | 各自后缘2点向内延47 mm；窗藏于墙体内的另19条不误修 |
| 入口圆饰 | 近档3件后缘距外墙 67.5 mm | 等距向墙内69.5 mm，不压扁构件、不动门洞 |
| 屋脊 | 近中突起在Y=+6.831m，远档跳到Y=0；原堆体已嵌屋面，并非悬浮 | 现代版本删34/32/12个独立三角，底下原坡面连续，702个屋顶采样点全部命中原坡面，不人为填洞；保留原版作历史线索 |

独立复验 528 个接触点（低窗228+圆饰180+腰线120），均命中朝外墙面，预留约2mm嵌入。分开检查新交叠：剩余腰线有同立面窗框/端墙的接口，低窗饰与同窗框相交，圆饰只与对应外墙相交；未新增门洞或门框内凹面交叠。首次试改曾在两档最下层东腰线 Y≈0.253m 接触既有入口回折面，整条改动被撤回，待结合实景入口分段处理，未标成通过。实际动作只动264/10/0个坐标，未动的24,819/11,255/228个有向三角角法线完全一致；全模型坐标及属性对比符合预期，10份内嵌贴图未动。原地零标高三角16/16/2仍在，不是整栋悬浮；原地块不等于游戏地形或门槛标高。

Blender 实际导出并回读三档 FBX：25,405／11,295／228 三角，保留有向三角全部匹配，最大坐标差约4.3微米，UV 差0；三档未检出退化、重合或越界/零面积UV。在导出转换中使用 FBX 7500 结构，不把它当 Autodesk FBX 2018 或 CS2 Editor 验收。保留原版 LOD1 共享纹理配置，没用它推断游戏内存。

## 实景证据与未通过项

- [芝大 Facilities 图层2](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2)，FID254，EPSG26916，测得平面外包约14.17（东西）×25.22（南北）米。近档包围盒含出挑构件约14.51×26.00米，合理作为配准起点，不据不同定义对整栋做比例拉伸。位于 Gates 南侧、Classics 北邻接端；官方 [无障碍校图](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/7/4088/files/2025/03/2025-02-24-Revised-ADA-Map-PDF.pdf)指 Goodspeed 北侧入口。原件北端是闭合面，不等于总装入口、通道或净空已验证。
- 县 [2024](https://img.cookcountyil.gov/arcgis/rest/services/CookOrtho2024/ImageServer/info/iteminfo)／[2025](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer/info/iteminfo)正射均实际目视。两张为相同 EPSG26916 检查窗(E450036–450100,N4626401–4626465)、640×640，约每输出像素0.10m，不是原始分辨率。校方平面标出南端 Goodspeed，屋脊以 y≈235–450 连续可见段辨识；原模型近/中和远档的两处突起在清晰段内均未辨识到，北方相邻屋顶可见另一突起，未从邻楼移植。靠南邻接端受阴影与屋顶设施遮挡。本修订仅取近年可见屋脊，不推论整栋从未有烟囱。校馆[Ellis 西立面档案](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-02071.xml)的南翼历史坡顶确可见一处竖向突出，年代与 2024/25 不能混用。
- 西立面体量是仍待查的关键：GIS 西侧是两处外凸（实图不是栏杆净尺寸）；近档模型的突出多层凸窗是另一种形状/分段。[1940年 Gates 东凸窗档案](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-02078.xml)不能引用为 Goodspeed 西凸窗实证。先补同年代清楚立面与段界，再定保留、改形或撤除。窗轴、南北接缝、落地与游戏试导入没有验收。

## 在原始独栋副本复现

使用 [按源文件 SHA 锁定的重建脚本](../candidates/20261119-building-review/goodspeed_modern_ridge.py)：`blender -b --disable-autoexec ORIGINAL.blend --python-exit-code 1 --python goodspeed_modern_ridge.py -- NEW.blend`。已另生成重放文件，实际读取后对比四个网格的坐标、拓扑、UV、材质索引、角法线及10份内嵌贴图记录完全一致。脚本不覆盖既有文件，不导出 FBX；验证后的 FBX 和编译前 Blend 另行交付，不将模型二进制写入本提交。
