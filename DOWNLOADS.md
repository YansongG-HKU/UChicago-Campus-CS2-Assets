# 下载与校验 · 20261013 严格离线复核版

**版本导航：** [20261013 最新版首页](README.md) · [r1 原版下载表](archive_docs/20261007_r1/DOWNLOADS.md) · [r1 原版验证范围](archive_docs/20261007_r1/VERIFICATION.md)。从旧 Release 进入的读者：原附件仍是 7,854 文件的 r1；只有按完整两层更新链恢复后才是 8,032 文件的最新版。

**完整恢复顺序：r1 八个基础资产 ZIP → 第一层全部 13 个 ZIP → 第二层全部 22 个 ZIP。** 后两层各包含入口 ZIP 和全部数据分片，不能漏项。各 ZIP 使用安装脚本读取，不要用二进制拼接，也不要直接覆盖编辑中的模型目录。

推荐下载/克隆整个仓库后使用 [统一恢复入口](updates/20261013/README.md)。仓库的 Code → Download ZIP 已包括两层更新和复核资料，r1 基础八包需另取；统一入口可下载并校验它们。本次没有新建 Release，也没有公开上传最新版八个自包含完整 ZIP。

## 基础资产：现有 r1 Release 八包

以下八个普通 ZIP 合计 **3,357,277,618 字节**，解压后为旧版 7,854 个文件。原 [Release](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1) 的另外两件报告/QA 附件是可选历史资料，不参与最新恢复链。

| 文件 / 直接下载 | 字节 | SHA-256 |
| --- | ---: | --- |
| [Campus_Repaired_20261007_r1_01_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_01_assets.zip) | 439,078,127 | `51e552f73f7e8ad38fbca5ba76db9366599cf47afb81bdf5adffe67ece4a0e8e` |
| [Campus_Repaired_20261007_r1_02_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_02_assets.zip) | 433,404,719 | `514f4a3a5cfe136c464fe7a2f2cc0352a35453fd9e056114da39094ec62c4d19` |
| [Campus_Repaired_20261007_r1_03_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_03_assets.zip) | 432,859,403 | `90dffe1761da853b5b510b2687ed290b8aaae6c0b4f6d008026efa55f2f77c73` |
| [Campus_Repaired_20261007_r1_04_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_04_assets.zip) | 435,461,071 | `be9426c1b9d34c2714d7c27cdfb82f49d94ea4a49e729a14dea8f4981d906be2` |
| [Campus_Repaired_20261007_r1_05_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_05_assets.zip) | 433,582,433 | `1bd82ceaac17038c6e80f4b959825cfe4eeed8a4a8a86da54529d836ef5b1ceb` |
| [Campus_Repaired_20261007_r1_06_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_06_assets.zip) | 427,030,565 | `307140fc91af74bcfb1366e75d7cc75dbcbefd5c7af04b3c69f78f6e1b943450` |
| [Campus_Repaired_20261007_r1_07_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_07_assets.zip) | 425,768,021 | `e8adc4837084761d8b6b2045f9f8241b8032543966e10ab8f7eba1a387693263` |
| [Campus_Repaired_20261007_r1_08_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/download/campus-20261007-r1/Campus_Repaired_20261007_r1_08_assets.zip) | 330,093,279 | `e0ff7a0d92f81d024fde430b78c5f475374c7822e4b9b7d3ab00a1751f00ad85` |

手动解压基础包时，将八包都解压到同一新目录，保留共同的 `Campus_Repair_20261007_r1` 根目录。公共清单内容相同可合并覆盖。这里得到的是更新输入，不是最新版。

## 两层更新：仓库内文件

| 顺序 | 入口 | 必须同时取得的数据包 | 结果与校验 |
| --- | --- | --- | --- |
| 1 | [Campus_LOD_Patch_START_HERE.zip](updates/20261013/layer1_20261012/Campus_LOD_Patch_START_HERE.zip) | `Campus_LOD_Patch_01_of_12.zip` 至 `Campus_LOD_Patch_12_of_12.zip`，共 12 个 | 7,854 → 7,940；[校验和](updates/20261013/layer1_20261012/SHA256SUMS.txt) |
| 2 | [Campus_LOD_Strict_START_HERE.zip](updates/20261013/layer2_20261013/Campus_LOD_Strict_START_HERE.zip) | `Campus_LOD_Strict_Patch_01_of_21.zip` 至 `Campus_LOD_Strict_Patch_21_of_21.zip`，共 21 个 | 7,940 → 8,032；[校验和](updates/20261013/layer2_20261013/SHA256SUMS.txt) |

全部分片的准确文件名、字节与 SHA-256 见 [完整链清单](updates/20261013/chain_manifest.json) 和 [发布文件清单](updates/20261013/PUBLICATION_FILES.json)；[更新总校验和](updates/20261013/SHA256SUMS.txt) 使用相对于更新目录的路径。第一层 13 个 ZIP 合计 **61,501,644 字节**；第二层 22 个 ZIP 合计 **108,660,459 字节**；35 个更新 ZIP 总计 **170,162,103 字节**。第二层公开入口包精简了说明/证据副本，安装器与资产相关输入不变；旧离线校验记录中的入口包大小不是本次公开入口包的大小。请以本目录的新校验清单为准。恢复后的最终资产约 3.51 GB；自动下载基础包建议至少 16 GB 可用空间，复用现有外部基线建议至少 8 GB。

统一恢复入口会按清单校验。若手动核对，在每个校验文件所在目录执行：

```bash
sha256sum -c SHA256SUMS.txt
```

macOS 可使用 `shasum -a 256 -c SHA256SUMS.txt`；Windows PowerShell 可运行 `Get-FileHash 文件名 -Algorithm SHA256`，与清单比较。原根目录 [RELEASE_SHA256SUMS.txt](RELEASE_SHA256SUMS.txt) 只涵盖 r1 的十个旧附件，不涵盖新两层更新。

## 23 份中文 PDF

每个链接均为仓库内相对路径，文件名采用英文、正文保持中文。[全部 PDF 哈希](atlas/20261013/SHA256SUMS.txt) · [原文件名映射](atlas/20261013/original_filename_index.csv)。

| PDF | 内容 / 范围 | 页数 | 字节 |
| --- | --- | ---: | ---: |
| [Campus_LOD_Atlas_01.pdf](atlas/20261013/Campus_LOD_Atlas_01.pdf) | R001–R008 | 8 | 5,380,771 |
| [Campus_LOD_Atlas_02.pdf](atlas/20261013/Campus_LOD_Atlas_02.pdf) | R009–R014 | 6 | 4,624,950 |
| [Campus_LOD_Atlas_03.pdf](atlas/20261013/Campus_LOD_Atlas_03.pdf) | R015–R020 | 6 | 5,357,346 |
| [Campus_LOD_Atlas_04.pdf](atlas/20261013/Campus_LOD_Atlas_04.pdf) | R021–R027 | 7 | 4,685,530 |
| [Campus_LOD_Atlas_05.pdf](atlas/20261013/Campus_LOD_Atlas_05.pdf) | R028–R035 | 8 | 5,110,237 |
| [Campus_LOD_Atlas_06.pdf](atlas/20261013/Campus_LOD_Atlas_06.pdf) | R036–R041 | 6 | 4,855,770 |
| [Campus_LOD_Atlas_07.pdf](atlas/20261013/Campus_LOD_Atlas_07.pdf) | R042–R048 | 7 | 4,585,797 |
| [Campus_LOD_Atlas_08.pdf](atlas/20261013/Campus_LOD_Atlas_08.pdf) | R049–R053 | 5 | 4,643,252 |
| [Campus_LOD_Atlas_09.pdf](atlas/20261013/Campus_LOD_Atlas_09.pdf) | R054–R059 | 6 | 5,397,108 |
| [Campus_LOD_Atlas_10.pdf](atlas/20261013/Campus_LOD_Atlas_10.pdf) | R060–R067 | 8 | 5,258,085 |
| [Campus_LOD_Atlas_11.pdf](atlas/20261013/Campus_LOD_Atlas_11.pdf) | R068–R075 | 8 | 4,779,104 |
| [Campus_LOD_Atlas_12.pdf](atlas/20261013/Campus_LOD_Atlas_12.pdf) | R076–R082 | 7 | 5,093,400 |
| [Campus_LOD_Atlas_13.pdf](atlas/20261013/Campus_LOD_Atlas_13.pdf) | R083–R089 | 7 | 4,860,649 |
| [Campus_LOD_Atlas_14.pdf](atlas/20261013/Campus_LOD_Atlas_14.pdf) | R090–R096 | 7 | 4,890,563 |
| [Campus_LOD_Atlas_15.pdf](atlas/20261013/Campus_LOD_Atlas_15.pdf) | R097–R103 | 7 | 4,921,939 |
| [Campus_LOD_Atlas_16.pdf](atlas/20261013/Campus_LOD_Atlas_16.pdf) | R104–R111 | 8 | 5,442,432 |
| [Campus_LOD_Atlas_17.pdf](atlas/20261013/Campus_LOD_Atlas_17.pdf) | R112–R118 | 7 | 5,030,523 |
| [Campus_LOD_Atlas_18.pdf](atlas/20261013/Campus_LOD_Atlas_18.pdf) | R119–R125 | 7 | 4,791,822 |
| [Campus_LOD_Atlas_19.pdf](atlas/20261013/Campus_LOD_Atlas_19.pdf) | R126–R134 | 9 | 5,242,203 |
| [Campus_LOD_Atlas_20.pdf](atlas/20261013/Campus_LOD_Atlas_20.pdf) | R135–R136 | 2 | 703,983 |
| [Campus_LOD_Complete_Review_Notes.pdf](atlas/20261013/Campus_LOD_Complete_Review_Notes.pdf) | 完整文字说明 | 41 | 253,199 |
| [Campus_LOD_Harper_Courtyard_Appendix.pdf](atlas/20261013/Campus_LOD_Harper_Courtyard_Appendix.pdf) | Harper 庭院组合附录（不新增计数组） | 1 | 725,968 |
| [Campus_LOD_Directory_and_Review_Brief.pdf](atlas/20261013/Campus_LOD_Directory_and_Review_Brief.pdf) | 目录与复核简报 | 6 | 66,882 |

## 审计与最新文件索引

- [136 组审计 CSV](audit/20261013/review_register_136.csv) / [JSON](audit/20261013/review_register_136.json)
- [处置台账](audit/20261013/disposition_ledger_136.json) · [101 个最终源文件哈希](audit/20261013/final_source_sha256_manifest.json)
- [审计文件校验和](audit/20261013/SHA256SUMS.txt) · [QA 摘要](audit/20261013/QA_SUMMARY.md)
- [8,032 个最终资产文件索引](ASSET_FILE_INDEX_20261013.csv) · [93 个资产组索引](ASSET_GROUP_INDEX_20261013.csv)
- [r1 历史下载表与回执](archive_docs/20261007_r1/INDEX.md)

这些是离线源资产，不是已通过 CS2 游戏或 Paradox Mods 验收的安装包。完整证据与边界见 [VERIFICATION.md](VERIFICATION.md)。
