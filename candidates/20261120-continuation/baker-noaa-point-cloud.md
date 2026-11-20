# Baker Dining · NOAA 2017 点云试取

在 ISGS 2022 DSM／DTM 服务拒绝新的取样请求后，另查了 NOAA 对外提供的 2017 USGS Cook County 分类点云。该发布为 NAD83(NSRS2007) / UTM 16N（EPSG:3723），垂直坐标为 NAVD88／GEOID18 米。项目名义间距为 0.35 m，采集在 2016 年完工后，单个庭院或采光窗的回波覆盖要用实际数据检验。[NOAA 数据目录](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9050/index.html)

云端尝试下载目录所列的两个分幅索引。XYZ 边界 CSV 返回 HTTP 403。GeoPackage 的 CONNECT 隧道返回 HTTP 403，文件传输为 0 字节。仅访问目录可读页面。网页工具对 CSV 还返回 HTTP 400／不支持 `text/csv`。因此此环境没有下载任何 LAZ、没有获取本地密度或分类测量，也没有产生新的模型或高程验收。[XYZ 边界 CSV](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9050/minmax_il2017_cook_kane_lake_mchenry_m9050.csv) · [GeoPackage 分幅](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9050/tileindex_il2017_cook_kane_lake_mchenry_m9050.gpkg)

核对范围为 EPSG:26916 的 E450170–450332、N4627060–4627222。待有实际分幅后，将该范围投影到文件所用 CRS，只读取相交的块，并记录文件 CRS、垂直基准、分类、密度和原始标高。以三个铺装控制点和绿屋面独立对照复核，再与模型相对地面高程比较。已记录的三处铺装点仍为旧 DSM／DTM 观测与 Blender 候选之间的 0.79–1.13 m 偏差。玻璃窗头、窗台及共墙细部待有可辨识回波或构造资料。[已有测点与坐标](../../docs/baker-dining-court-and-clerestory-evidence-20261119.md)

围护顾问项目页确认其参与幕墙、屋顶和接缝性能测试。公开页面未给出所缺节点标高。[ZS 项目页](https://zsllc-us.com/project/campus-north-residence-hall-and-dining-commons/)
