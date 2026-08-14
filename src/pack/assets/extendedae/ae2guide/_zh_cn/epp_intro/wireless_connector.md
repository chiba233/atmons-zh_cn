---
navigation:
  parent: epp_intro/epp_intro-index.md
  title: ME无线连接器
  icon: extendedae:wireless_connect
categories:
- extended devices
item_ids:
- extendedae:wireless_connect
- extendedae:wireless_tool
---

# ME无线连接器

<Row gap="20">
<BlockImage id="extendedae:wireless_connect" scale="6"></BlockImage>
<ItemImage id="extendedae:wireless_tool" scale="6"></ItemImage>
</Row>

ME无线连接器 可以像 <ItemLink id="ae2:quantum_link" /> 一样连接两个网络，但距离有限，且不能
跨维度。ME无线连接器 仅支持一对一连接，如果你想进行多对多连接，
则需要使用 <ItemLink id="extendedae:wireless_hub" />。

## 连接无线连接器

使用 ME 无线配置套件点击你想要连接的两个无线连接器，然后你就可以将它们连接起来。

潜行 + 点击可清除 ME Wireless Setup Kit 的当前设置。

当成功建立连接后，ME无线连接器会改变其纹理。

未连接的 ME无线连接器

<GameScene zoom="5" background="transparent">
  <ImportStructure src="../structure/wireless_connector_off.snbt"></ImportStructure>
</GameScene>

已连接的 ME无线连接器

<GameScene zoom="5" background="transparent">
  <ImportStructure src="../structure/wireless_connector_on.snbt"></ImportStructure>
</GameScene>

## 颜色

无线连接器和线缆一样可以染色，并且只会连接与其颜色相同的线缆/连接器。

你需要一个 <ItemLink id="ae2:color_applicator" /> 来给连接器染色。

因此你可以这样设置你的无线连接器：

<GameScene zoom="3" background="transparent" interactive={true}>
  <ImportStructure src="../structure/wireless_connector_setup.snbt"></ImportStructure>
</GameScene>

## 功耗

ME无线连接器相距越远，耗能越高。它的耗能 - 距离曲线并不是线性的，因此当它们相距过远时，
功耗会变得非常高。

你可以使用 <ItemLink id="ae2:energy_card" /> 来节省能量，每张卡都可以降低 10% 的能耗。