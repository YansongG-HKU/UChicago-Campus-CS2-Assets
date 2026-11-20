# 芝大 Facilities 平面底图：可用于下一步配准

[Facilities Building Footprint（Layer 2）](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2)实际查询获得 32 条校园附近要素，使用服务转投影的 EPSG:26916 平面坐标。下列是明确以校方名和要素号识别的多边形、按轴外包尺寸（约值，单位米）；不是现场测绘、屋面轮廓或楼层净空。校方 [2022 Haskell 3D 缓存](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/2022_08_16_Campus_3D_WSL46/SceneServer/layers/0) 仅核 metadata，未把合并视图、包围盒或标有 BLDG_HGT 的字段当独立的实测依据。

| 对象（FID / 校方编号） | 平面范围 | 可支持的判断 |
|---|---|---|
| Haskell Hall (227 / D39) | 东西18.62，南北55.10 | 以北/南端与中央凸出组一起做平面配准；与2024/25主要可见瓦边粗量约52 m方向一致，原C模型南北整体包络约43.36 m口径不同，不能从外包比直接拉伸，也不应把屋脊高度同比上调。 |
| Goodspeed Hall (254 / D42) | 东西14.17，南北25.22 | 与独栋原记录约25.3 m吻合；其13.3 m是主体进深而非所有凸窗。北到 Gates，南至 Classics；接口和三层屋顶各边仍要独立核查，不能套用 Harper 组合文件。 |
| Ryerson Laboratory (234 / D17) | 东西49.37，南北46.98 | 轮廓中北附楼与主体之间有细颈；用穿颈位置的近轴切片，外廓约2.8 m宽、5.6 m长，2024影像的5–6 m屋顶间隔与此相容。仅水平图形，不是通道内净宽/坡度，也不给其屋面或墙体高度。 |
| Kent Chemical Laboratory (232 / D18) | 东西53.43，南北45.51 | 北讲堂外廓两端不对称，不能直接替代为正八边形。 |
| Stuart Hall (223 / D37) & Stuart-to-Harper walkway (216 / D38) | 单体27.72×54.65；另列桥4.34×6.58 | 桥应单独配准，不把约61 m含连廊的模型整体与单体55 m直接同比，也不以平面范围证明拱下净空。 |

浏览器标准查询参数：layer 2 / query，envelope (-87.6014,41.7878,-87.5984,41.7908)、inSR=4326、outSR=26916、格式 GeoJSON，识别字段 DISCRIPT1/DISCRIPT2。研究结果只保存约值、要素号和来源，不把原校园模型或贴图加入发布资产。
