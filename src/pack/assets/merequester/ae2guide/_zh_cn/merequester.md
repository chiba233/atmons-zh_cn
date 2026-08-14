---
navigation:
  title: ME请求器
  icon: requester
  position: 100
item_ids:
- merequester:requester
- merequester:requester_terminal
---

# ME请求器

<Row>
  <ItemImage id="requester" scale="3"/>
  <ItemImage id="requester_terminal" scale="3"/>
</Row>

一个附属模组，可让你在 [ME System](ae2:getting-started.md#your-very-first-me-system) 中持续维持物品和流体库存。
<br/>

## 入门

要开始使用，请放置一个 <ItemLink id="requester"/> 并将其连接到你的网络。确保它连接到与你的
[自动合成](ae2:ae2-mechanics/autocrafting.md)逻辑所在相同的网络中。它应承载你的
[合成器CPU](ae2:ae2-mechanics/autocrafting.md#the-crafting-cpu)和 <ItemLink id="ae2:pattern_provider"/>。

<RecipeFor id="requester"/>

为了让 <ItemLink id="requester"/> 正常工作，你需要确保想要维持库存的物品或流体都拥有样板，
并且当你作为玩家请求它们时也确实可以被合成。它只负责自动发起请求本身，合成则由
[ME 系统](ae2:getting-started.md#your-very-first-me-system)处理。
<br/>

<FloatingImage src="assets/gui.png" align="right"/>

## 配置

第一次打开 <ItemLink id="requester"/> 时，你会看到请求设置的总览。单个
方块可容纳的槽位数可在配置中调整。GUI 的每一行都代表一条独立请求。
<br/>

### 切换开关

左侧的复选框用于切换该行所配置的请求是否启用。禁用请求后，将不会执行任何检查，且你的
请求库存也不会被维持。<br/>
这可用于临时禁用某个特定请求，或防止 <ItemLink id="requester"/> 在你仍在修改某一行时发出合成任务。
<br/>

### 要补货的内容

在第二列中，你可以指定想要保持库存的物品。这里的槽位是幽灵槽位，不会存放实际物品。当你将物品拖到槽位上时，可以使用右击将数量设为 1，或使用左键点击将数量设为你当前拖动的那组物品所拥有的数量。
当你将装有流体的桶拖到槽位上时，可以使用右击设置其中包含的流体，或使用左键点击设置桶本身。
你也可以通过 Shift 点击物品来快速设置物品类型。如果你的物品栏中没有想要的物品，也可以从应用能源支持的配方查看器中将其拖放过来。
<br/>

### 补货数量

“储备数量”字段表示要维持多少库存。先指定要储备的内容，然后再输入你想要的数值。对于非物品请求，
该字段会根据类型自动适配。例如，对于流体会显示 `B` 表示桶。<br/>
当当前库存低于指定数量时，<ItemLink id="requester"/> 会请求更多。
<br/>

### 批量大小

下一个输入框用于指定批量大小，也就是当当前库存低于“储备数量”字段中设定的阈值时，
一次会请求多少。<br/>
这可以减轻[合成器CPU](ae2:ae2-mechanics/autocrafting.md#the-crafting-cpu)和参与合成的机器的压力，
因为会一次性请求完整数量，而不是拆成许多个独立任务。
<br/>

### 提交按钮

要将更改应用到该请求，请在“储备数量”和“批量大小”字段中输入所需数值，然后按 Enter，或点击当前行右侧的
提交按钮。点击其他任何一行都会将数值重置为之前的状态。
<br/>

### 状态栏

输入框下方和提交按钮下方的状态条会反映当前请求的状态。
<br clear="all" />
<br/>

## 状态

以下状态会显示在每个请求的状态栏中。
<br/>

### 灰色 - 倒空

当前行已被禁用，或尚未指定要补货的内容。
<br/>

### 绿色 - 空闲中

已达到目标库存数量，或配置的请求没有对应样板。
<br/>

### 红色 - 缺少材料

系统缺少发出当前任务所需的材料。一旦在
系统中找到足够的材料，它就会继续。
<br/>

### 黄色 - 合成

所需请求当前正在合成中。请求器正在等待任务完成。<br/>
当此状态激活时，<ItemLink id="requester"/> 中对应请求的设置会被锁定，无法更改。
<br/>

### 紫色 - 输出

<ItemLink id="requester"/> 已收到当前任务的全部结果，并正尝试将其导出到存储系统中。<br/>
这种状态通常不会持续可见。如果它持续太久，说明你的存储系统空间不足。
<br/>

### 方块外观

如果 <ItemLink id="requester"/> 中的任意请求状态不是空闲或为空，它的外观就会发生变化。

<Row>
  <Column>
    未激活
    <BlockImage id="requester" scale="3" p:active="false"/>
  </Column>
  <Column>
    已激活
    <BlockImage id="requester" scale="3" p:active="true"/>
  </Column>
</Row>
<br/>

## 终端

该模组还提供了一种名为 <ItemLink id="requester_terminal"/> 的新终端。它允许你在一个中心位置访问同一网络中的所有 <ItemLink id="requester"/>。


该终端具有与 <ItemLink id="ae2:pattern_access_terminal"/> 相同的功能，并允许你搜索特定请求。
由于所有 <ItemLink id="requester"/> 默认名称都相同，所有请求都会被归类到
同一个标题下。如果你希望在 <ItemLink id="requester_terminal"/> 中将 <ItemLink id="requester"/> 分成不同分组，
可以在铁砧中重命名它们，或使用 <ItemLink id="ae2:name_press"/>。