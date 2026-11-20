# CS2 Editor 六项试导入交接

这组六项锁定芝大草稿提交 `ada4b6cafa5d010e2bbd814e77331e3e878878c5`。每个资产目录在 `ProjectFiles/` 下。完整 FBX 与相对 PNG 的 SHA-256、单位、坐标轴及 `settings.json` 逐项见 `exact-sha256.json`。室外包围盒使用 Blender 里的米值。

| 资产 | 导入来源 | 首先观察 |
|---|---|---|
| MitchellTower | 技术基线 | 门洞、塔脚、与邻楼的近中档交界 |
| MandelHall | 技术基线 | 东西端墙、剖坡落地、与塔组件齐缝 |
| HutchinsonCommons | Completion 差量 | 与 Reynolds 的窄缝、材料切档 |
| ReynoldsClubhouse | Completion 差量 | 远档连接、台阶及遮挡 |
| HarperMemorialLibrary | Completion 差量 | 近中档改过的隐蔽面、可见背面、日夜玻璃 |
| SaiehHall | Closeout 差量 | 庭院窗层、阁楼通窗、日夜背面及中档 |

1. 在独立获准、可运行 Cities: Skylines II 的机器上建空的测试项目。记录游戏版本与测试保存路径。
2. 在 Editor 打开 Asset Importer，设置 Project Root 为本包的 `ProjectFiles`，逐个选 Assets Folder 与适用的 prefab 类型。保留一份导入日志，核对场景尺度和地块。
3. 分别在平地、斜坡放置模型。并排校验 Tower 四件组，用两侧近景和三个视距观察接缝、落地、台阶和穿行。
4. 核对日间、夜间的近中远档。看窗与玻璃、PBR、材质缝、碰撞、地块定位及褪变。保存本地测试存档与候选 prefab，重载再检查一次。
5. 每项记录提交、文件 SHA-256、截图、游戏版本、结果和待修项。当前实际 CS2 验收是 0/153。

[Paradox 官方 Asset Importer 流程](https://www.paradoxinteractive.com/games/cities-skylines-ii/news/adding-custom-assets)
