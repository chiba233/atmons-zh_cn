---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME标签存储总线
  icon: extendedae:tag_storage_bus
categories:
- extended devices
item_ids:
- extendedae:tag_storage_bus
---

# ME标签存储总线

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_tag_storage_bus.snbt"></ImportStructure>
</GameScene>

ME标签存储总线是一种 <ItemLink id="ae2:storage_bus" />，可按物品标签或流体标签进行筛选，并支持一些基础逻辑运算符。

以下是一些示例：

- 只接受原矿

c:原始材料/*

- 接受所有锭和宝石

c:锭/* | c:宝石/*