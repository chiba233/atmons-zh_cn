---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: 高级IO总线
  icon: advanced_ae:advanced_io_bus_part
categories:
- advanced items
item_ids:
- advanced_ae:advanced_io_bus_part
---

# 高级IO总线

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_advanced_io_bus.snbt"></ImportStructure>
</GameScene>

高级IO总线是与外部容器交互的强大工具。它由
一个 <ItemLink id="advanced_ae:import_export_bus_part"/> 和一个 <ItemLink id="advanced_ae:stock_export_bus_part"/> 融合而成，继承了
两者的功能。此外，高级IO总线的基础速度是 <ItemLink id="ae2:export_bus"/> 基础速度的 8 倍。虽然它需要一些时间来逐步提速，但在完全升级后会快得惊人。

## 输出

高级IO总线会根据过滤器导出内容，直到达到设定的固定数量后停止。在 UI 左侧
还有一项配置，允许用户选择是否调节物品库存。

## 导入

高级IO总线还会导入所有未被过滤为导出的内容。导入和导出操作
是分别计算的，因此总线不会卡在只执行其中一种操作上。当总线被配置为调节模式时，它会
优先导入所有超过设定数量的内容。如果还有剩余操作次数，则会导入未被过滤的内容。

<RecipeFor id="advanced_ae:advanced_io_bus_part"/>