# 第95项 · Bartlett Hall 独栋候选

**修复近、中景两侧入口共16条悬浮石线脚，并补齐三档屋脊的连续天窗外观。** 保留原版窗门、墙身、塔楼、南门罩、屋面与贴图，不是开孔透光的室内模型。第94项组合接缝另排，不计进本栋。

## 实景依据

- 1904 年 [Shepley, Rutan & Coolidge 原设计说明](https://campub.lib.uchicago.edu/pdf/?docId=mvol-0007-0008-0010)给历史主体 200×80英尺（60.96×24.384m），东西入口凸出另列。此处不拿历史主体尺寸代替当前全体外沿。校方 [Facilities C04/FID63](https://services.arcgis.com/ppFhFO7kjyIF441C/ArcGIS/rest/services/Archibus_Web_Map_WFL1/FeatureServer/2)回读平面包络约37.73×73.42m，包含出挑和服务体量；当前模型近档包络约31.93×64.71m，两个定义和覆盖未配准，不能直接对整栋缩放。
- [改建设计单位 Bruner/Cott](https://brunercott.com/projects/bartlett-commons/)记 2002 前后餐饮改造有通长节能天窗，校方[完工报道](https://chronicle.uchicago.edu/020110/bartlett.shtml)也证实继续利用屋顶采光。1982 年 [南侧历史原图](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-00585.xml)可见中间已有条状构造；不说此前全无天窗。1982 [西侧原图](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-00588.xml)支持入口石线脚与塔楼定位，不证明毫米尺寸或今日门槛。
- [2024](https://img.cookcountyil.gov/arcgis/rest/services/CookOrtho2024/ImageServer/info/iteminfo)与[2025](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer/info/iteminfo)正射实际回读同一范围 EPSG26916 E450208.509–450352.362、N4626795.408–4626939.262，840×840，约0.1713m/输出像素。两年均看到中央带密集浅色分隔的深色条带，长约59.5–60.5m、宽约2.9–3.3m。沿中线像素亮度节奏约0.61m，仅供重复密度参考，不称实测分格数。模型取60.25×3.15m，96分段近、48分段中、远景保留双坡条带及边框。原宽幅红瓦面、浅色檐边和东凸出交界仍需细化，不因天窗补全就报现状准确。

## 这次实际改了什么

- 近、中景各8条（每侧四层），后缘离原入口外墙约207mm。只把48／48／0个后缘点向内延伸209mm，形成约2mm搭接；不向内平移原正面。新接触限制于同一入口墙、局部端头返边和相邻石构件，未改门窗开口。原顶檐与南罩本就贴住支承，不误作悬浮。
- 天窗只增加一层贴着屋面的有框低模型。原瓦面留作背衬，沿原屋脊、两边随坡。外观用原有不透明蓝灰和浅色材质图区域，纹理文件、关联及近中共享配置未改；没有新材质依赖，没有开洞或室内透光模拟。新面3,100／1,564／24；远景为498三角，但不把500作为通用上线标准。
- 32件立面圆饰已单列：后缘约98mm悬空，但历史图不支持现有重复排布风格，尚未证实现状。不强行贴墙后冒充真实花饰，留原件待高清当代立面定去留。实测外沿、北尾部/服务区及东部入口接地未放行。

独立复验：192 个入口接触探点均约2mm，429个屋面采样点全部命中实搭；新天窗顶高出原瓦面约37–206mm，底部嵌入约132–950mm（远景上限790mm），全长度无采样漏缝。所有新增边均闭合；未动区域角法线、原面UV/材质和10份内嵌图一致。

三档 FBX 重新导入 Blender 为 **59,954／19,410／498**，缺增0、UV差0，最大坐标差约6.9μm；保持已验屋脊与正面细节。另一次重放与候选网格、UV及内嵌贴图记录一致。FBX 7500结构不等同 Autodesk FBX2018认证或 CS2 游戏内验收。

[复现脚本](../candidates/20261119-building-review/bartlett_portal_skylight.py)只接受锁定原版 SHA，不覆盖现文件；脚本的云端重放已实际比对。FBX、Blend 及贴图随候选包另交付，不在本提交内。
