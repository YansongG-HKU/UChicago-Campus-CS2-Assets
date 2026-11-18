# UChicago 建筑检查与安全修复

## 本轮实际覆盖

云端 Blender 4.3.2 重新打开最新仓库对应的全部 101 个 Blender 源文件、导入全部 484 个原始 FBX。扫描 575 个网格和 1473 条文件贴图引用。136 条建筑/网格家族记录见逐项表；这些记录含重复版本、组合建筑，不能称为 136 栋独立建筑。

所有源文件及 FBX 可在 Blender 打开。未发现丢失贴图、无效 UV 数值、UV 超出 0–1、负缩放。所有贴图引用均已内嵌，尺寸为 512、1024、2048 或 4096 的正方形。主建筑家族及 LOD 各一材质；特殊玻璃/水面不含材质。Mansueto 的双材质对象是明确标记的预览玻璃，不应作为游戏导出对象。

## 已修复

仅在独立副本删除面积小于 1e-16 的退化面，不改建筑外形、尺度、贴图或原文件：
- BlaineJuddBelfield：BelfieldHall 主模型和 LOD1 各 1 面。
- SaiehAdditionsContext：SaiehHall 主模型 11 面、LOD1 4 面。
- SaiehHall：主模型 19 面、LOD1 4 面。

共 40 面。重新打开修复文件后，以上退化面计数归零；对象尺寸变化为 0；贴图均仍内嵌。相应 3 个整体 FBX 已重新导入 Blender，分别读取 9、12、3 个网格，包含原有 LOD。这些 FBX 是几何核查导出，不是已经通过游戏验收的预制件。

## 仍需优化或核实

逐项表中 31 条家族/版本记录有性能建议或本轮修复记录。LOD2 超过官方建议 500 三角面的重点包括 BoothHarperCenter 2208、BurtonJudsonCourts 1778、MitchellTower 1597、LillieHouse 1433、BondSwiftCloister 1388、SwiftHall 1322、KellyHall 1036、IdaNoyesHall 854、RegensteinLibrary 778、SaiehHall 718/719。500 是优化建议，不是所有建筑的强制淘汰线。为避免轮廓损坏，本轮没有盲目统一减面。

Rockefeller 的两个版本 LOD1 为 47418 三角面，约为主模型 79600 的 59.6%，未达到低于 50% 的优化建议。NeubauerCollegium 主模型最低点 -0.04m，LOD1 最低点 -0.02m，需要核对是否有意嵌地，不直接改高程。

Rockefeller 外包尺寸为 31.09×80.772×63.094m，与官方建筑页 102×265×207 英尺相符。Mansueto 全模型包围盒含连接通道，不能拿完整宽度直接对比穹顶宽度或直接缩放。官方穹顶参考为 73.152×36.576×10.668m；独立穹顶实测分离核对尚未完成。

## 视觉与验收范围

已生成 7 个源文件版本、两个方向、三级 LOD 共 42 张几何检查图；抽查 Bond、Harper、Rockefeller、Mansueto、Regenstein、Saieh 的主/LOD 轮廓，未见明显塌陷。检查图为灰模，不用于证明贴图、玻璃或夜景最终效果。远景几何丢失窗线、装饰等属于精简表现，需结合最终烘焙贴图及切换距离验收。

未完成：全部建筑逐栋多视角艺术精修；全部贴图像素与 OpenGL 法线方向逐张确认；MaskMap 通道逐像素验证；FBX2018 官方管线兼容验收；CS2 编辑器/游戏内导入、LOD 跳变、夜景、雪景、性能和存档测试。原 FBX 有 7400 与 7500 两种格式版本，本轮仅证明 Blender 可读。没有在用户电脑运行游戏，没有发布或推送仓库。

官方参考：
- https://cs2.paradoxwikis.com/Asset_Creation_Guide
- https://www.rockefeller.uchicago.edu/the-spaces/rockefeller-architecture/
- https://www.lib.uchicago.edu/mansueto/tech/numbers/
