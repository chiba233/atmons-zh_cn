---
navigation:
  parent: aae_intro/aae_intro-index.md
  title: 量子计算机
  icon: advanced_ae:quantum_core
categories:
- advanced devices
item_ids:
- advanced_ae:quantum_unit
- advanced_ae:quantum_core
- advanced_ae:quantum_structure
- advanced_ae:quantum_accelerator
- advanced_ae:quantum_multi_threader
- advanced_ae:quantum_storage_128
- advanced_ae:quantum_storage_256
- advanced_ae:data_entangler
---

# 量子计算机

量子计算机是一种特殊的合成计算机。只要拥有足够的合成存储，
它就能够运行无限数量的合成请求。

<GameScene zoom="2" background="transparent">
  <ImportStructure src="../structure/quantum_computer_multiblock.snbt"></ImportStructure>
</GameScene>

## 量子核心

<BlockImage id="advanced_ae:quantum_core" p:powered="true" p:formed="true" scale="4"></BlockImage>

量子核心是量子计算机的核心。它自身拥有 256M 合成存储和 8 条协处理器线程。
它是唯一一个可以单独形成量子计算机并提供量子计算机全部优势的方块。
不过，如果用于构建多方块结构，就能创建更强大的计算机。作为独立计算机使用时，
必须从带有连接器的上侧或下侧输入电力。

## 量子存储

<Row gap="20">
<BlockImage id="advanced_ae:quantum_storage_128" scale="4"></BlockImage>
<BlockImage id="advanced_ae:quantum_storage_256" scale="4"></BlockImage>
</Row>

这些方块可扩展量子核心的合成存储。它们实际上提升了
量子计算机可同时运行的任务数量。共有两种版本，容量分别为 128M 和 256M。

## 量子数据纠缠器

<BlockImage id="advanced_ae:data_entangler" scale="4"></BlockImage>

数据纠缠器是一种特殊方块，会影响多方块结构中存在的所有存储方块。它们使存储
方块能够在多个维度中存储数据，实际上将其存储容量提升为 4 倍。每个量子计算机多方块结构中
只能放置一个。

## 量子加速器

<BlockImage id="advanced_ae:quantum_accelerator" scale="4"></BlockImage>

量子加速器会为量子计算机多方块结构增加 8 个协处理器。需要注意的是，所有由量子计算机
运行的合成样板都能够共享这些协处理器，因此投入大量这类部件通常是个不错的选择。

## 量子多线程处理器

<BlockImage id="advanced_ae:quantum_multi_threader" scale="4"></BlockImage>

与数据纠缠器类似，多线程处理器可让加速器在独立维度中运行额外线程，
使其协处理能力提升为 4 倍。每个量子计算机多方块结构中只能放置一个。

## 量子结构

<Row gap="20">
<BlockImage id="advanced_ae:quantum_structure" scale="4"></BlockImage>
<BlockImage id="advanced_ae:quantum_structure" p:formed="true" p:powered="true" scale="4"></BlockImage>
</Row>

这些方块构成了量子计算机的框架。它们用作量子计算机的构建方块，
并将所有部分连接在一起。

## 多方块结构

要创建一个多方块量子计算机，必须遵守一些规则：
- 最大尺寸为 7x7x7（外部尺寸）；
- 多方块结构内部不能有空隙。可以用 <ItemLink id="advanced_ae:quantum_unit" />
填充，但不会带来额外收益；
- 恰好一个 <ItemLink id="advanced_ae:quantum_core" />；
- 最多一个 <ItemLink id="advanced_ae:data_entangler" />；
- 最多一个 <ItemLink id="advanced_ae:quantum_multi_threader" />；
- 外层上的所有方块都必须是 <ItemLink id="advanced_ae:quantum_structure" />；
- 内部不能有任何方块是 <ItemLink id="advanced_ae:quantum_structure" />。

## 服务器配置

有多个数值可以通过服务器配置进行调整，例如：
- 多方块结构的最大尺寸；
- 每个量子加速器中的协处理器数量；
- 量子多线程处理器的最大数量；
- 多线程处理器的线程倍率；
- 数据纠缠器的最大数量；
- 数据纠缠器的存储倍率；

你当前实例的限制可以通过物品的工具提示查看。