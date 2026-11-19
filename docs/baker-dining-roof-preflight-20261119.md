# Baker Dining Commons #97｜开展单栋审阅前的屋面证据

本轮只完成资料和只读测量，未修改任何 Blender 几何，亦未给 #97 记首轮完成。云端审阅备份为逐字节同一原版，SHA-256 c4b265b12ac02659fec970085d66ffcc05bbcdef99e696d5de5c6edf3a873cba。三档模型三角面为 3,858 / 650 / 230。只读检查三档均把约 3,003.25 平方米连续顶面放在 Z=5.8m 的同一高度；近中档另有合计24平方米设备面位于 Z=6.8m。设备面不是主绿屋面的标高。

## 分清路径、餐厅和宿舍

[校方启用报道](https://news.uchicago.edu/story/university-chicago-opens-campus-north-residential-commons)及 [Studio Gang 项目](https://studiogang.com/projects/university-of-chicago-campus-north-residential-commons/)确认 2016 已建项目。[建筑师首层实图](https://studiogang.com/wp-content/uploads/2645-gp-1286-university-of-chicago-campus-north-level-1.jpg)可见餐厅入口 14、公共就餐区 15、双私人餐厅 16、餐线 17、后台 18、卸货 19、北零售 22；不能沿内隔墙 16 拟合外幕墙，亦不能把院两侧的宿舍条形和上层院都当作单独餐厅。校方设施 C26 关键词返回 FID267/278/303/307 实为**同一地理几何**（逐字节摘要一致，外接框约79.43×22.25m），字段 BLDG_HGT 均135（不是已测本餐厅标高）。不能把它当作餐厅独立足迹或求并集补出其他形体。

## 现状是缓坡绿屋面，而非水平板

- [Cook County 2025 正射](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer)实际查看场地图（EPSG26916，E450170–450332，N4627060–4627222，900×900，约0.18m/像素）：西侧低层的大草本屋顶由矩形西端沿斜弧向东北延伸。北白屋顶宿舍、向南高条、另一条绿化院落可分开。
- [ISGS 2022 DSM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer)与 [DTM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer)按14个落在西侧连续绿屋面的像元中心取样，单位美国测量英尺换米。DSM−DTM 为6.29–9.00m（另轮独立西侧样点6.10m）；绝对 DSM 在样点内西低东高，差约2.39m。平面拟合的东西项约+4.63%，南北项约−0.24%，观测残差 RMSE 约0.10m；相对裸地拟合的东西约+4.79%。对照街道与广场相对差均约0.01m，东宿舍白屋顶一处约19.78m，不混入样本。
- 此读数证明需要修正三档的**屋盖坡面及对应上缘**，不是简单加高整栋或挪动基座。采的是植被/屋面表面加插值地形，不是结构实测；未获檐口标高、屋面厚度、种植层净高、排水坡折、相邻住区精确搭接或各门幕墙高度。模型 Z=0 不和绝对高程直接相减。下一步在打开该栋原件后按照片与实际边缘配准明确入口轴、幕墙上沿和服务区，分证据修三档，不改未经证明的角点。
