# 芝大建筑逐栋检查与导出候选 · 2026-11-20

## 检查范围

本轮从草稿 PR #2 的 `2355225e000b3d0887f50377f73007fd525b7cd5` 开始，使用独立 Codex 云环境的 Blender 4.3.2。源树来自八个公开 r1 基础包、两层 20261013 更新和已记录的草稿模型补丁。每个首选源的 SHA-256 由既有源审计校验。原交付 FBX 与原场景分开保留。

- [88 个独立资产逐项台账](evidence/asset-register.csv)和[285 份原交付 FBX 回导结果](evidence/fbx-readback.csv)记录各自路径、SHA、尺寸偏差、三角面、角点 UV、材质名和贴图引用。所有 285 份 FBX 都在清空后的 Blender 场景成功读取，版本均为 7500。零未解析相对贴图引用、零退化三角面、零材质名差异。有向几何和角点 UV 都与当前源一致的 278 份，包围盒最大差约 0.000011 m。其余七份存在源与包的版本差。
- 每个资产的近、中、远档都生成了两个固定方位及俯视的源网格图，共 [8 张联系表](previews/)和[逐档视图统计](evidence/visual-screen.json)。橙色表示射线先命中背面，蓝色是另存的玻璃或水网格。该方法能发现轮廓、开放面和 LOD 间突变，运行时着色和切档需进游戏测试。Beecher、Kelly、Green 以及 Woodlawn Dining 的高比例背面命中与已记载的共墙／开口相符。Harper 和 Saieh 仍需定位可见背面。
- 三校逐栋首检口径累计 93/119。芝大 62/88、哥大 19/19、宾大 12/12。宾大 Quad 另有 34 段已首检。John Crerar Library 为原 #75 的复验。核对前几批记录发现 D’Angelo Law Library 与 Smart Museum 各重复计入一次。本轮新增 23 个带专项测量的首检。其余 26 项已有本轮静态筛查与历史人工记录，单独的定点复核待做。CS2 编辑器及游戏验收为 0/153。
- 88 个首选源均已对上 20261013 人工台账的具体条目。82 个源文件 SHA 相同。另六个恢复两版，按同一 XY 网格复查，三档包围盒和 41×41 点投影／底部覆盖计数均一致。也统计了两端位于 Z=0 ± 2 mm 的边，补充只测最小单点高度的不足。[20261013 人工台账](../../audit/20261013/review_register_136.csv) · [本轮地面与屋顶网格](evidence/footprint-review.json) · [六个旧源对照](evidence/historical-footprint-review.json)

## 模型与测点

| 资产 | 本轮结果 | 后续 |
| --- | --- | --- |
| Henry Hinds Laboratory | 近／中档门前浑仪底座在采样位置与浑仪有 19.0–30.5 mm 空隙。上移底座顶面四角 35 mm 后，实测搭接 4.5–16.0 mm。浑仪与远档保留。五份 FBX 7500 独立回读，角点 UV 差 0。 | [同镜对比](previews/hinds-armillary-before-after.jpg) · [复验记录](evidence/HenryHindsLaboratory-repaired-fbx.json) |
| William Eckhardt Research Center | 六个采样排气罩与下方竖井约有 41.6 mm 搭接。近／中／远主体 41,936／15,070／370 面，另两个玻璃各 4,130 面，五份原交付 FBX 有向几何和角点 UV 一致。 | 游戏玻璃和实景尺度待验。[测点](evidence/WilliamEckhardtResearchCenter-probes.json) |
| John Crerar Library | 三档天窗采样 Z 为 18.9／18.2 m，五份原交付 FBX 有向几何和角点 UV 一致。 | 早期门把手候选字节未取得。[测点](evidence/JohnCrerarLibrary-probes.json) |
| Women’s Quadrangle | Foster、Kelly、Green、Beecher 三档最低点都为 Z=0。Foster–Kelly 每档 20 个测点均由单侧墙面覆盖。另两条接口为原设计的开放端，无重复共面墙。四个单位的 12 份原 FBX 均回读。 | 共墙放置与碰撞待游戏验证。[组合测点](evidence/WomensQuadrangle-probes.json) |
| Tower Group | Mitchell、Hutchinson、Reynolds、Mandel 三档共用 Z=0 支点。只裁去 Hutchinson、Reynolds 远档位于对侧墙包络内的面，三个接点共 60 个测点由双墙变为单墙。远档分别由 330／631 变为 332／636 面。12 份实际组合 FBX（两份替换、十份原档）对差量恢复源重导，通过有向面、角点 UV 和相对贴图检查。 | 近、中每档各 44 个双墙样点仍待裁定；各有一处未命中的测试位置。Mitchell 的当前远档为 1,597 面，保形减重待验。[同镜对比](previews/tower-far-before-after.jpg) · [复验记录](evidence/TowerGroup-repaired-fbx.json) |
| Hull Court 四栋 | Anatomy、Culver、Erman、Zoology 的各三档，独栋与组合包围盒及三角面数一致。全部 60 个室内轴线底部样点落在 Z=0。两条可选廊体与两端模型名义墙线有采样间距与搭接，端点实景尺寸留空。 | Cobb Gate 在组合内是空对象的待定标记。廊体为可选场景几何，屋顶设备和真实接口待实测。[测点](evidence/HullCourt-probes.json) |
| Woodlawn 住宅与餐厅 | 基座四段三档各 25 次竖向测量，共 300 点。第 2 段只有理论分割线上的 1 点／档双空，±15 和 ±50 mm 有实体承接。餐厅负责的屋顶花园跨越两侧 Z=4.200 m 的基座。36 个组合测点原有 5 mm 缝，花园底面下移 8 mm 产生 3 mm 搭接，顶面维持 Z=4.235 m。单体的 18 个点也已复测。三份独栋新导出 4,470／1,638／66 面、加 640 字节，用旧相对贴图和设置；六份组合检查件独立回读。 | 单体屋顶花园外沿仍需配套住宅基座。实际地形、北到达庭院及游戏切档待验。[同镜对比](previews/woodlawn-lawn-before-after.jpg) · [单体回读](evidence/final-overlay-WoodlawnDining.json) · [组合测点](evidence/WoodlawnAssembly-lawn-contact.json) |
| Max Palevsky 东、中、西三栋 | 东、西院落中心三档均无屋顶或地板命中，指定翼位底部同为 Z=0。中央栋长条和南侧突出体各有三档实体，两个北楼梯塔均为 15.8 m，入口间的后退位置为空。12 个站位的近／中／远读数逐点一致。九份原交付 FBX 回读通过。 | 校方平面和照片支持相对体量。精确间距、地形和地下连接待验。[逐站测量](evidence/footprint-review.json) |
| Ratner Athletics Center | 定位到原建模 Z=0 墙脚因整体居中抬到 Z=41.49 mm，三档的绝对最低点来自其他构件。只将该层的 328／201／56 个点移回 Z=0。31,806／2,742／392 面保持，三份新 FBX 7500 重导的角点 UV 差 0，原贴图仍逐字节复用。三份合计增加 112 字节。 | 游戏地貌与碰撞待验。[同镜对比](previews/ratner-ground-before-after.jpg) · [模型测量](evidence/RatnerAthletics-ground-contact.json) · [新 FBX 回读](evidence/final-overlay-RatnerAthletics.json) |
| Cobb Gate | 三档拱道水平射线结果一致。Z=1、2、3.9 m 时, X=−2、−1、0、1、2 m 的样点通过全门深。Z=4.75 m 的三处通过，5.2 m 只中线通过，5.5 m 无采样通行。 | 与 Hull Court 两翼的实景定位仍待测。[门洞网格](evidence/footprint-review.json) · [芝大建筑页](https://architecture.uchicago.edu/locations/cobb_gate/) |
| Burton–Judson Courts | 远档地面内部无底面命中，周边及其他坐落边在 Z=0，远档约 873.7 m 边的两端落在该标高容差内。对照公开版和新源，远档 41×41 覆盖计数均为 873，仍保留两个院落和远档开放底面。 | 地形贴合、远档底视及碰撞待验。[新旧测量](evidence/historical-footprint-review.json) · [20261013 条目 R021](../../audit/20261013/review_register_136.csv) |
| Blaine Hall | 三档墙脚在 Z=0 均有成段接地边。近／中／远的屋顶和底部投影覆盖计数为 812／808／695。远档比近档少 117 个网格点，最大高度 27.75 → 26.50 m。原轮廓审阅记录对应同一源 SHA。 | 对应高低屋体的远档取舍需依正式视距审查，组合两端为条件接口。[网格](evidence/footprint-review.json) · [Blaine 校方照片](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-00859.xml) |

实景资料用于核对建筑特征。测点为当前模型坐标。[芝大 Hinds](https://architecture.uchicago.edu/locations/henry_hinds_laboratory_for_geophysical_sciences/) · [Payette Crerar](https://www.payette.com/project/crerar/) · [HOK Eckhardt](https://www.hok.com/projects/view/university-of-chicago-william-eckhardt-research-center/) · [芝大 Women’s Quadrangle 档案](https://www.lib.uchicago.edu/collex/exhibits/building-long-future/creating-womens-residence-halls/) · [芝大 Tower Group](https://architecture.uchicago.edu/locations/tower_group_mitchell_tower_hutchinson_commons_reynolds_club_mandel_hall/)

[Hull Court 照片档案](https://photoarchive.lib.uchicago.edu/db.xqy?show=browse2.xml%7C115) · [Botany Pond 修复资料](https://news.uchicago.edu/story/beloved-botany-pond-getting-sustainable-upgrades) · [Woodlawn 竣工项目](https://www.elkus-manfredi.com/project/university-of-chicago-woodlawn-residential-and-dining-commons/) · [芝大 Max Palevsky 建筑资料](https://architecture.uchicago.edu/locations/max_palevsky_residential_commons/) · [芝大 Ratner 建筑资料](https://architecture.uchicago.edu/locations/gerald_ratner_athletics_center/)

## 原交付 FBX 修正

本轮把六份过期导出换为当前签名源的 FBX 7500。包中所有原贴图、命名的着色器贴图与设置文件继续使用原字节。使用哈希锁定的独立副本回导五个包的 15 份 FBX，均通过有向三角面、角点 UV 和贴图路径核验。第七份为 Booth Harper Center 的远档，已由[前一批候选](../20261120-export-review/README.md)修正。

| 替换项 | 原包 → 当前源三角面 | 原包 → 新 FBX 字节 |
| --- | ---: | ---: |
| Bond–Swift Cloister LOD2 | 1,388 → 1,318 | 72,492 → 73,180 |
| Burton–Judson Courts LOD2 | 1,778 → 1,742 | 86,140 → 85,372 |
| Lillie House LOD2 | 1,433 → 1,418 | 73,260 → 72,892 |
| Rockefeller Chapel LOD1 | 47,418 → 46,469 | 2,650,668 → 2,640,268 |
| Saieh Hall 主档 | 59,596 → 59,577 | 3,039,580 → 3,039,308 |
| Saieh Hall LOD1 | 22,273 → 22,269 | 1,021,692 → 1,022,188 |

六份过期导出合计减少 10,624 字节。Tower 两份新远档合计增加 1,248 字节，来自裁切处三角化。游戏内性能待实测。

## 复现

用 [20261013 恢复链](../../updates/20261013/README.md)及[既有草稿技术树补丁](../20261118-technical/README.md)准备源目录。需要 Python 3.9 或以上、`zstandard==0.25.0`。以下命令在仓库根目录运行并写入互相独立的新位置。

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/hinds-review --patch-dir candidates/20261120-continuation/hinds-delta
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/tower-review --patch-dir candidates/20261120-continuation/tower-delta
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/woodlawn-review --patch-dir candidates/20261120-continuation/woodlawn-delta
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/ratner-review --patch-dir candidates/20261120-continuation/ratner-delta
python candidates/20261120-continuation/apply_export_overlay.py /path/to/technical-tree /path/to/export-review
```

前四条还原五份真实 Blender 源。第五条在原包副本中替换十四份 FBX，并验证原包的已有文件及替换件的 SHA-256。[Hinds 源差量](hinds-delta/manifest.json) · [Tower 源差量](tower-delta/manifest.json) · [Woodlawn 源差量](woodlawn-delta/manifest.json) · [Ratner 源差量](ratner-delta/manifest.json) · [FBX 差量](export-overlay/manifest.json) · [完整静态检查入口](inventory_readback.py)

## 合并状态

草稿保持待审。Baker Dining 庭院和采光窗缺实测高程。[Baker 已测范围](../20261120-cloud/README.md)含单体及组合记录。[NOAA 备选点云试取回执](baker-noaa-point-cloud.md)记录下载被拒绝及后续测点边界。[Ryerson 北附楼与 Kent 北讲堂](../20261119-building-review/README.md)仍有实景形态差异。Tower 近／中档接线、Harper 和 Saieh 的可见背面以及尚欠本轮定点检查的 26 项记录在台账中。优先查 Tower 近／中接点、Blaine 的远档覆盖、Cobb Gate 与 Hull Court 的配准，以及 International House 和 Quadrangle Club 的开放底面与地形。当前云环境可运行 Blender，未提供可用的 CS2 编辑器与游戏运行环境。
