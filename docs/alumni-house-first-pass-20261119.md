# Alumni House #96｜首轮核对、扶手试修与重建要求

结论：首轮已查。扶手支承已做局部离线修复，但**原建筑体量不达到现状复刻**，不能把补扶手版发布为真实校园资产。地址以[大学现用目录](https://college.uchicago.edu/advising/college-academic-advising-office)的 5555 S Woodlawn 为准；按当前楼体，不混用早期方案。

## 复核到的重大问题

| 项目 | 模型源 | 实际证据 |
| --- | --- | --- |
| 北向和院口 | +X东／+Y北；C 形朝西，两块坡屋顶按西翼处理 | [校方 Facilities 图层 2 FID84/N12](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2)和 [2025 Cook County 实际场地正射](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer)显示东西长主楼，院口朝南，东翼向南投影约 8m |
| 总体尺度 | 结构基座 23.2×26m | GIS 东西／南北外接约 31.04×21.45m；沿墙线去偏角后 31.05×21.31m，不是轴网测绘 |
| 主楼屋盖 | 旧模型以大坡屋顶和双西翼山墙主导 | 2024/2025 正射中央低平屋面、两端坡面、南向东翼；ISGS 2022 同坐标 DSM−DTM 中部九个点约 10.64–11.51m，中心三点 10.69–10.85m；东带一条横断面中部约 12.66m。不以像元高度推算墙厚、檐口或绝对高程 |
| 正门和投影 | 旧主入口拱门上方未表现正确的南中部叠层凸窗轮廓 | [2023 现状照片](https://commons.wikimedia.org/wiki/File:Alumni_House,_Woodlawn_Avenue_and_56th_Street,_Hyde_Park,_Chicago,_IL_(54826292221).jpg)可辨南侧中央拱门上为两层凸窗、石托和开孔女儿墙；东翼近院一侧为山墙和回廊，另有西端凸 bay |

不整栋盲旋或缩放。下一次锁定局部坐标（EPSG:26916中心 E450475.3714，N4627021.0034，局部东轴−1.018°），先按现状改平面、分区屋面、东翼及门廊，再重新证明其接地与三档外观。东/北侧细部未锁定，照片里实际扶手的斜段与整个入口动线需与未来台阶一起重建。中档有多组窗件和线脚局部支承待处理，旧参考扫描的屋顶垂向射线会错过已经穿入屋体的烟囱，不当作浮空定论。

## 已做的局部候选

在锁定的 AlumniHouse.blend SHA-256 189399d49ffab0be5de07b0f8ae3b4e1dd8ce422d19a5cc60eb4fdf1be70fa50 上运行 [扶手脚本](../scripts/alumni_house_rail_support.py)，用 Blender 4.3.2 为两侧扶手和14根立柱调整128个顶点，插入台阶10mm，外端移入最末级。源位置在台阶外，外端还超过台阶前沿；独立复验154个脚底探针和14个扶手连接，均接合。未改变三角拓扑、UV、材质、中/远档或10个 packed 贴图。重放独立验算一致。

实际导出7500三档 29,811 / 8,375 / 178 三角面；Blender 回读三档面集合缺增均0、UV差0、最大顶点差约3.02微米。此为局部离线保留件，不是正式建筑候选。无游戏实测，无建筑安全或通行合格结论；二进制不推普通 Git，草稿不合并。
