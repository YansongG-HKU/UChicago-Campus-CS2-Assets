# 2026-11-20 芝大第三批远档与庭院接缝

延续同一草稿及 Blender 4.3.2。独立复算本环境缓存八个公开 r1 ZIP 的 SHA，均与公开更新链一致；使用其中已解出的 r1 在新目录完整重跑双层安装器，7,854 → 7,940 → 8,032 个文件，最终全部资产清单和 SHA 通过。三批工作的技术源树均由同一严格版加草稿覆盖得到。

| 对象 | 本轮结果 | 仍需检查 |
| --- | --- | --- |
| Booth Harper Center | 原包近、中和两个玻璃 7500 与当前源一致，远档原包 2,208 面属于 20261013 源 `a03419e…`，有向面及 UV 与该版本完全一致。11 月分支源 `29c3935…` 的远档实际为 1,986 面。用当前源新出三档及两个玻璃 7500 后逐份回读，UV 差 0，最大点差 10.2 µm。当前四组屋盖凹斗保留，16 个向下剖面命中；三档西入口框／背面有独立采样证据。全包 2,248,125 → 2,129,101 字节，PNG 18 → 10 张。远档减少 222 三角但单份 FBX 字节 91,868 → 92,300。 | 远档 1,986 面仍高于项目常用的 500 面建议。远档玻璃为原方案的烘焙表达，入口实体深度、实景位置和运行时性能待验。 |
| Smart Museum 与 Cochrane-Woods | 两栋独立文件的原交付 7500 三档均实际回读及逐角比较。组合内实测两处屏墙端部与 Smart 北壁在 72 个采样位置重复接触，去除 Cochrane 被遮蔽的端面，每档去面面积 24.15 m²，保留两侧各 0.15 m 可见压顶。切分边界后 Cochrane 三档由 1,982／504／200 变为 1,984／506／202；Smart 保持 2,086／446／134，源有向点和角 UV、材质绑定不变。复测三档 72 种采样都由 Smart 单独封口，两侧各档 24 条低位路径仍畅通，6 条高位路径命中过梁。六份组合新 7400 回读的 UV 差 0，绝对最大点差 4.8 µm。 | 组合接线由现有模型决定，庭院宽度、门口现况、游戏着色、地坪、碰撞和导航待验。独栋导入仍使用各自封闭源。 |

Booth 新包复用五条既有纹理共享映射。源包本来只有规范主贴图和配置映射，故检查器现在允许省略完全由 `sharedAssets` 解析的 LOD1 别名文件，仍验证实际目标文件与导出相对引用。旧 7500 与新 7500 均保留于独立存档。参阅 [Rafael Viñoly 的 Booth 项目](https://vinoly.com/works/university-of-chicago-booth-school-of-business-charles-m-harper-center/)及[芝大对艺术建筑与共用庭院的说明](https://architecture.uchicago.edu/locations/cochrane_woods_art_center/)。

[真实 FBX 和 Blend 差量](patches/manifest.json)已重放并核对确切输出 SHA。[实测记录](evidence/)和[同镜图](previews/)可独立核查。以下命令输出到新目录：

```sh
python candidates/20261120-cloud/apply_candidate_deltas.py /path/to/technical-tree /path/to/new-output --patch-dir candidates/20261120-export-review/patches
```

按交接 62 个计，三批已新增 **7 个首检**。芝大 **38/88**、哥大 **19/19**、宾大 **12/12**，合计 **69/119**，剩余 **50** 个均在芝大。宾大 Quad 另有 **34 段**已首检。Woodlawn 和 Chicago Lying-In 的补充复验没有增加上述计数。CS2 编辑器及游戏实测仍 **0/153**。原台账未迁至 Codex 环境，计数以已知交接基数、新增条目和仓库证据去重。

下一批从 D’Angelo Law Library、Law Classroom Administration 及两者 Law Quadrangle 组合入手，再查 Keller Center。接缝在组合内核验，计数沿用独立资产口径。Baker 庭院和玻璃采光带仍缺能区分铺装、窗头、窗台的可信高程证据，现有实际修复保留在第一批候选。
