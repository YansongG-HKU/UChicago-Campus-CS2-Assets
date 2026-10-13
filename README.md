# 芝加哥大学校园建筑资产 · 20261013 严格离线复核版

最新版包含 **93 个技术资产组、101 个 Blender 源文件、484 个 FBX、8,032 个资产文件**。本项目是校园建筑与组合场景的近似重建，用于后续编辑和导入准备，不是测绘资料，也不代表芝加哥大学官方作品或认可。

## 从这里开始

**完整最新版 = 原 r1 的八个资产 ZIP + 第一层更新 + 第二层严格更新。** 顺序为 **7,854 → 7,940 → 8,032** 个文件。只下载第二层不能从 r1 直接恢复最新版。

1. 下载本仓库的 **Code → Download ZIP** 并解压，或克隆仓库。仓库内提供两层更新、23 份复核 PDF 和审计资料，**不包含 r1 的八个完整基础资产 ZIP**。
2. 安装 Python 3.9 或更高版本后，在仓库根目录打开终端，运行以下入口。它下载并校验原 r1 基础包，再按顺序应用两层更新；工作目录必须是一个新目录。

```bash
python updates/20261013/reconstruct.py --download-base --work ../Campus_Strict_Work
```

已有完整解压、未自行改动的 r1 资产时，可改用：

```bash
python updates/20261013/reconstruct.py --base ../Campus_Repair_20261007_r1 --work ../Campus_Strict_Work
```

入口仅使用 Python 标准库，不需要 Blender 或游戏。成功后，最终资产位于 `../Campus_Strict_Work/Campus_Strict_20261013`；中间 7,940 文件版本会保留在同一工作目录。自动下载基础包建议至少留出 **16 GB** 空间；使用现有外部 r1 基线建议至少 **8 GB**。

macOS/Linux 如需可将 `python` 改成 `python3`，Windows 可用 `py -3`。参数、输出位置、校验和及分层手动步骤见 [完整恢复指南](updates/20261013/README.md)；[下载与校验表](DOWNLOADS.md) 提供基础包、更新和全部 PDF 入口。使用新输出目录并保留目录结构，不要把更新包直接覆盖到自己的编辑副本上。

**本次更新放在仓库主分支，未新建 GitHub Release。** [现有 Release `campus-20261007-r1`](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1) 继续提供原始八包；单独下载这八包只会得到旧版。最新版的八个自包含完整 ZIP 尚未公开上传。按上述完整链恢复的结果是等价的最终资产集合，资产数据合计 **3,505,395,608 字节**。

## 先看效果与结论

- [图册总目录：20 册，R001–R136](atlas/20261013/README.md)
- [目录与复核简报](atlas/20261013/Campus_LOD_Directory_and_Review_Brief.pdf)
- [完整文字说明](atlas/20261013/Campus_LOD_Complete_Review_Notes.pdf)
- [Harper 庭院组合附录](atlas/20261013/Campus_LOD_Harper_Courtyard_Appendix.pdf)
- [136 组逐项审计表](audit/20261013/review_register_136.csv) · [当前处置与历史问题](audit/20261013/disposition_ledger_136.csv) · [验证范围](VERIFICATION.md)

共 **23 份 PDF**，内容保留原中文，英文文件名不表示已经翻译。20 册图册恰好覆盖 136 个审阅条目，Harper 附录不新增计数组。

本轮修复涉及 23 个建筑名称、36 个模型家族出现项、31 个源文件和 54 个命名网格。36 个修复项已对最终源文件的原材质四角视图重新人工复核；其余 100 项按来源一致或未改动网格证据继承原人工记录。**不声称 136 项全部重新渲染或本轮逐项重新人工看图。** 本轮实际导回检查了 76 个唯一最终 FBX，不能理解为对全部 484 个 FBX 重新导入验收。

93 个技术资产组是文件组织口径；136 个审阅条目是源文件/模型家族口径（133 个完整 Main/LOD1/LOD2 家族、2 个 Main-only 组、1 个背景场景），均不等于不同建筑栋数。

## 按资产查找

- [最新版资产组索引](ASSET_GROUP_INDEX_20261013.csv)：93 组、各组文件数和原 r1 基础包位置
- [最新版完整文件索引](ASSET_FILE_INDEX_20261013.csv)：8,032 个最终路径、大小、SHA-256 与最后内容更新层
- [机器可读版本摘要](LATEST_VERSION.json) · [更新记录](RELEASE_NOTES.md)

`r1_base_package` 只是追溯基础文件位置；最新版恢复仍需完整八包和两层更新。`last_content_stage` 表示最终字节最后来自哪一阶段，不能作为跳过前置层的依据。

`Rockefeller_Chapel_v0.1` 为优先版本；`RockefellerChapel_v02` 保留为独立备选。`BlakeCobbMapProxy` 为敏感性研究用代理场景。

## 明确边界

- 尚未进行 Cities: Skylines II 编辑器或游戏运行测试，游戏内 LOD 切换、碰撞/导航、内存与性能均未验收。
- `_Gls` / `_Wat` 的玻璃、水材质自动分派及游戏内外观未测试。保留原材质语义，不用重新着色掩盖几何问题。
- 不保证测绘精度、全局水密、室内完整度或所有视角无缺陷。作者定义的共墙接口、地面接触底部开口及部分细部简化按审计记录保留。
- Saieh 原有极细三角面的未定义角点法线例外仍存在并已列明。
- **Paradox Mods 已发布条目：0。** 这不是可直接安装的 `.cok` 或已完成 prefab 成品。

## 历史与权利

原 r1 Release、标签和附件保持原样。原固定路径 [ASSET_FILE_INDEX.csv](ASSET_FILE_INDEX.csv) 和 [ASSET_GROUP_INDEX.csv](ASSET_GROUP_INDEX.csv) 继续保留 r1 数据；最新版索引使用带 `_20261013` 的文件名。[r1 历史说明、索引及回执](archive_docs/20261007_r1/INDEX.md) 单独保留；根目录 `PUBLICATION_STATUS.json`、`PUBLICATION_VERIFICATION.json`、`FINAL_PUBLICATION_VERIFICATION.json` 及 `RELEASE_SHA256SUMS.txt` 仍仅描述 r1，不能当作最新版远端发布证明。

不新增或替换项目许可证；公开下载不会自动授予额外使用、再分发或商业许可。保留原文件中的第三方权利与来源说明，见 [保留的许可与署名](audit/20261013/licenses/README.md)，包括涉及 16 个技术组的 OpenStreetMap 署名和原 DejaVu 字体许可。项目不声称与芝加哥大学或游戏发行方存在官方隶属或背书关系。
