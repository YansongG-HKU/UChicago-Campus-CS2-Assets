# UChicago CS2 独栋源候选复现：逐栋 #81–88

[第 81–83 项审查记录](../../docs/building-by-building-review-81-83-20261119.md)。这里提交的是可以应用的精确顶点改动，不是只有记录，也不打包重复的完整源、原图库、FBX 或游戏资产。现有恢复链、组合场景、Release 和主分支不做替换。

| # | 独栋源键 | 已复现改动 | 已实际回读的原交付候选 FBX（近 / 中 / 远） |
|---|---|---|---|
| 81 | ClassicsBuilding | 近、中档各 40 点，只延伸 20 根石腰线背面。 | 87,317 / 20,669 / 336 |
| 82 | WieboldtHall | 远档 32 点，只将门塔八垛下口接屋面。八处搭接并不代表整底。 | 65,188 / 16,504 / 660 |
| 83 | EckhartHall | 近档 6 点，只修南立面三腰线背棱；中腰线仍避开中央窗洞。 | 77,348 / 19,056 / 413 |
| 84 | RyersonLaboratory | 三档各 24 / 16 / 8 点，两个屋脊风帽只下延底缘 605 mm；36 点复验消除原实测 312–486 mm 缝。 | 92,662 / 20,426 / 480 |
| 85 | KentChemicalLaboratory | 三档各 8 点，北讲堂的通风亭顶饰环底下延 448 mm；原缝约 444 mm，改后样点与瓦面搭接约 4 mm。 | 98,408 / 22,664 / 477 |
| 86 | HaskellHall | 仅 A 案结构：近中扶壁尖帽接石冠、台阶底接模型 Z0；远档原共面避免误报为悬空。36/36/32 个 Z 点，亦可单独共享源纹理。 | 18,140 / 8,616 / 367 |
| 87 | JonesLaboratory | 近中各 72 个背棱点，只延伸三处南墙雕框，144点搭主墙约5mm，远档不变。 | 24,403 / 6,943 / 327 |
| 88 | SearleChemistry | 三档四只风筒（2×2）48/32/24个底环点只下拉42mm。独立48组原40mm→短搭接2mm；不封北格栅的真实空隙。 | 41,818 / 13,330 / 226 |

## 仅在副本中重放

1. 从仓库现有恢复链取一个单体源，不选 Ryerson_Eckhart_Kent 等组合。当前基准为 2026-11-18 完整候选快照中的这八份独立源（脚本内有原件 SHA-256）；脚本拒绝错版、用户已改动源和已存在的输出。无需插件、网络或在用户保存目录内操作。
2. 用 Blender 4.3.2 测试过的命令。将路径换成自己的，输出父目录应已存在、目标文件不得存在：

    blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python candidates/20261119-building-review/apply_to_copy.py -- EckhartHall /path/to/original/EckhartHall.blend /path/to/review/EckhartHall_review.blend

3. 重放输出是新保存的 Blend，不保证全文件字节等于原审查候选；新生成的八份文件已重新打开，逐顶点、面拓扑、材质索引及 UV 和审查候选一致。输入哈希不符、输出已存在的反例均拒绝写入。脚本只重放坐标，不生成或替换 FBX，也不修改运行时元数据；表中的 FBX 是审查候选包里单独回读的数据。

## 阻塞放行的现状差异

- **Ryerson**：[1910 校刊](https://campub.lib.uchicago.edu/text/?docId=mvol-0002-0003-0001)写北附楼设计为 60 英尺见方，通过首层约 15 英尺拱廊连接；[2025 校方遗产地图](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/7/4088/files/2025/10/2025-09-29-Campus-Heritage-Map_Color_op.pdf#page=1)可见主体和北附楼两侧留空、窄颈相连，原独栋模型却直接贴墙。这个窄颈不同于主体东侧的 Eckhart 接口。没有现代可核竖向尺寸与净空，不能直接按历史 15 英尺搬楼或封缝。本轮仅修风帽，未解决主体关系。
- **Kent**：[校方建筑说明](https://architecture.uchicago.edu/locations/main_quadrangle/)称北讲堂八角形；[1934 年讲堂外景](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-04692.xml)与[校方 2025 地图](https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/7/4088/files/2025/10/2025-09-29-Campus-Heritage-Map_Color_op.pdf#page=1)用于区分讲堂、窄颈与南主楼。现代地图的北边和南侧折角不支持直接用规则八边形替代，完整尺寸及坡地未核。顶饰接合不更改北讲堂整体。
- **各栋**：坡地、相邻资产拼接、全套 PBR/昼夜、碰撞、LOD 过渡均无实际 Editor / 游戏验收，不合并为发布版。

## Haskell Hall 单独纹理优化与实景纠偏

[共享内嵌贴图脚本](haskell_share_packed.py)以已交付的 Haskell A 扶壁台阶原候选的 SHA-256 为门槛，仅可用于该文件；坐标重放得到的 Blend 可能有不同容器字节。19 个内嵌图像块变为 10 个数据唯一块，4K像素和色彩空间不变。实际源文件 17,769,925→6,775,336 字节；12对同镜工作台渲染逐像素不变，独立确认坐标、拓扑、法线、材质节点/UV和图像采样语义一致。既有 FBX、外部纹理及发布包不改，不能宣称游戏显存省62%。

[施工方竣工照片](https://www.jonesandcleary.com/university-of-chicago-haskell-hall/)和 [INSPEC 整修记录](https://iibec.org/wp-content/uploads/2025/07/July-07compressed.pdf#page=49)确认两段次屋脊用铜百叶通风棚、红瓦保留。本轮刻意不提交把蓝色图集下缘接到瓦面的 B 案，那个试验不能作现代屋顶。铜百叶下方泛水与端亭是独立细部；现状尺度、游戏验证仍待。

现代 C 候选独立[复现脚本](haskell_modern_copper_geometry.py)只接受已交付、确切 SHA-256 的 Haskell A 贴图共享 Blend。它在新 .blend 中以双次脊铜百叶、斜泛水和外端亭替换蓝玻璃带与局部旧框饰；不继承历史 B。三档新候选是 18,332 / 9,512 / 499 三角；原模型其它保留面坐标/UV与图集字节不变，已独立查询 60 组瓦面交点并回读三个候选 FBX。坐标重建脚本不导出 FBX；脚本输出已打开并与 C 候选逐顶点/面顺序/UV 核对。

    blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python candidates/20261119-building-review/haskell_modern_copper_geometry.py -- /path/to/HaskellHall_A_shared.blend /different/path/HaskellHall_C.blend

[Cook County 2024 正射](https://img.cookcountyil.gov/arcgis/rest/services/CookOrtho2024/ImageServer/info/iteminfo)仍能看出双带和中山墙。C 保留现模型定位，每段14.50米；航片中视觉脊线粗量约19.6–20.3米，分辨率/阴影/投射有误差，不作现地尺寸。没有为修这个屋顶单独拉长楼体，主脊铜饰章、实际氧化色和整体比例留待核对。该候选不替换主分支或发布包。
