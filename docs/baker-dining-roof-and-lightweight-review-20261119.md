# Baker Dining Commons #97｜缓坡屋面与轻量交付

首轮完成，修复的是 **餐厅连续主绿屋顶、沿屋面的立面上缘与设备支承**，不是整个 Campus North 的复刻验收。校方与 [Studio Gang 已建项目](https://studiogang.com/projects/university-of-chicago-campus-north-residential-commons/)区分餐厅、住宅与架高院落；证据见[上一轮预检](baker-dining-roof-preflight-20261119.md)。采用[用户工作流](#复现与验收)的先实况、后单栋复核、实出文件重读原则。不改 Campus North Residential 资产。

## 形体和约束

- 从[2025 Cook County 正射](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer)和 Studio Gang 首层图选4个主要参照点，保持模型 XY 不变，EPSG26916 平移至 E450224.501 / N4627134.519，手选点配准 RMS 约0.53m。不是地籍或施工图校准。
- [ISGS 2022 DSM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer)与 [DTM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer)给出主坡面相对地面的近似目标 7.77331 + 0.0478957 X + 0.00125751 Y，东端依据另4个样点收平至8.92m。屋面及上缘同步调整；原门槛、地面坐标和原 Z≤3.70m 的顶点均保留。近/中档两组设备箱顶保持水平、底角嵌入该面25mm；远档不添设备。
- 西北为高度更低的花园，不偷拉成同一片主屋面。保留那里原版5.8m作为暂用基线，靠接界只做简化过渡：目前西北独立测试点与候选最大差约1.32m，尚须拿现状高程和多向实景分开复核花园、采光高窗及相邻宿舍的接缝。未改通行、透明窗或地形碰撞，不把浅层材质绘制当成室内玻璃。

## 复现与验收

- [可重放模型脚本](../scripts/baker_dining_roof_profile.py)锁原版 SHA-256 c4b265b12ac02659fec970085d66ffcc05bbcdef99e696d5de5c6edf3a873cba，运行用 Blender 4.3.2 的 --disable-autoexec 与 --python-exit-code 1；输出仅写新文件。独立重放4网格、10张原内嵌图完全一致。
- 近/中/远 **3,858/650/230 → 4,686/906/382**。仅在坡面分界增加分割，主结构壳每档216三角面，324条边全部正确成对；无重复及零面积三角面。原UV连续插值、无零UV面积，原贴图像素逐字节保留。
- 实际三档主坡面几何对14个样点的误差 RMS 约0.061m，最大偏差0.146m；东端另外4个样点最大差约0.104m；16个设备底角均与坡面相接。
- Blender 真正回读三档 FBX 7500，无缺面/增面，UV差0，最大顶点差约5.14μm，角法线最大约0.81°。这是离线序列化 QA，不代表 Autodesk 认证或游戏可用。
- 导出前将十张原图的 FBX 图像路径正规化为同目录规范名；独立在 Blender FBX 中以相对路径确认6张相关着色贴图（近/中实际共用3个通道，远3个通道），其余图按原资产命名交付。沿用 settings.json 5条近中共享映射。正式导入目录从 **652,844 → 568,039 B（−12.99%）**：PNG 21→10、368,823→151,890 B；新FBX从283,668增至415,796 B。这里的节省只指文件目录磁盘字节，不表示帧率或显存，没用降分辨率交换质量。
- 候选 .blend SHA-256 6635418b57e4c2c099e842b5012c6ccddd1c11632a295ea63892e428efb5daaf；附件 ZIP SHA-256 24fa114f767372957fce703401606df86e0ca03891e45e331a39340bac5deeee。遵循 [Paradox 实际导入路径](https://www.paradoxinteractive.com/zh-CN/games/cities-skylines-ii/news/adding-custom-assets)待验 Editor。只入草稿可重放脚本和记录，模型二进制不写普通 Git。
