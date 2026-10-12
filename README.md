# 芝加哥大学校园建筑资产（离线源文件修复版）

本项目整理已完成的芝加哥大学校园建筑与组合场景近似重建资产，版本 **20261007_r1**。模型用于后续编辑与导入准备，不是测绘级建筑资料，也不代表芝加哥大学官方作品或认可。

## 下载完整资产

仓库：[YansongG-HKU/UChicago-Campus-CS2-Assets](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets)。资产下载入口为 [Release `campus-20261007-r1`](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1)；[逐附件下载表](DOWNLOADS.md) 列出全部 **10 个附件**的直接链接、准确字节大小及 SHA-256。

仓库的 **Code → Download ZIP** 仅包含说明、索引及归档报告，**不包含完整模型**。完整交付包含：

- `Campus_Repaired_20261007_r1_01_assets.zip` 至 `Campus_Repaired_20261007_r1_08_assets.zip`：全部模型、纹理、预览、脚本及相关资料，共 3,357,277,618 字节。
- `Campus_Repair_Retest_20261007_r1_ZH.pdf`：中文修复与复测报告。
- `Campus_r1_Library_Index_QA.zip`：原始交付索引、清单及复测证据。

十个 Release 附件合计 **3,370,511,145 字节**。完整资产需下载 01–08 八个资产包；另两个附件提供报告与索引。

八个资产包都是**独立普通 ZIP**，不是二进制分卷。按需下载一个包，或下载八包后解压到同一个新目录。它们共享 `Campus_Repair_20261007_r1` 根目录；解压时保留 ZIP 内目录结构，合并同名文件夹，重复的公共清单内容一致，可覆盖。不要把八个 ZIP 拼接成一个文件，也不要改动模型与纹理的相对目录。

### 按建筑查找

查看 [资产组索引](ASSET_GROUP_INDEX.csv)，找到对应下载包；[完整文件索引](ASSET_FILE_INDEX.csv) 提供每个文件的路径、大小、SHA-256 和所属包。正式包内包含 **93 个技术资产组、101 个 Blender 源文件、466 个 FBX、7,854 个唯一资产文件**。资产组包括单体、组合体和研究场景，不能理解为 93 栋不同建筑。

### 校验下载

[RELEASE_SHA256SUMS.txt](RELEASE_SHA256SUMS.txt) 列出全部十个附件的 SHA-256。在存放十个附件及该校验文件的同一目录中可运行：

```bash
sha256sum -c RELEASE_SHA256SUMS.txt
```

Windows PowerShell 可逐文件运行，并把结果与校验文件或下载表中的哈希比较：

```powershell
Get-FileHash .\Campus_Repaired_20261007_r1_01_assets.zip -Algorithm SHA256
```

只下载部分附件时，逐个核对其文件大小和 SHA-256；完整校验命令会提示未下载的附件缺失。解压后还可使用原交付包提供的 `verify_download.py` 检查对应资产组。历史说明中的文件库下载方式保留作归档；本次公开下载以本仓库 Releases 为准。

### 发布状态与核验记录

[PUBLICATION_VERIFICATION.json](PUBLICATION_VERIFICATION.json) 是 **2026-10-12 发布前准备记录**，其 `publication_status` 保持 `NOT_YET_PUBLISHED`，不作为 GitHub 已发布或已公开下载的证明。实际发布状态、十个远端附件的大小和 SHA-256、公开下载检查结果由最终回执 `FINAL_PUBLICATION_VERIFICATION.json` 记录。详见 [验证范围](VERIFICATION.md)。

## 版本选择与使用范围

- Rockefeller Chapel：`Rockefeller_Chapel_v0.1` 是用户偏好的优先版本；`RockefellerChapel_v02` 为独立备选，两者均保留。
- `BlakeCobbMapProxy` 是敏感性研究用代理场景。
- 旧版验证文档放在 `historical_evidence`，属于历史证据；当前文件以 `release_manifest/file_manifest.json` 为准。
- 本版涵盖重复表面与法线修复、LOD 补充、组合体接缝修复，以及纹理打包和相对路径整理。详见 [修复与验证说明](VERIFICATION.md)。

## 明确限制

未完成 Cities: Skylines II 编辑器或游戏内验收；不声称提供可直接安装的 `.cok`、已完成 prefab、Paradox Mods 发布成品或游戏兼容保证。亦不保证测绘精度、全局水密实体、室内、碰撞或导航系统。

## 权利说明

本次整理不新增或替换任何开源许可证。保留文件中已有来源与权利说明；公开下载不自动授予额外使用、再分发或商业许可。第三方名称、标识及附带资源的权利归各权利人。项目与芝加哥大学及游戏发行方不存在所声称的官方隶属或背书关系。
