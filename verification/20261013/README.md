# 20261013 公开发布核验

## 最新公开入口复核

[精简最终回执](LATEST_PUBLIC_VERIFICATION.json) 对应不可变提交 [d5a541a30db9e74d602dff5e49cbf2855bd05ecd](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/commit/d5a541a30db9e74d602dff5e49cbf2855bd05ecd)：131 个预期 Git 对象匹配，20 个变化文件匿名下载通过；111 个未变化文件与首次公开证明保持同一对象。35 个 ZIP 保持原字节，重新检查后复用。

从该提交匿名取回的兼容版脚本又实际完成完整两层重建；8,032 个最终资产、7,940 个中间资产和原 r1 的 7,854 个资产均独立全量重哈希通过。该精确公开脚本自己的联网函数也成功下载并校验了原始文件地址与历史 Release 重定向附件。没有把工具下载成功冒充脚本下载成功，也没有宣称重新自动下载了全部八个基础包。

## 首次完整发布

[公开提交 60fe8297c591682166c148643b5017b811bad35c](https://github.com/YansongG-HKU/UChicago-Campus-CS2-Assets/commit/60fe8297c591682166c148643b5017b811bad35c) 已完成独立验证：

- 119 个新增/更新文件、273,839,372 字节全部匿名下载成功；HTTP 200、SHA-256 与 Git blob SHA 全部一致。
- 包含全部 35 个更新 ZIP、23 份 PDF、审计记录和入口说明；没有不可达文件。
- 使用从该提交取回的脚本和补丁，真实完成 7,854 → 7,940 → 8,032 的两层重建。
- 独立第二次读取全部 8,032 个最终资产与 7,940 个中间资产，全部匹配。原 r1 的 7,854 个文件在前后检查中逐一未变。
- 原 r1 标签和 10 个 Release 附件保持不变。

[汇总回执](initial-publication/PUBLIC_VERIFICATION_SUMMARY.json) · [逐文件公开 URL/哈希](initial-publication/PUBLIC_DOWNLOAD_VERIFICATION.json) · [完整重建核验](initial-publication/PUBLIC_RECONSTRUCTION_VERIFICATION.json) · [历史版本保留核验](initial-publication/PUBLIC_REPOSITORY_PRESERVATION.json)

这些是对应不可变提交的历史事实，后续文档更新不改写它们。所有实际模型、35 个更新 ZIP 与资产清单都与这次验收保持一致。

## 下载组件兼容性

后续下载组件调整仅恢复标准 Python HTTPS/系统代理兼容性，保留官方 GitHub 目标限制、TLS 证书/主机名检查及下载长度/SHA 校验，不更改任何模型或补丁数据。真实网络检查及具体范围见 [网络兼容性记录](../../updates/20261013/NETWORK_COMPATIBILITY.json)。

## 验证边界

这是公开下载、文件完整性和云端离线重建验证，没有进行 Blender 或 CS2 编辑器/游戏内验收。LOD 切换、玻璃/水体自动分派、碰撞/导航、内存和运行性能仍未验证；Paradox Mods 发布条目仍为 0。
