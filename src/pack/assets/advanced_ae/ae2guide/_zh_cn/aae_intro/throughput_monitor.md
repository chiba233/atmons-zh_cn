---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: ME吞吐量监控器
  icon: advanced_ae:throughput_monitor
categories:
- advanced items
item_ids:
- advanced_ae:throughput_monitor
- advanced_ae:throughput_monitor_configurator
---

# ME吞吐量监控器

<GameScene zoom="8" background="transparent">
<ImportStructure src="../structure/throughput_monitors.snbt"></ImportStructure>
<IsometricCamera yaw="195" pitch="30" />
</GameScene>

吞吐量监视器是监视器的一个子类型。它提供与 <ItemLink id="ae2:storage_monitor" />
相同的功能，并额外增加了吞吐量计量功能。它会追踪单一种物品/流体，并监控其
数量变化，向玩家显示每秒变化量。

它*不*需要频道。

## 按键绑定

*   手持物品右击，或用流体容器双击右击，将监控器设置为该物品/流体。
*   空手右击以清除监控器。
*   空手 Shift+右击以锁定监控器。

## 吞吐量监视器配置器

<ItemImage id="advanced_ae:throughput_monitor_configurator" scale="4"></ItemImage>

吞吐量监控配置器是一种可用于更改显示数据的工具。手持它对监视器右键点击
可在三个选项之间循环切换：

* 每刻物品数
* 每秒物品数
* 每分钟物品数

注意：切换模式后，读数可能需要一些时间才能稳定下来，因此不要相信初始数值！