# 第93项 · Gates Hall 中央段与 Gates–Blake 合体离线候选

**中央 Gates：50 个悬浮构件实例修复；按近年影像让三档都保留西坡同一烟囱。北侧 Blake 的第92项修复全部保留。这是外壳离线候选，未合验邻楼接缝或进游戏。**

|部位|检查及修复|
|---|---|
|近景21处低窗外饰、22处上层窗下饰|原后缘离墙45mm，向墙内延47mm，正面轮廓不动|
|近/中各2条上部独立腰线|原悬空20mm，后缘延22mm；4条低/中腰线横跨 Gates 与 Blake，原样保留，待总装时分段|
|东入口3件圆饰|原后缘离墙67.5mm，等距向内69.5mm；不补不切入口|
|东侧三层凸窗|历史图证实 Gates 独有。近/中各16个接合采样同平面；远档32点（29墙面，3原背板）。不把15–25mm贴花距离认成凸窗悬浮，不整体移动|
|烟囱|原近/中有两处脊线突起、远档无。只保留现代图可确认的那处：西坡中心 X=-1.30/Y=-15.05m，脚底 Z=25.31m 是模型坡配值；远景复用同一资产的低模简体及UV。另一个北侧突起不保留在当代候选，原版未覆盖。|

## 资料与适用范围

- [校馆正东历史图 apf2-02070](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-02070.xml)及 [1940年凸窗图 apf2-02078](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-02078.xml)支持主入口上方连续凸窗和周边五层中央体量，不能用作实测细部。
- 读 [2024](https://img.cookcountyil.gov/arcgis/rest/services/CookOrtho2024/ImageServer/info/iteminfo)／[2025](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer/info/iteminfo) 同框正射，实际参数 EPSG26916，E450036–450100/N4626436–4626500、640×640，约0.10m/输出像素。Gates 西坡清楚的帽顶两年都在 (x约274–277,y约476–483)，旁边脊线 x≈286–288（坐标为原640图从左上计）；用 Blake 同框对齐和 [Facilities FID221](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2) 检查相对位置，给出候选位置而非测绘。北侧旧模型约 y≈397 附近屋脊未见等高大烟囱，不以邻楼或细小阴影当第二根；不推论历史上从未存在，不从阴影给绝对高度。实际屋顶分脊、屋面交接比现模型复杂，后续单独校形。
- [2017校方内路记录](https://college.uchicago.edu/news/student-stories/secret-passageways)本次直连404，搜索索引可读完整正文。Cobb 二层向南转折下短梯至 Gates–Blake，至 Goodspeed 经两道门，Goodspeed 到 Classics 需左转上半层入小壁龛。只用作历史连通与相对高差，不能拿来开墙、造室外桥、承诺净空或现行通行。Cobb–Blake 既有外墙直接接触结论不变；历史接触研究旧源并非本候选的总装验证。

## 云端离线验收

独立复验：744个饰件点都达约2mm接合；同窗框、檐端的接触属预期，未发现新增入口、凸窗或玻璃碰撞。495个新烟囱脚采样均与屋面相交（0.116–0.831m），原位置另外660点没有采样漏孔。验证屋脊不是靠看图判无洞。独立比对其余有向三角位置/UV/材质符合预期，不受影响面法线不变，10份内嵌纹理未改，Gates 之外 Blake 及原基础保留。

三档真正 FBX 重新导入 Blender **57,721／25,569／473** 三角，缺增0，点最大差约5.4μm，UV差0，未发现重复/退化/零面积UV。另一次从脚本重放的 Blake 源文件继续重建，4个网格和10图和候选一致。保留原中景共享贴图设置；FBX7500结构不是 Autodesk 2018 或 CS2 Editor 验收。外墙、实际坡地/入口、屋顶实测形状以及组合接合尚未放行。

## 组合接缝约束


校方学院 2017-05-16 [Secret Passageways](https://college.uchicago.edu/news/student-stories/secret-passageways)直链本次开404，搜索索引保留完整正文，另有学校 2024 年[校友报道](https://college.uchicago.edu/news/student-stories/anna-chlumsky-ab02-named-uchicagos-2024-class-day-speaker)支持历史上 Cobb 至 Goodspeed 有内部连通，但不核级差。路线顺序，仅作模型审核提示：

|接口|2017 文字指向|不据此绘制|
|---|---|---|
|Cobb → Blake｜Gates | 从 Cobb 二楼向南，走廊末端右折后下短梯 | 不另建室外连廊；不按平层通道做高差 |
|Gates–Blake → Goodspeed | 长廊尽端穿两道门 | 不给净宽、门扇朝向或过梁标高 |
|Goodspeed → Classics | Goodspeed 出门后左转，半层楼梯上升至小壁龛再穿门 | 不给半层精确米数，不等同运营或无障碍路径 |

2025 [ADA 校图](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/7/4088/files/2025/03/2025-02-24-Revised-ADA-Map-PDF.pdf)把 Goodspeed 无障碍入口指向北侧，不能反推为上述二层门或直通邻楼。旧 Cobb 接合研究模型采用临时源拟合，Cobb 以 (2.5,58.2,0)m 平移与 Blake 原 y28.6 接触；只供定位，历史 JSON 不代表现候选尺寸或同源哈希。当前三档仍封闭接合面，只适于独立入口/外壳测试；不从网页指引在墙中切开不可证实的步行路径。

下一轮总装即使比对正射/设施边界，也要分别检查外壳接触、檐口、墙面互穿、贴图跃迁和地面入口。真实室内坡级和门几何另找分层图或现状测量。禁止为填空再创一个单独“Cobb连廊建筑”。

[本轮脚本](../candidates/20261119-building-review/gates_central_geometry.py)以 [第92项可重现输出](../candidates/20261119-building-review/blake_north_geometry.py)为基线，验证网格和内嵌贴图的指纹，拒绝错版和覆盖。不提交 Blend/FBX 二进制，源文件及导出另行交付。
