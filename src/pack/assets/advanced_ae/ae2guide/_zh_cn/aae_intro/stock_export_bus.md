---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: 库存输出总线
  icon: advanced_ae:stock_export_bus_part
categories:
- advanced items
item_ids:
- advanced_ae:stock_export_bus_part
---

# 库存输出总线

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_stock_export_bus.snbt"></ImportStructure>
</GameScene>

库存输出总线可配置为精确导出过滤物品堆的指定数量。它会追踪目标容器中
当前已有的数量，并且不会插入超过该数字的内容。配置方式是：打开 GUI，将
目标物品拖入过滤槽，然后通过中键点击来设置数量。注意，它不会调节输出，
这意味着如果容器中的物品/流体超过设定数量，它不会把多余的部分提取出来。