# 2026-11-20 第四批，法学院与 Keller Center

当前技术覆盖树中按准确 SHA 打开 D’Angelo、Law Classroom Administration、Law Quadrangle 组合及 Keller，实际 Blender 4.3.2。原始独立 Blender 和 ProjectFiles 均保留。

- **D’Angelo Law Library**。独立 7500 三档 11,634／3,114／490 三角全部实际导入，有向三角及角 UV 与源一致。近中保留曲折的北及两侧立面和南扩建体关系。组合里的远档原本是 456 面，这轮作为独立的组合版本保留。芝大图书馆确认 1987 年扩建向南 45 英尺。当前模型的现场尺寸、后翼及游戏落地待验。[芝大图书馆](https://www.lib.uchicago.edu/law/about/facts/)
- **Law Classroom Administration 与 Law Quadrangle**。独立不透明三档 5,990／2,510／338 面及三个 2 面水体 FBX 7500 实际回读通过。组合两条连接线每档 50 个采样。原近／中／远分别有 20／20／50 个两侧共面的命中。每个候选面在四个局部点证实由相反朝向的图书馆墙面背衬，再仅去除教室端的 10／8／4 个三角。复验每档 50 个点都由图书馆一侧命中。原有近中中央约 0.12 m 退位保持。组合候选已回读 9 份独立 7400，角 UV 差 0，水面各 2 面，无材质，白盒几何不验水着色或玩家通行。走廊净空、池体与地坪、碰撞和引擎 LOD 切换继续待验。
- **Keller Center**。近中各 72 个柱位用同一坐标上、下检测，主档分别命中柱座与柱头的边界高度 1.704／13.20 m，中档为 1.524／13.35 m。远档采用原有贴图表示及实体顶底，样点检查只计柱位投影。三档各九个屋面点命中，包含北厅、两侧服务屋、三组锯齿采光、两块光伏及绿屋面。独立五份 7500 含两档玻璃全部回读，三档不透明为 30,200／14,372／356 面。未见本轮有依据改动的屋顶形体；前廊开孔在游戏内的 alpha、玻璃和基础仍待验。[芝大 Keller 翻修资料](https://architecture.uchicago.edu/locations/keller_center/)

[实际候选二进制差量](patches/manifest.json)已验证完整重放。另有[近中远回读和射线记录](evidence/)与[同镜图](previews/)。从已经复验的技术树恢复方式：

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/new-output --patch-dir candidates/20261120-law-review/patches
```

按交接基数，这四批累计新增 **10 个独立资产离线首检**。三校合计 **72/119**，其中芝大 **41/88**，哥大 **19/19**，宾大 **12/12**，尚余芝大 **47** 个。宾大 Quad 另有 **34** 段已首检。组合、历史候选及补充范围不另加数。CS2 游戏或编辑器验收仍为 **0/153**。Baker 的庭院和采光窗仍受制于可核实标高，庭院三处已知对照点不用于假定整体坡面。

后续独立批次先查 Henry Hinds Laboratory、John Crerar Library 和 William Eckhardt Research Center，复核芝大旧台账的可见条目后再推进。原 Dot 工作区未被恢复，以上证据来自独立 Codex 环境及仓库可取得的已核资产。
