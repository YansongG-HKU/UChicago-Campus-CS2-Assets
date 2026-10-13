# 验证范围与证据

**版本导航：** [20261013 最新版首页](README.md) · [r1 原版下载表](archive_docs/20261007_r1/DOWNLOADS.md) · [r1 原版验证范围](archive_docs/20261007_r1/VERIFICATION.md)。从旧 Release 进入的读者：原附件仍是 7,854 文件的 r1；只有按完整两层更新链恢复后才是 8,032 文件的最新版。

本文件描述 **20261013 严格离线复核版**。数值通过、图像已生成、已人工看图和游戏验收是不同范围，不能互相替代。

## 1. 模型与人工证据

[136 组审计表](audit/20261013/review_register_136.csv) 覆盖 101 个源文件中的 136 个源/家族条目：133 个完整 LOD 家族、2 个 Main-only 组、1 个背景场景。每条均有实算的最终源 SHA-256，原记录与最终处置分开保存。

36 个修复家族出现项涉及 23 个建筑名称、31 个源文件和 54 个命名网格。修复后的最终源文件以原材质在 45°、135°、225°、315° 查看 Main/LOD1/LOD2 联系图，并重新人工记录。其余 100 项使用已有人工证据，其中 84 项整源 SHA-256 一致，16 项为已修改共享源内的非目标家族，保留记录核对了网格、UV、角点法线、材质槽和变换。

没有声称本轮对全部 136 项重新渲染、重新人工看图。自动生成诊断图、哈希相同或脚本返回成功，不能替代对应视角的实际人工观察。

证据：[登记校验](audit/20261013/verification/register_validation.json)、[网格整合](audit/20261013/verification/mesh_merge_verification.json)、[最终保存后签名](audit/20261013/verification/saved_source_signature_verification.json)、[原始证据来源说明](audit/20261013/verification/evidence_provenance.json)。

## 2. FBX、材质与明确例外

本轮 **76 个唯一最终 FBX** 实际导入 Blender 检查，另有一次辅助源比较。58 个是原路径/原版本替换，18 个是新增验证导出。此数字不表示全部 484 个最终 FBX 在本轮重新导入；新增单对象验证文件不代表完整组合体。

检查记录包括几何与多边形对应、源/导入顶点误差、绕序、已定义角点法线、UV、材质索引、变换、文件版本和相对依赖。法线比较使用局部几何双精度叉乘再经世界矩阵逆转置，严格点积阈值仍为大于 0.99998，未为 Harper 微小面放宽阈值。

Saieh 原有微米级薄三角面存在未定义角点法线，逐文件、逐对象和面积/计数已明确列出；这些例外未被伪装成普通有效法线通过。

原对象引用的材质槽、节点及图像语义保留，全部原纹理字节仍可取得。Blender 保存时省略了 10 个未使用重复材质数据块和 74 个未使用图像数据块。原玻璃无材质槽、原不透明 LOD atlas 等约定保留，不能保证三个层级外观完全一致。

证据：[实际 FBX 导回记录](audit/20261013/verification/actual_fbx_import_checks.json)、[导出复核摘要与例外](audit/20261013/verification/final_export_qa_summary.json)、[材质与图像保留摘要](audit/20261013/verification/material_preservation_summary.json)。

## 3. 文件恢复与资料打包

完整恢复路线必须依次使用原 r1 八包和两层更新，文件数为 **7,854 → 7,940 → 8,032**。最终集合包含 93 个技术组、101 个 .blend、484 个 .fbx，共 3,505,395,608 字节；逐文件权威内容在 [最新版完整索引](ASSET_FILE_INDEX_20261013.csv)，分层清单与操作入口在 [更新目录](updates/20261013/README.md)。

已完成的严格第二层恢复测试校验 21 个数据 ZIP 和 1 个入口 ZIP 的 CRC/SHA-256；新输出的 8,032 个资产逐文件与最终清单匹配，原 7,940 文件基线未被修改。拒绝测试覆盖已有输出、嵌套输出、错误基线和损坏分片。这里描述已完成的离线恢复测试，不将其冒充 GitHub 远端下载校验。本次第二层公开入口 ZIP 精简了说明与证据副本，安装器和资产相关输入保持不变，因此原测试记录中的入口包哈希/大小与公开入口包不同；请使用 [当前更新清单](updates/20261013/chain_manifest.json) 核对公开包。

公开审计资料准备时，独立重新核对了 101 个最终源文件和 76 个最终 FBX 的身份哈希。23 份 PDF 保持原交付字节，并检查了提取文字、元数据和解码对象字典；该准备步骤没有重跑 Blender 或游戏。自动扫描也不是“绝无敏感内容”的保证。

两层清单衔接另已逐路径、大小与 SHA-256 核对：第一层结果恰好是第二层输入，第二层结果与 8,032 文件最终清单一致。公开 35 个 ZIP 的 CRC 与分片哈希检查见 [完整链校验记录](updates/20261013/CHAIN_VERIFICATION.json)。

证据：[严格层恢复记录](audit/20261013/verification/reconstruction_test.json)、[严格层文件校验](audit/20261013/verification/final_delivery_verification.json)、[公开资料字节检查](audit/20261013/verification/public_packaging_checks.json)、[PDF 文件名与哈希索引](atlas/20261013/index.json)。

## 4. 发布状态与 r1 历史

本次交付方式为主分支中的更新链与复核资料，未新建 GitHub Release，最新版八个自包含完整 ZIP 尚未公开上传。Code → Download ZIP 不能单独提供全部基础模型。

[原 r1 Release](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1) 的十附件下载记录保持历史事实。原 r1 曾记录 101 个 .blend、466 个 .fbx 的既有检查；这不是对最新版的相同覆盖声明。

根目录三个 `PUBLICATION_*` / `FINAL_PUBLICATION_VERIFICATION.json` 记录与 `RELEASE_SHA256SUMS.txt` 仍只适用于 r1。[历史档案](archive_docs/20261007_r1/INDEX.md) 保留这些文件的原始字节；其中 `NOT_YET_PUBLISHED` 是当时的准备状态，不覆盖后来的 r1 最终公开下载回执。旧版已发布也不证明最新版远端下载已经复核。

## 5. 尚未验证

- Cities: Skylines II 编辑器导入与游戏运行
- `_Gls` / `_Wat` 玻璃、水材质分派与游戏内外观
- 游戏内 LOD 自动切换、碰撞和导航
- 内存、帧率及其他性能行为
- Paradox Mods 上传、发布或验收；已发布条目为 **0**
- 测绘精度、全局水密、室内完整度及所有未审视角

审阅边界主要是建筑主体、轮廓和主要附体在已查看视角不出现破碎/大缺面。窗格、线脚、细台阶等允许记录在案的简化；作者共墙接口和地面接触开口按具体记录保留。完整限制和来源见 [公开 QA 摘要](audit/20261013/QA_SUMMARY.md)。
