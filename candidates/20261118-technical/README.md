# 完整 101 源场景技术复验与安全修复候选

本轮在云电脑重新从公开八包及两层更新恢复 **8,032 个资产文件**，逐个验证字节/SHA；应用上一轮 11 场景候选后，实际重新打开全部 **101 个 Blender 源场景、136 个登记家族**。不是只检查未修改的 90 份，也不把版本/组合当作不同建筑栋数。

## 已修复并实际包含的模型数据

- 8 个组合场景的 24 个材质名，从意外 `.001` 后缀规范化为对应对象 `_Mtl`。材质节点、贴图、其余几何保持原样。
- Harper 庭院组合的 `GoodspeedHall_LOD1` 有两个相反朝向的重叠极薄三角，FBX 回导会丢掉其中一个。只焊接一对间距 **0.00000095367431640625 米**的近重复点，保留存续角点 UV/法线，去除两处重复闭合角。LOD1 从 11,342 变为 11,340 三角，修后导出/回导均为 11,340。
- `material-patches/` 是**真实二进制差量**，总约 11.6 MB，可精确恢复这 8 个 `.blend` 的全部字节，不是空指针或私人下载链接。避免为更名重新存入超过 143 MB 的 Harper 整场景。
- 其中 2 个场景覆盖上一轮候选，6 个是新增修复；相对 20261013 基线，累计 **17 个源场景有改动，84 个保持原字节**。旧基线和上一轮候选都保留。

## 恢复完整候选源树

需 Python 3.9+；第二步额外使用官方 PyPI `zstandard==0.25.0` 解码 Zstandard 字典差量。所有输出目录必须不存在；预留约 25 GB 空间（基础下载、历史中间版本及两次完整副本都保留）。从仓库根运行：

```sh
python updates/20261013/reconstruct.py --download-base --work ../Campus_Strict_Work
python candidates/20261118-technical/assemble_full_candidate.py --repo . --base ../Campus_Strict_Work/Campus_Strict_20261013 --output ../Campus_Candidate_First
python -m pip install zstandard==0.25.0
python candidates/20261118-technical/apply_technical_patch.py --base ../Campus_Candidate_First --output ../Campus_Candidate_Technical
```

已有通过完整索引校验的 `Campus_Strict_20261013` 可跳过首步。两个后续脚本会在写入新目录前核查输入、全部资产清单、差量和输出 SHA；不会覆盖基线或用户修改过的文件。构建出的完整源树已实际复原验证。原项目许可/第三方署名保持不变。

**重要：完整候选源树里的历史 FBX 不自动变成这些新源模型的导出。** 本轮另外实际独立导出了登记模型的全部 425 个网格作回导测试。需要再生成核查 FBX，可使用下面的复验脚本；它们仍不是已认证的游戏导入资产：

```sh
blender -b -t 2 --disable-autoexec --python candidates/20261118-technical/audit.py -- ../Campus_Candidate_Technical ../Campus_Audit .
blender -b -t 2 --disable-autoexec --python candidates/20261118-technical/export_roundtrip.py -- ../Campus_Candidate_Technical ../Campus_Audit/source_audit.json ../Campus_FBX_Check
```

这里的 Blender FBX 7400 导出只用于可重复几何回导，不是将头改为 7500 冒充 FBX2018。若出现任何异常，请保留日志，不要把失败标成通过。

## 本轮证据

- [汇总](evidence/summary.json)：101 源、136 家族、425 网格、1,473 个文件图片引用。
- [逐家族状态](evidence/family_status.csv) 与 [完整源场景扫描](evidence/source_audit.json)。`__context_scene__` 是登记表中的背景占位，不是缺失建筑。
- 材质名/数量、非有限或越界 UV、退化多边形均未发现剩余异常；1,473 个图片引用为 PNG、内嵌、尺寸在允许的 2 次幂集合。实际扫描 290 个 MaskMap 图片引用的蓝通道，未发现大于 1/255 容差的非零像素。
- [425 个完整独立网格回导结果](evidence/roundtrip.json)：网格数量、三角面数量、UV 层数、世界包围盒及双向顶点距离小于 0.0001 米检查通过。Harper 在修复后整场景重新导出/回导，另外 100 场景字节未再改动，沿用该次结果。
- [保留性复核](evidence/preservation.json)：所有 8 场景的内嵌图片字节不变；除明确修复的 Goodspeed LOD1 外，所有网格顶点/拓扑/UV/变换字节指纹不变。
- [微米级拓扑修复](evidence/goodspeed-topology-fix.json)。之前一次“11342→11341”的失败已定位和修复，没有隐去或将它算作通过。

## 仍不能声称“全部符合游戏规范”

官方参考：[建筑资产管线](https://cs2.paradoxwikis.com/Asset_Pipeline:_Buildings)。本轮是静态与 Blender 回导验证，不替代该页面所要求的 FBX2018 和正式编辑器验收。

- 2 条 Rockefeller LOD1 版本记录仍超过主模型 50% 的建议，27 条 LOD2 家族/版本记录超过 500 三角面建议；这些是建议指标，不是自动判退线。
- 尚未逐像素验证 Normal 为 OpenGL、MaskMap alpha 的实际 glossiness 语义、颜色遮罩互斥、Emissive/ID 配合；尺寸合法不能证明通道语义正确。
- 特殊 shader 的 UV 不重叠、窗口比例/方向、主子 pivot 对齐需要进一步针对性验证。此次 UV 仅检查有限值、0–1 范围与层数。
- 仍未在 CS2 编辑器/游戏核验朝向、尺寸/地块、LOD 切换、材质外观、夜景雪景、碰撞/导航、性能或存档。绝不在用户电脑试运行游戏。
- 建筑真实还原和多视角精致度不由网格扫描代替，不能据此称全部建筑艺术精修完成或直接发布。
