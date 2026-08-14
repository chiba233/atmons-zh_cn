---
navigation:
  parent: ae2wtlib/ae2wtlib-index.md
  title: AE2WTLib无线终端
  icon: ae2wtlib:wireless_universal_terminal
  position: 10
categories:
- ae2wtlib
item_ids:
- ae2wtlib:wireless_pattern_encoding_terminal
- ae2wtlib:wireless_pattern_access_terminal
---

# 无线终端

<ItemGrid>
  <ItemIcon id="ae2wtlib:wireless_universal_terminal" />
  <ItemIcon id="ae2:wireless_crafting_terminal" />
  <ItemIcon id="ae2wtlib:wireless_pattern_encoding_terminal" />
  <ItemIcon id="ae2wtlib:wireless_pattern_access_terminal" />
</ItemGrid>

除了 <ItemLink id="ae2:energy_card" /> 之外，所有 AE2WTLib 无线终端都可以用 <ItemLink id="ae2wtlib:quantum_bridge_card" />
进行升级，并组合成一个 <ItemLink id="ae2wtlib:wireless_universal_terminal" />。

和 AE2 的 <ItemLink id="ae2:wireless_terminal" /> 一样，它可以通过按键绑定访问，也可以放入饰品栏中
（如果安装了任意实现 curio api 的模组）。

无线终端也可以像普通的 <ItemLink id="ae2:wireless_terminal" /> 一样，使用 <ItemLink id="ae2:wireless_access_point" /> 进行绑定

## 无线通用终端

<ItemImage id="ae2wtlib:wireless_universal_terminal" scale="3" />

<ItemLink id="ae2wtlib:wireless_universal_terminal" /> 是将多个无线终端组合成一个物品的产物。

## 无线合成终端

<ItemImage id="ae2:wireless_crafting_terminal" scale="3" />

<ItemLink id="ae2:wireless_crafting_terminal" /> 是合成终端的无线版本。
与原版 AE2 相比，它具有一些[额外功能](wireless_crafting_terminal.md)。

## 无线样板编码终端

<ItemImage id="ae2wtlib:wireless_pattern_encoding_terminal" scale="3" />

<ItemLink id="ae2:pattern_encoding_terminal" /> 的无线版本

<RecipeFor id="ae2wtlib:wireless_pattern_encoding_terminal" />

## 无线样板管理终端

<ItemImage id="ae2wtlib:wireless_pattern_access_terminal" scale="3" />

<ItemLink id="ae2:pattern_access_terminal" /> 的无线版本

<RecipeFor id="ae2wtlib:wireless_pattern_access_terminal" />

## 附加终端

其他附属模组中的大多数无线终端也能与 <ItemLink id="ae2wtlib:wireless_universal_terminal" /> 配合使用。

## 无法在通用终端中使用的终端

<ItemLink id="ae2:wireless_terminal" /> 不能在 <ItemLink id="ae2wtlib:wireless_universal_terminal" /> 中使用，
因为与 <ItemLink id="ae2:wireless_crafting_terminal" /> 相比，它不会带来任何好处。
它也无法使用 <ItemLink id="ae2wtlib:quantum_bridge_card" />