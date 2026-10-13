# 校园资产完整公开更新链 · 2026-10-13

最新版需要完整的两层更新：

公开 r1 的 8 个资产 ZIP（7,854 文件） → 第一层 13 个 ZIP（7,940 文件） → 第二层 22 个 ZIP（8,032 文件）。

不要把第二层直接用于 r1，也不要跳过第一层。本目录包含两层更新所需的全部 35 个 ZIP，共 170,162,103 字节；它们引用公开 r1 的既有字节，无需重新运行 Blender。

## 最简单的方式：可选校验与安装脚本

下载/克隆本仓库并保持目录结构。在仓库顶层用 Python 3.9 或更新版本运行：

```sh
python updates/20261013/reconstruct.py --download-base --work ../Campus_Strict_Work
```

程序会从[既有公开 r1 Release](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1)下载并验证原始八包，从当前目录读取两层更新文件，校验后依次运行两个原有安装器。

如果已把公开 r1 八包合并解压，可跳过下载与重复解压：

```sh
python updates/20261013/reconstruct.py --base ../Campus_Repair_20261007_r1 --work ../Campus_Strict_Work
```

- --work 指定的目录必须尚不存在，父目录应已存在。推荐使用短路径；Windows 长路径可能需要系统支持。
- --download-base 推荐至少 16 GB 可用空间；已有外部 --base 时推荐至少 8 GB。程序保留下载、基线、中间版和最终版，不自动删除这些文件；只清理它在全新工作目录内自行创建的临时解压分块与已使用的差量副本。
- 最终资产目录：Campus_Strict_Work/Campus_Strict_20261013。
- 中间版：Campus_Strict_Work/Campus_Cloud_Offline_Candidate_20261012。
- 只使用 Python 标准库，不启动 Blender、游戏或任何资产内脚本。macOS/Linux 可将 python 替换为 python3，Windows 可用 py -3。
- 更新文件默认从脚本旁的相对路径读取。可用 --updates-url 指定本仓库 raw.githubusercontent.com/YansongG-HKU/UChicago-Campus-CS2-Assets/<ref>/updates/20261013 的官方 HTTPS 原始文件根地址，以下载缺少的更新 ZIP；不接受其他仓库或任意域名，也不会跳过哈希失败。
- 脚本固定校验 chain_manifest.json 的 SHA，随后校验每个 ZIP、每个分块和完整资产清单。请先从可信仓库取得脚本和校验清单；哈希不是数字签名，不能凭不可信文件自证来源。

## 手动安装：两层都必须执行

1. 下载并合并解压[公开 r1 的八个 Campus_Repaired_20261007_r1_XX_assets.zip](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1)，得到 Campus_Repair_20261007_r1/assets/。原始八包的 URL、大小与 SHA 保存在 chain_manifest.json 的 public_base_archives.archives 中。
2. 下载[第一层目录](layer1_20261012/)全部 13 个 ZIP。将 START 和 12 个数据 ZIP 解压到同一个补丁文件夹，合并出 Campus_LOD_Patch/。进入这个文件夹，执行：

```sh
python apply_delta.py --original "/path/Campus_Repair_20261007_r1" --output "/path/Campus_Cloud_Offline_Candidate_20261012"
```

3. 只有看到 SUCCESS，才把生成的 7,940 文件版用作下一层输入。下载[第二层目录](layer2_20261013/)全部 22 个 ZIP，合并解压出 Campus_LOD_Strict_Patch_20261013/。进入这个补丁文件夹，执行：

```sh
python apply_second_delta.py --original "/path/Campus_Cloud_Offline_Candidate_20261012" --output "/path/Campus_Strict_20261013"
```

4. 看到第二次 SUCCESS 后，再执行只读复核：

```sh
python verify_bundle.py --root "/path/Campus_Strict_20261013"
```

应有 8,032 个资产全部 SHA 匹配，且没有缺失或额外资产。每次输出目录都必须全新，不能覆盖或嵌套于原资产目录。不要将数据 ZIP 按字节直接拼接；先合并解压，安装器会按 parts.json 连接其中的 .bin 数据块。这些 .bin 不是可直接导入模型软件的文件。

任何校验失败都应停止。失败或中断可能留下不完整的新目录，不能使用；检查原因后自行移走/清理该目录，再选择新输出重试。原始基线和既有资产目录不被修改。

## 下载与校验清单

- [全链清单](chain_manifest.json)：两层顺序、公共 r1 来源和每个更新 ZIP 的长度/SHA。
- [全部公开文件 SHA-256](SHA256SUMS.txt)
- [第一层 SHA-256](layer1_20261012/SHA256SUMS.txt)
- [第二层 SHA-256](layer2_20261013/SHA256SUMS.txt)
- [链兼容与原有复原验证](CHAIN_VERIFICATION.json)

第一层 61,501,644 字节；第二层 108,660,459 字节。每个文件均小于 5.5 MB，适用于仓库文件方式分发，无需另建 GitHub Release。

第一层清单：
- [Campus_LOD_Patch_START_HERE.zip](layer1_20261012/Campus_LOD_Patch_START_HERE.zip)
- [Campus_LOD_Patch_01_of_12.zip](layer1_20261012/Campus_LOD_Patch_01_of_12.zip)
- [Campus_LOD_Patch_02_of_12.zip](layer1_20261012/Campus_LOD_Patch_02_of_12.zip)
- [Campus_LOD_Patch_03_of_12.zip](layer1_20261012/Campus_LOD_Patch_03_of_12.zip)
- [Campus_LOD_Patch_04_of_12.zip](layer1_20261012/Campus_LOD_Patch_04_of_12.zip)
- [Campus_LOD_Patch_05_of_12.zip](layer1_20261012/Campus_LOD_Patch_05_of_12.zip)
- [Campus_LOD_Patch_06_of_12.zip](layer1_20261012/Campus_LOD_Patch_06_of_12.zip)
- [Campus_LOD_Patch_07_of_12.zip](layer1_20261012/Campus_LOD_Patch_07_of_12.zip)
- [Campus_LOD_Patch_08_of_12.zip](layer1_20261012/Campus_LOD_Patch_08_of_12.zip)
- [Campus_LOD_Patch_09_of_12.zip](layer1_20261012/Campus_LOD_Patch_09_of_12.zip)
- [Campus_LOD_Patch_10_of_12.zip](layer1_20261012/Campus_LOD_Patch_10_of_12.zip)
- [Campus_LOD_Patch_11_of_12.zip](layer1_20261012/Campus_LOD_Patch_11_of_12.zip)
- [Campus_LOD_Patch_12_of_12.zip](layer1_20261012/Campus_LOD_Patch_12_of_12.zip)

第二层清单：
- [Campus_LOD_Strict_START_HERE.zip](layer2_20261013/Campus_LOD_Strict_START_HERE.zip)
- [Campus_LOD_Strict_Patch_01_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_01_of_21.zip)
- [Campus_LOD_Strict_Patch_02_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_02_of_21.zip)
- [Campus_LOD_Strict_Patch_03_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_03_of_21.zip)
- [Campus_LOD_Strict_Patch_04_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_04_of_21.zip)
- [Campus_LOD_Strict_Patch_05_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_05_of_21.zip)
- [Campus_LOD_Strict_Patch_06_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_06_of_21.zip)
- [Campus_LOD_Strict_Patch_07_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_07_of_21.zip)
- [Campus_LOD_Strict_Patch_08_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_08_of_21.zip)
- [Campus_LOD_Strict_Patch_09_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_09_of_21.zip)
- [Campus_LOD_Strict_Patch_10_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_10_of_21.zip)
- [Campus_LOD_Strict_Patch_11_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_11_of_21.zip)
- [Campus_LOD_Strict_Patch_12_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_12_of_21.zip)
- [Campus_LOD_Strict_Patch_13_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_13_of_21.zip)
- [Campus_LOD_Strict_Patch_14_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_14_of_21.zip)
- [Campus_LOD_Strict_Patch_15_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_15_of_21.zip)
- [Campus_LOD_Strict_Patch_16_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_16_of_21.zip)
- [Campus_LOD_Strict_Patch_17_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_17_of_21.zip)
- [Campus_LOD_Strict_Patch_18_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_18_of_21.zip)
- [Campus_LOD_Strict_Patch_19_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_19_of_21.zip)
- [Campus_LOD_Strict_Patch_20_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_20_of_21.zip)
- [Campus_LOD_Strict_Patch_21_of_21.zip](layer2_20261013/Campus_LOD_Strict_Patch_21_of_21.zip)

## 内容与验证范围

- 最终：8,032 个资产文件、3,505,395,608 字节，包含 101 个 Blender、484 个 FBX、4,652 张 PNG/JPEG。技术分组数不代表独立建筑数。
- 第一层最终清单与第二层基线的全部 7,940 个路径、字节数、SHA 一致；第二层最终清单与当前 8,032 文件版完全一致。两层都没有删除资产。
- 33 个数据 ZIP 和第一层 START 保留原字节。第二层公开 START 仅调整说明和随包报告范围，其安装器、校验器、分块索引、完整资产清单及变更清单均保持实际复原验证时的原字节。
- 两层的原有完整复原测试均通过；本次重新验证所有 ZIP CRC、各分片与完整差量 SHA，以及两层清单衔接。可选整链辅助脚本的检查测试另见 ORCHESTRATOR_TESTS.json。
- [离线审查材料](../../audit/20261013/README.md)与[图册](../../atlas/20261013/README.md)独立提供，不需要为安装下载额外的历史证据大包。第一层原始说明中的旧 qa/ 引用属于历史背景，不是本次安装依赖。

各资产现有许可、署名、字体许可和历史来源资料保留；此封装不授予新的统一许可。原公开 r1 Release 与其校验信息保持不变。

本项目尚未完成 CS2 游戏/编辑器导入、玻璃/水体着色、实际 LOD 切换、碰撞/导航、帧率、显存与加载性能验收。文件字节一致和离线审查不能替代游戏运行验证。

English summary: Use public r1 (eight ZIPs), then all 13 first-layer ZIPs, then all 22 second-layer ZIPs. The final tree contains 8,032 files. The optional reconstruct.py verifies and applies this complete sequence into new directories. It preserves the original base, uses only Python's standard library, and does not run Blender or CS2.
