# 芝大最后 26 项专项首检与模型修复

以草稿提交 `d10b8a65033f27c8b609f798abb72f47fecde680` 为起点，在独立 Codex 云环境使用 Blender 4.3.2。以 SHA 锁定重建的源和原包。最后 26 个独立资产通过三档固定站位复核，并实际回导了 78 份 FBX 7500。所有 78 份有向三角面、角点 UV 和材质名称均与当前源一致，相对贴图引用均能解析。其中 Bond–Swift Cloister 和 Lillie House 使用上一批纠正的包。实景对照使用校方、建筑顾问和档案资料，尺寸读数为模型坐标。[逐项检查](individual-review.md) · [测点](evidence/asset-sections.jsonl) · [FBX 回导](evidence/asset-fbx.csv)

三校详细首检累计 **119/119**。芝大 88/88、哥大 19/19、宾大 12/12，另有宾大 Quad 34 段。塔群组合、Harper、Saieh、Ryerson 和 Kent 的重复复核未另计栋数。**CS2 编辑器与游戏仍为 0/153**。开放底面、碰撞、透明、LOD 切换和现场尺度的未决项记录在[最新台账](evidence/asset-register.csv)。

## 具备复验件的修复

| 资产 | 修复与验证 | 仍待验证 |
| --- | --- | --- |
| Tower Group | 对三条接线按已有面覆盖裁切近中档的隐藏共面区。每档 60 个站位原有 44 处跨对象双命中，复验后为 0；单命中 59 处，原有零命中 1 处。五个固定外视图各 192×192 点，轮廓命中一致，首命中深度无超过 2 mm 的变化。Hutchinson 近／中档 28,598／10,938 → 28,522／10,886 三角；Reynolds 12,002／4,850 → 12,051／4,886 三角。两件原已修远档保留。本批四个近中替换件增 8,000 字节。 | Reynolds–Mandel 在原采样位置 Z=2 m 没有命中理论面，近档分别先见约 70 mm 和 350 mm 处的斜面。该处保持原样。相邻实体碰撞、Mitchell 远档 1,597 三角的减重待验。[接线证据](evidence/tower-final-probes.json) · [同镜对比](previews/tower-same-view.jpg) |
| Harper Memorial Library | 按原图集和构件面向，翻正阅读室上方两塔内侧四组窗片。近档 52、中档 20 个面，远档不需改。坐标、材质和 UV 逐角对应保持。近档未改角法线分量最大差 0.000272，中档为 0。五视图的首命中背面像素近档 791→569、中档 1,416→1,143，原覆盖像素数不变；左下檐与斜返回面另留状态。 | 塔楼长窗边框、檐底及内返面需进一步判定应有的可见面向。三档均实导核对。[同镜对比](previews/harper-same-view.jpg) · [固定视图数据](evidence/Harper-visibility.json) |
| Saieh Hall | 按原图集和建模构件方位，翻正高塔东向中部与上段长窗、方塔西北向窗、礼拜堂院侧窗与远档两处院墙窗带。近／中／远各 128／112／24 个面，位置和 UV 保留。五视图的背面像素分别 1,488→1,033、1,494→940、962→74，覆盖与首命中深度保持。三档均实导核对。 | 塔楼下段、门洞内部、部分石饰的剩余背面逐处保留，玻璃游戏材质待验。[同镜对比](previews/saieh-same-view.jpg) · [固定视图数据](evidence/Saieh-visibility.json) |

三个保存后的源都从字典差量逐字节还原。用还原结果重读 18 份成套 FBX。包括 9 份本轮更新、2 份前次 Tower 远档、7 份对照件。各文件均有真实 FBX 7500 字节、角点 UV 差 0、零退化面，贴图从未改动的原包解析。四个补丁包保留原 PBR 文件、设置及其哈希记录。[Tower 成套回导](evidence/TowerGroup-packages-final.json) · [Harper 成套回导](evidence/Harper-packages-final.json) · [Saieh 成套回导](evidence/Saieh-packages-final.json)

## 当前待验问题

- **Ryerson** 的 1910 校刊记录北附楼边长 60 英尺和首层连廊，现有模型中原主体和附楼直接在 Y≈3.27 m 接触一段。附楼中心近／中／远 Z=19.15／19.15／19.00 m，东西越过附楼边界为空。现状连廊平面、竖向与净空仍缺统一的量测，暂保留源形。[1910 校刊](https://campub.lib.uchicago.edu/text/?docId=mvol-0002-0003-0001) · [模型复测](evidence/expansion-sections.json)
- **Kent** 北讲堂中心三档同为 23.834 m，过渡处 15.605／15.605／12.062 m；两侧测点在远档无命中，四处北转角都保持留空。校方确认北讲堂为八角形，档案外景可辨山墙、过渡体和北讲堂，现状轮廓与坡地需要独立测量。[校方建筑说明](https://architecture.uchicago.edu/locations/main_quadrangle/) · [1934 讲堂外景](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-04692.xml) · [模型复测](evidence/expansion-sections.json)
- **Baker** 庭院和采光窗仍欠可靠高程，本轮没有新的高程证据。保留既有待验状态。[NOAA 下载回执](../20261120-continuation/baker-noaa-point-cloud.md) · [已有实景控制点](../../docs/baker-dining-court-and-clerestory-evidence-20261119.md)
- 其余需进场验证的项目包括 International House 远档塔南边缘站位从高檐变为下层屋面、Quadrangle Club 及 International House 的开放底面、Chicago Lying-In 远档南拱代理面。此前与本轮的独立范围见[逐栋表](individual-review.md)。草稿留作审核，未达到合并条件。

## 复现

使用 [20261013 重建指南](../../updates/20261013/README.md)和[技术源恢复说明](../20261118-technical/README.md)得到经校验的源树。Python 需要 `zstandard==0.25.0`。在仓库根目录运行以下两条命令，分别生成新源目录和新导出目录。

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/new-blends --patch-dir candidates/20261120-completion/source-delta
python candidates/20261120-continuation/apply_export_overlay.py /path/to/technical-tree /path/to/new-packs --patch-dir candidates/20261120-completion/export-overlay
```

模型编辑源码在 [Tower 裁切](tower_joint_trim.py) 和[窗片面向](tower_window_winding.py)。Tower 裁切以此前远档修复后的源为输入，脚本通过 `--dependency-dir` 可载入适配 Blender Python 的 `shapely==2.1.2`。哈希锁定的二进制差量直接从完整技术源树恢复三份最终源，复验无需 Shapely。[源 SHA 和差量](source-delta/manifest.json) · [FBX SHA 和差量](export-overlay/manifest.json)

26 个资产的专项复测命令如下。旧台账用来固定本批 26 个名字及源哈希。

```sh
blender -b -t 2 --factory-startup --disable-autoexec --python-exit-code 1 \
  --python candidates/20261120-completion/asset_sections.py -- \
  /path/to/technical-tree candidates/20261120-continuation/evidence/asset-register.csv \
  /path/to/asset-sections.json --landmarks candidates/20261120-completion/landmarks.json
```
