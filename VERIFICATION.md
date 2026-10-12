# 修复与验证范围

## 2026-10-07 原修复版证据

原交付的独立复测报告记录：101 个 Blender 源文件和 466 个 FBX 均已进行 Blender 4.3.2 打开/导入检查；检查 514 对源文件/导出对象对应，以及 1,453 条内嵌图像记录。最终源文件与导出文件哈希与清单一致，FBX 图像路径已整理为可解析的相对路径。

修复涵盖：Saieh Hall、Keller Center、Quadrangle Club 重复表面清理；D’Angelo LOD2 入口和立面补充；组合体 Main/LOD1/LOD2、接缝与贴合关系；源文件内嵌纹理及外部副本保留。历史输入与旧验证资料保留，当前修订另行记录。

详细证据位于 [FINAL_QA_SUMMARY.json](archive_docs/release_manifest/independent_qa/FINAL_QA_SUMMARY.json)，原中文 PDF 列在 [本版 Release](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/releases/tag/campus-20261007-r1) 的附件清单中。这些是原修复版的既有检查，本次公开发布准备未重复运行 Blender 或游戏。

## 2026-10-12 发布准备复核

检查结果见 [PUBLICATION_VERIFICATION.json](PUBLICATION_VERIFICATION.json)。本次重新恢复八个正式资产 ZIP，并重新读取全部条目进行 CRC 检查、逐资产 SHA-256 与大小比对、重复/遗漏检查和完整包哈希比对；7,854 个资产文件与清单对应。另附 [完整资产文件索引](ASSET_FILE_INDEX.csv)、[资产组索引](ASSET_GROUP_INDEX.csv) 和 [十个发布附件的校验和](RELEASE_SHA256SUMS.txt)。

该 JSON 是发布前准备记录，`artifact_validation_status: PASS` 仅表示其中记录的文件检查通过；`publication_status: NOT_YET_PUBLISHED` 保留原值，**不证明 GitHub 发布成功，也不证明远端附件可公开下载**。

发布准备还检查了文件名及内容中的常见凭据、私钥、个人邮箱与非项目内部笔记标记，保留原字体许可中的公开署名与联系方式；此类自动扫描不能证明任何形式的敏感信息绝对不存在。

## GitHub 发布最终核验

目标仓库为 [YansongG-HKU/UChicago-Campus-CS2-Assets](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets)，本版标签为 `campus-20261007-r1`。逐附件预期文件名、字节大小、SHA-256 和直接下载链接见 [DOWNLOADS.md](DOWNLOADS.md)。

实际发布完成后，独立的 `FINAL_PUBLICATION_VERIFICATION.json` 记录仓库与 Release 链接、公开/非草稿状态、全部十个远端附件的状态、大小、SHA-256 及公开下载检查结果。应以最终回执记录的实际检查范围与结果判断发布是否完成；本文件与发布前 JSON 中的准备结果不能替代该核验。

## 验证边界

- 未进行 CS2 编辑器或游戏运行验收。
- 特定视角与采样接缝检查不等于全局水密性证明。
- 不证明测绘精度、室内完整度、碰撞、导航或所有游戏版本兼容性。
- 历史文件可能引用生成时的工作目录；仅作为来源与复测上下文保留，不代表下载者必须拥有这些路径。
