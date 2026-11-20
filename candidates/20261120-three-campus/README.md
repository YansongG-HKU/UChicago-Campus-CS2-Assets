# 三校导入包复核与减重

本轮覆盖芝大 88 件、哥大 19 件、宾大 12 件独立资产与 34 个 Quad 分段，共 153 个导入目录。119 个独立资产的建筑首检沿用各仓逐栋台账。此次新增工作的对象是固定版本的实际导入文件，重点为三档、材质引用、包体、可验证的局部几何及发布阻塞。

## 本目录的证据

- `asset-audit.csv` 逐件记录导入目录和独立 ZIP 字节、三档三角数、包围盒、待验标记。包体计 FBX、PNG 和设置，另行保留作者 Blend、渲染预览和备用整组导出。体积采用十进制 MB。
- `asset-hashes.json` 固定每件候选的实际字节、SHA-256、FBX 单位设置和相对贴图，便于重建后核验。
- `three-campus-summary.json` 汇总三校。哥大和宾大逐项记录在各自既有草稿。
- `editor-trial-exact.json` 固定六个原尺寸、原字节版试导入包。它与本轮减重包分别保存。
- `editor-trial.md` 记录 Editor 最小验证流程。
- `tools/` 保留导入包的重建及实际 Blender 4.3.2 回导复验脚本。

## 离线通过项和待验

初始 740 个分档 FBX 和候选最终的 648 个 FBX 都用 Blender 4.3.2 实际回导。共校验 1530 张 PNG 和 153 个独立 ZIP。以顶点、面序、UV、材质、米制包围盒和图片引用对比最终版；哥大 26 个零面积面的局部修改另做同镜和非退化角点核验。芝大的哈希贴图副本只有在逐字节匹配正式文件时才移除，同步修正 FBX 引用。既有 `settings.json`、通道文件命名及共享映射保留。PNG 压缩保留全部解压扫描行和非 IDAT 数据块。哥大、宾大 168 个窗面或玻璃 FBX 按项目规则解除预览材质绑定。24 个玻璃 FBX 仅重新展开原有零面积 UV 的面，原有效 UV 保留。三校 56 个非空玻璃 FBX 的最终 UV 无面积塌缩、无正面积重叠。

三档包围盒只是模型测点，实景绝对高程和游戏地形仍需独立证据。游戏内验收当前为 **0/153**。芝大仍有 Baker Dining 庭院/采光窗高程、Harper 背面局部、Ryerson 连廊、Kent 北体量待证。哥大和宾大的个别立面及现状改建问题见各仓逐栋台账。官方 Asset Importer 流程已核对，细则 Wiki 请求返回 HTTP 401。7500 为已写出且 Blender 能回读的 FBX 二进制版号。最终近远切换、碰撞、玻璃和着色仍需要 Editor。

[Paradox 官方 Editor 工作流](https://www.paradoxinteractive.com/games/cities-skylines-ii/news/adding-custom-assets)

## 重放

在新工作目录使用 Blender 4.3.2、Python 3、Pillow 和 zstandard。哥大、宾大用留有真实 LFS 实体的锁定 main 克隆，文件夹分别为 `Columbia-CS2-Assets` 和 `Penn-CS2-Assets`。芝大采用原技术树和既有草稿候选。将本目录的 `chicago-baseline.json` 放到独立芝大复建工作区的 `Review_20261120/continuation/inventory/plan.json`。从该复建目录下面新建工作目录运行。技术树恢复及哈希见 [完整源树候选](../20261118-technical/README.md) 与 [批次采用的原始导出路径](./chicago-baseline.json)。该清单的候选目录按脚本中列出的路径放置。

1. 运行 `python /path/to/tools/stage_packages.py --campuses Chicago Columbia Penn`。也可选择单校。
2. 对各校运行 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/portable_readback.py -- staged-packages-v1.json Chicago import-candidates-v2/Chicago`，按校替换两处名称。需要并行时使用 `--offset` 与 `--stride`。
3. 有 Columbia 时，从同一工作目录运行 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/clean_columbia_faces.py -- import-candidates-v1/Columbia columbia-geometry-fix`。只做其他学校时，向最终验证提供一个内容为 `{}` 的几何记录文件。
4. 运行 `python /path/to/tools/png_storage.py import-candidates-v2 png-verify`。对各校运行 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/finalize_import.py -- import-candidates-v2 Chicago png-verify/png-verified.json columbia-geometry-fix/zero-area-readback.json final-readback`，替换校园名和适用的几何记录。按清单比较最终输出 SHA-256。
5. 用 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/special_mesh_materials.py -- import-candidates-v2 final-readback Columbia` 处理哥大，替换为 Penn 处理宾大。用 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/glass_uv.py -- import-candidates-v2 glass-uv-audit.json` 取玻璃 UV 记录。运行 `blender -b --factory-startup --python-exit-code 1 --python /path/to/tools/repair_glass_uv.py -- import-candidates-v2 final-readback glass-uv-audit.json glass-uv-repair.json`，再运行玻璃检查脚本生成最终记录。
6. 三校复验齐备后运行 `python /path/to/tools/summarize.py`，生成分开的单件 ZIP 和逐项 CSV。独立复跑优先对照解包后的文件 SHA，压缩库实现可能影响 ZIP 自身 SHA。
