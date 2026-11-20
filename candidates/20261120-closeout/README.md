# 芝大修复收尾与 CS2 待验项

本批从草稿提交 `4873aa96a425c7319e0552c9f4debcdeef0476ab` 开始。三校离线首检维持 **119/119**，编辑器与游戏验收为 **0/153**。

- **Saieh Hall** 西北庭院近、中档的五组上部窗、五扇廊窗和两扇老虎窗正面朝向均有原建模程序和图集依据。仅翻转这些窗口的近档 144 面、中档 124 面。固定近景以 192×192 射线取样，近档首命中背面像素从 9,477 降至 352，中档从 9,544 降至 262。轮廓覆盖和命中深度在该样本内一致，位置、材质和逐角 UV 保留。两份近中 FBX 合计减少 336 字节。对从差量恢复的成套目录实际回导三档 FBX 7500，均为零退化面、角点 UV 差 0、相对贴图引用可解析。远档使用前批字节。剩余背面样本含边饰、檐底及返回面，需逐处判定。 [前后同镜图](previews/saieh-court-before-after.jpg) · [抽样数据](evidence/saieh-visibility.json) · [三档回读](evidence/saieh-package-readback.json)
- **Tower Group** 的 Reynolds–Mandel 理论接面零命中位于组坐标 (13.7075, −4.0, 2.0) m。对完整四栋组合在该点周围 ±0.3 m，从北、南、东、西各作 7×7 组射线。三档共 588 条射线的第一命中均为正面，原源与现候选的第一命中位置一致。没有找到外部可见穿洞的证据，保留接缝凹入和原有几何。 [坐标和射线](evidence/probe-and-topology.json)
- **Harper Memorial Library** 复查近档和中档各 12 个先前最明显的背面命中。相连面组只有 1–3 个三角，每组有 3–5 条开放边；采样包括塔窗斜饰条、檐底及侧向返回。开放面组的拓扑和档案照片不足以确定应加厚的位置或哪一面应向外，保留现候选，待编辑器近景验证可见缺损。 [面组和法线](evidence/probe-and-topology.json) · [校方建筑页](https://architecture.uchicago.edu/locations/william_rainey_harper_memorial_library/)

## Ryerson 与 Kent 的实景资料

- **Ryerson** 的 1911 年校刊由参与扩建的 Millikan 撰写，说明当时正在建造的北附楼边长约 18.29 m，仅以约 4.57 m 长的首层拱廊衔接。这是连廊长度，档案未在这段正文提供宽、净高或现今坐标。1893 年首层图先于该扩建；档案索引将 1910 扩建和 1927–1929 改建分列在 Box 28、Folder 8–9。仍需取得相关图纸或实测，才可移动现模型上贴接的北附楼。 [1911 年校刊](https://campub.lib.uchicago.edu/text/?docId=mvol-0001-0016-0000) · [原首层图](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-07148.xml) · [校方档案索引](https://www.lib.uchicago.edu/e/scrc/findingaids/view.php?eadid=ICU.SPCL.BG)
- **Kent** 校方建筑资料确认讲堂为八角形。1934 年北讲堂外观照可定位屋顶、转角和立面；档案另列 Box 23、Folder 6–7 的初建机电规格和 1909 年改建规格。没有取得可按比例落位的现状北讲堂平面，也未取得连接体折点和坡地标高，保留原模型。 [校方建筑说明](https://architecture.uchicago.edu/locations/main_quadrangle/) · [1934 年外观](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-04692.xml) · [校方档案索引](https://www.lib.uchicago.edu/e/scrc/findingaids/view.php?eadid=ICU.SPCL.BG)

本环境访问校方 Facilities 图层 2 的请求返回 HTTP 403，未取得新的建筑边界要素。Baker 庭院与采光窗仍缺高程控制。 [Facilities 图层](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2) · [Baker 高程记录](../20261120-continuation/baker-noaa-point-cloud.md)

## 快速实机验收

需要一台获准使用的独立 Windows 64 位测试机或云工作站，带可用的 GPU 加速和可写工作区，已安装获授权的 Cities: Skylines II，能打开主菜单里的 Editor 并运行测试地图。游戏版本和硬件随验收结果记录。 [Steam 系统要求](https://store.steampowered.com/app/949230/Cities_Skylines_II/#app_requirements)

1. 在 Editor 的 Asset Importer 指向完整的候选目录，保留相对 PNG、设置和各档网格。先导入 Saieh、Harper 与 Tower Group，记录导入版本、日志、尺度和材质。 [Paradox 导入流程](https://www.paradoxinteractive.com/games/cities-skylines-ii/news/adding-custom-assets)
2. 用空地图和平、斜两种地面检查窗口剔背、昼夜材质、塔群接缝和地面贴合。启用游戏镜头从近到远经过各档，记录 LOD 跳变、闪面、透明、碰撞及通行。
3. 本地保存后在游戏中重载。用同一视角截图，登记测试版本、资产 SHA、结果和报错。先用这三组确认流程，再做完整资产的逐项验收。合并仍取决于所需实机检查及未解决的实景差异。

## 复现 Saieh 修复

从[经校验的技术源树](../20261118-technical/README.md)恢复，本批目录仅影响 Saieh，前批的 Harper 和 Tower 继续采用各自候选。Python 需要 `zstandard==0.25.0`。在仓库根目录使用新输出路径。

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/saieh-blend --patch-dir candidates/20261120-closeout/source-delta
python candidates/20261120-continuation/apply_export_overlay.py /path/to/technical-tree /path/to/saieh-pack --patch-dir candidates/20261120-closeout/export-overlay
```

要从前批 Saieh 源重做编辑，可用 [repair_saieh_court.py](repair_saieh_court.py)；正文中的回读直接使用完整技术源树精确还原的最终文件。 [源差量及 SHA](source-delta/manifest.json) · [FBX 差量及 SHA](export-overlay/manifest.json)

同镜图的庭院视角在 [compare_visibility.py](../20261120-completion/compare_visibility.py) 使用 `--focus -23.14 3.44 11.8 0 -1 .02 25 9`，前档为前批精确还原的 `Saieh_windows.blend`。
