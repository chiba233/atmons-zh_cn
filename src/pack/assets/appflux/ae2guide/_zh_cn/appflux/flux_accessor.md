---
navigation:
  parent: appflux/appflux-index.md
  title: 通量访问点
  icon: appflux:flux_accessor
categories:
- flux accessor
item_ids:
- appflux:flux_accessor
- appflux:part_flux_accessor
---

# 通量访问点

<Row>
<BlockImage id="appflux:flux_accessor" scale="8"></BlockImage>
<GameScene zoom="8" background="transparent">
  <ImportStructure src="../structure/flux_accessor.snbt"></ImportStructure>
</GameScene>
</Row>

通量访问点可以输入/输出存储在你的 ME 网络中的能量。默认情况下，它们没有 I/O 限制，这可以在 
Appflux 配置中更改。

它们有快速模式和普通模式。在快速模式下，它每刻都会输出能量，如果大量使用可能会导致卡顿。
在普通模式下，它会根据目标的储能情况输出能量，因此不会造成卡顿问题。

* 注意：这里提到的“能量”是存储在你的[FE存储元件](./flux_cells.md)中的 FE，而不是[能量单元](ae2:items-blocks-machines/energy_cells.md)中的能量。