# 第92项 · Gates–Blake 合体资产中的北翼 Blake Hall

**北翼已修：26 个悬浮构件实例；屋顶保留真实存在的烟囱，并把三档移到同一近年影像位置。范围限 Blake，中央 Gates、跨楼腰线和 Cobb 接缝未验，不将整个合体加入完成计数。**

| 部位 | 原模型 | 北翼候选 |
|---|---|---|
| 两侧上部腰线 | 近、中各2条，距墙20 mm | 后缘向里22 mm；只改北翼专属高处腰线 |
| 低窗外饰 | 近档19条，后缘距墙45 mm | 后缘向里47 mm，外轮廓不挪 |
| 东入口三个圆饰 | 近档距墙67.5 mm | 整个向里69.5 mm，形状不变，不改入口洞口 |
| Blake 屋顶烟囱 | 近、中位于屋脊 X≈−0.013m、Y≈+9.20m，远档 Y=+16m | 统一中心 X=−1.30m、Y=+17.10m，西坡比原位置低，随坡下降约1.065m。形态及顶高仍非实测 |

4 条低/中位长腰线在合体中跨越 Gates 和 Blake（Y−28.6 到 +28.6），因此近/中这两档都不整条推移。固定保留另两处 Gates 烟囱、中央东凸窗以及全部原版贴图。Gates / Blake 交界待两翼分开复核后整体过渡；更北 Cobb 总装已有定位研究，不复用代理去补未测通道。

## 取证

- [芝大 Facilities 图层2](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2)：Blake FID132，Gates FID221。Blake 平面外包约13.73×26.25 m。两者南北外包范围重叠约0.73 m，不是墙厚或需要切掉的重合量。
- [Art Institute of Chicago：Henry Ives Cobb 档案](https://aic-web-cms-uploads.s3.us-east-2.amazonaws.com/8543fb1d-70df-4a94-8f76-cc61e9985e61/HenryIvesCobb_RyersonandBurnhamLibraries_TheArtInstituteofChicago.pdf#page=36)明确历史三楼组是中央五层 Gates，北 Blake、南 Goodspeed 四层镜像；**镜像不是现代屋顶设备、地坪和入口的复制依据**。[1969年 Blake 东立面原照](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-02081.xml)实际可辨横向三枚圆纹样，现模型的分离素线条不是雕刻实测；只修浮空，不用该照宣称入口现状合规。[校方纪念图](https://125.uchicago.edu/then-and-now/classics-quadrangle/)实际查看较晚庭院图，仅用作组团朝向，镜头没有把 Blake 门槛或 Cobb 接缝拍全，不从照片推标高。
- 县 [2024](https://img.cookcountyil.gov/arcgis/rest/services/CookOrtho2024/ImageServer/info/iteminfo) 和 [2025](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer/info/iteminfo) 同窗正射实际读图：EPSG26916，E450036–450100/N4626436–4626500，640×640，约0.10m/输出像素。未旋转图（左上为像素原点）Blake 始于图上方 Cobb 邻接以下，五组小山墙中第三组附近烟囱帽在 x≈270–274、y≈152–161，主脊 x≈284–287。两年日影不同但浅色烟囱位置相符。先以五组山墙的相对位置校核，再取模型中心 X−1.30/Y+17.10；方位与尺寸是近似，变化可从透视位移、像素判读、真实屋面与模型坡度差产生。影像未量烟囱高、墙口净空，不把估计当实测。

## 云端验收与复现

- 476 个独立探点确认装饰在原外墙后约 2 mm 接合。新烟囱下 495 个采样全命中屋面，模型筒脚在测试点嵌入约 0.111–0.690 m；原来的三个档位位置另查 495 点，原坡面连续、没有采样漏孔。既有窗框、端帽处有同一立面构件接口接触，没有改入口玻璃或堵门洞；这不等同游戏碰撞。
- 原/新共对比 287／25／8 个改点均属于北翼；三档有向拓扑、全 UV、材质索引和 10 张内嵌图一致，未受影响角法线一致；另一次独立重放比较 4 个网格逐点相同。原档 32／32／4 个零标高三角保留，没有改基础。
- 重新导出并回读整个合体的三档 FBX：57,755／25,601／461 三角，全部匹配、无缺增，最大坐标差约5.4微米、UV 差0。几何退化/重复、零面积或越界 UV 为0；FBX 7500 结构不等于 Autodesk FBX 2018 或 CS2 编辑器验收，游戏内未验。

[可重现脚本](../candidates/20261119-building-review/blake_north_geometry.py)仅接受锁定原版 SHA 的两楼合体源文件，拒绝覆盖。未将 Blend/FBX 二进制放入此提交。