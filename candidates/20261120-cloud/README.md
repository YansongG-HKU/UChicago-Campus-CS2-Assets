# 2026-11-20 芝大逐栋复核与模型候选

使用独立 Codex 云环境和 Blender 4.3.2，在 PR #2 的 `4397a06ee7df50b5c8a0a2d421fc8a6abbf1b394` 上继续。对云端可见的八个 r1 基础归档及双层更新所得公开基线执行全量资产路径及 SHA 核对，再在新目录应用 11 个前批候选和 8 个技术差量。最终 8,032 个文件、101 个 Blender 源场景，17 个源相对公开基线改动。原 Dot 未发布工作区与先前未提交的 ZIP 在此环境不可见。Baker 单体坡屋面从已提交脚本重放，网格结果可检查，新 Blend 的容器 SHA 与原附件不同。

## 模型改动与实测

| 对象 | 本轮结果 | 仍需检查 |
| --- | --- | --- |
| Baker Dining 单体 | 重放主绿屋面，近／中／远 4,686／906／382 三角面。三份新 FBX 7500 回读，角点 UV 差 0。10 张不同贴图，5 条既有近中共享映射保留。导入文件夹 652,844 → 569,895 字节，减 12.7%。 | 三个独立庭院样点仍为 5.80 m，分别高于历史观测 0.92、1.13、0.79 m。可见边线有十点控制，缺庭院坡折和采光玻璃窗头窗台标高。ISGS DSM 与 DTM 的新 `getSamples` 查询均返回 HTTP 403。暂保留该部分形态。 |
| Baker × Campus North 组合 | 精确源 `a94fb0b1…`。复用单体坡屋面，删除每档 Baker 隐蔽接线上的两片共面墙，三档各 125.312 m²，由住宅墙保留该边。50 次射线／档，近中远原各 30 处跨两对象同位命中。去面后住宅墙在原测试高度均可命中。近中仍各 5 处是约 45° 的斜收边穿越垂直墙，远档为 0 处。近／中／远 Baker 4,684／904／380 面，住宅三档的有向几何与 UV、原材质绑定及变换保持一致。6 份组合 FBX 7400 作独立几何回读。 | 21.61 m 接线的一段已查。西端转角、屋面收口可见范围、地面通廊在 Editor 的碰撞／基础及临近地形、现场精确配准均待验。组合中的 Baker 接触面是由住宅墙补足的开放边，独栋使用封闭的单体。 |
| Billings Hospital | 锁定原交付 FBX 7500 的近档 `eabd2b1a…` 已在空 Blender 场景完整导入，原三档 195,963／40,049／252 有向面及角 UV 与源一致。源近中档保存完好。远档以两档现有的南入口三级外包形状补 28 三角；20 个原无命中的远档踏面测点现在与近中档一致，三级高 0.16／0.42／0.68 m，全部接模型地面。三档 54 个双塔屋面测点同为 42.0 m。新 7500 三档 195,963／40,049／280 面，角 UV 差 0。独立包 8,336,806 → 8,059,827 字节，减 3.32%；PNG 21 → 10 个，省 278,147 字节，FBX 总量增 1,168 字节。 | 远档入口仍用老的简化面表达退深，材质以原图集裁切域映射。历史范围保留开敞院落，后建院内楼与医院之间的 Goldblatt 连廊未加。精确历史尺寸、塔楼边缘实体／零散缝、实景相机配准待验。 |
| Edward H. Levi Hall | 按 2013 后穿楼现状复核。按三档测 75 条东西向路径射线，45 条在 Z 1.0～2.5 m 均无阻挡，近中同时计入独立玻璃。189 个步道地面采样点均有命中，主穿堂面 Z 0.86 m，远档用两端坡段替代逐级阶梯。独立原交付 7500 五份 FBX（含两档玻璃）有向面及角点 UV 与源一致。 | 独立保留原文件；玻璃游戏着色、无障碍入口、地形和碰撞待验。 |
| Chicago Lying-In Hospital | 原交付 7500 三档 85,151／24,963／398 面有向回读及角 UV 一致。近中五个南拱各四条穿越线均畅通，远档 20 条均被原有代理面挡住，确认为原设定的贴图简化。每档六个墩脚低点有实体，九个塔屋面点均为 38.0 m。 | 已有 2026-10-05 制作交付记录，当前对照原台账未找到独立条目，计为复核证据；开放拱廊的游戏 LOD 和碰撞待验。 |
| Campus North Residential 单体 | 原交付三档 75,560／18,216／234 面 FBX 7500 回读，有向几何与角点 UV 一致。 | 以往北立面折肋和腰带 20 mm 背缝未覆盖面到面全局。窗后仍是实体墙，组合接缝检查未替代单体首检。 |

Billings 原近档在最新全三档进程内回导阶段约 0.57 秒，峰值 RSS 591,456 KiB（含进程前段读取与对比快照）。云运行内存上限 16 GiB，前后 cgroup `oom_kill=0`。历史 7400 对照仍为另一份独立导出。新导出的单体 7500 使用恢复链自带的 64 位记录重序列化器，游戏兼容性仍需 Editor 验证。

实景参照：[Studio Gang 2016 建成项目](https://studiogang.com/projects/university-of-chicago-campus-north-residential-commons/)、[AIA Chicago 项目剖面及图册](https://aiachicago.awardsplatform.com/gallery/dLgYJPQR/OeXxaYoe?search=c5b2f2c77c415f2f-100)、[芝大 Billings 南立面档案](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-00781.xml)、[芝大医学院两栋历史医院资料](https://mbsaa.uchicago.edu/2026/07/evolution-of-the-university-of-chicagos-medical-campus/)和 [Krueck Sexton Levi Portal](https://ks.partners/projects/edward-h-levi-hall-portal)。同镜图为当前候选的 Blender 工作台渲染，未复制来源照片。

## 可复现的交付

- [二进制差量和输出 SHA](patches/manifest.json)、[逐档回读与测点](evidence/)、[同镜图](previews/)。三个 Zstandard 字典差量可逐字节恢复三个真实 Blender 候选。已实际重放并核对每份输出；[已有技术树安装说明](../20261118-technical/README.md)包含基线准备。
- 已校验的旧技术树和所有保存结果相互独立。使用 Python 3.9+ 及 `zstandard==0.25.0` 复现，不覆盖旧树：

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/Campus_Candidate_Technical /path/to/new-review-blends
```

- [Baker 接缝建模脚本](baker_assembly_seam.py)接收精确组合、已重放的独栋坡屋面和新目标路径。[Billings 台阶脚本](billings_far_steps.py)接收精确 Billings 原源和新目标路径。脚本以 `blender -b -t 2 --factory-startup --disable-autoexec --python-exit-code 1 --python SCRIPT -- INPUTS OUTPUT` 运行。重存 Blender 的包装字节可能不同，精确候选使用差量。
- [导出、贴图与逐角核验](fbx_review.py)支持 `--packaged` 检查现有文件，以及 `--export` 写新目录。完整临时目录应保留相对贴图。例：

```sh
blender -b -t 2 --factory-startup --disable-autoexec --python-exit-code 1 \
  --python candidates/20261120-cloud/fbx_review.py -- \
  /path/BillingsHospital_far_steps.blend /path/billings-review.json \
  BillingsHospital BillingsHospital_LOD1 BillingsHospital_LOD2 \
  --export /path/new-package --textures /path/original/ProjectFiles/BillingsHospital \
  --converter /path/original/scripts/convert_blender_fbx_7500.py
```

本轮按同一逐栋口径新增 Billings 和 Levi 两个首检。芝大 33/88、哥大 19/19、宾大 12/12，合计 64/119，剩余 55 个都在芝大。宾大 Quad 另有 34 段已首检。Chicago Lying-In 和宿舍单体本轮复核未加入新增数。CS2 编辑器或游戏 0/153。台账未在本环境完整恢复，后续先把公开索引与可查旧记录对齐，再继续 Campus North 独栋、Cathey Dining 与 Woodlawn 餐厅／住宅组合。Belfield 已做的远档窗和贴图修复保留。
