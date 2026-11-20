# 2026-11-20 芝大第二批模型复核

沿用已核全量 SHA 的 20261013 公共重建基线及两级 11 月候选覆盖层，在 Blender 4.3.2 保存两个独立候选。源路径、接触坐标与 PBR 贴图来自现有还原文件。图中为当前实际 Blender 同镜工作台画面。

| 芝大资产 | 实测与候选 | 尚未放行 |
| --- | --- | --- |
| Campus North Residential 单体 | 北墙直段两档共移动 1,270 个 20 mm 背缝上的脊肋与腰带后点，Y 方向内移 23 mm。四跨、两类构件、两档各三线的 48 组采样从 20 mm 后缝变成约 3 mm 搭接，外侧可见命中保持相同。三档 75,560／18,216／234 面与 UV 均无增减，新的三档 7500 以原比例和相对贴图回读。原 21 张 PNG 改为 10 张规范文件，整包 4,145,220 → 3,966,831 字节，减 4.30%。 | 仅一段平墙的背缝，未触碰转向墙、游戏窗、内凹屋室、Baker 组合或宿舍地坪。实景面板的双曲折法和连接尺寸仍有不确定性。 |
| Cathey Dining | 单体原 7500 的三档不透明网格和两档玻璃全数回读。三档各 15 个曲面屋盖点、18 个基座点均命中；近中在南门中线有独立玻璃，其后约 2.90 m 有第二面，远档首面与近中玻璃线重合。用当前 Burton-Judson 独立源按合同平移组合。三档共 75 点查实接线两面的法线相反且重合，组合中只删除 Cathey 端的 12／2／2 片，保留 Burton 一侧，复测全部 75 点均保有唯一接点。三档 Cathey 组合不透明面降到 4,846／1,312／352；含玻璃和旧翼的八份检查用 7400 实际回读。 | 这不是独立 Cathey 的替换，也未新开通往旧厅的通道。近中玻璃后的实体与正式通行净空待地形、场景和碰撞复核。Burton 全栋首检单独计。 |
| Woodlawn Commons | 按住宅与餐厅完整组合打开严格树版 `e750b32…`。每档四段内部分缝各 25 次横向采样，发现 98 个双侧空命中与旧合同要求省去内墙一致，另外 2 个为远离理论分缝的构件边，未测到该理论线上的双面重合。两个单体组件六份原交付 7500 全部回读。住宅与餐厅各有自己的导入坐标与质感，继续依作者组合关系使用。 | 当前采样只测内部分缝，外围共享基座、屋顶花园及北到达庭院还需专门验证；未把两个依存文件计为两栋新增首检。 |

当前草稿累积新增 4 个独立资产首检，包含上一批 Billings、Levi 及本批 Campus North 住宅、Cathey。根据交接基数合计 **66/119**，芝大 **35/88**，余 **53**。芝大原工作区台账未恢复，Woodlawn 与 Chicago Lying-In 的复验不额外加数。哥大 19/19，宾大 12/12，另有 Quad 34 段。游戏／编辑器为 **0/153**。

主资料为 [Studio Gang 校园北区](https://studiogang.com/projects/university-of-chicago-campus-north-residential-commons/)、[芝大法学院 Cathey 与 Burton-Judson 图册](https://www.law.uchicago.edu/slideshows/slideshow-view-south)及[Elkus Manfredi Woodlawn 竣工项目](https://www.elkus-manfredi.com/project/university-of-chicago-woodlawn-residential-and-dining-commons/)。

## 复现

[二进制补丁](patches/manifest.json)逐字节恢复白盒验证的宿舍候选。[重建安装说明](../20261118-technical/README.md)用于获取旧源。以下命令需要 Blender 4.3.2 或 Python 与 `zstandard==0.25.0`。

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/new-output --patch-dir candidates/20261120-followup/patches
blender -b -t 2 --factory-startup --disable-autoexec --python-exit-code 1 --python candidates/20261120-followup/cathey_burton_joint.py -- /path/to/CatheyDining.blend /path/to/BurtonJudsonCourts.blend /path/to/new-CatheyBurton.blend
```

[同镜图](previews/)和[实测](evidence/)保留。Cathey 组合的 Blender 输出容器可能随重存时间变化。脚本要求输入文件的确切 SHA，其近、中、远面数、源地理变换、导出回读和角点 UV 都有机器证据。
