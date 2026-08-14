---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME阈值发信器
  icon: extendedae:threshold_level_emitter
categories:
- extended devices
item_ids:
- extendedae:threshold_level_emitter
---

# ME阈值发信器

<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/cable_threshold_level_emitter.snbt"></ImportStructure>
</GameScene>

它的工作方式类似 Reset-Set Latch。当网络中某种物品的数量低于
下阈值时，它会关闭红石信号；当数量高于上阈值时，则会开启红石信号。

例如，将下限设为 100，上限设为 150。

起初网络是空的，因此侦测器不会激活。

当该物品的数量增长并超过 150 时，发射器将发送红石信号。

当数量下降并低于 150 时，发射器仍会继续发送信号。

最后当数量少于 100 时，发射器将会关闭。