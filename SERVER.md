# 服务端汉化包 · 安装说明

[![GitHub](https://img.shields.io/badge/GitHub-chiba233%2Fatmons--zh__cn-181717?logo=github)](https://github.com/chiba233/atmons-zh_cn)
[![Contributing](https://img.shields.io/badge/Contributing-guide-blue.svg)](./CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/Security-policy-red.svg)](./SECURITY.md)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](./LICENSE)

> 适用于 All the Mons @@MCVER@@ **专用服务器**（dedicated server）。**单机玩家不需要本包**——
> 单机时你自己的客户端就兼任逻辑服务端，蜂名迁移脚本已包含在客户端包里。

## 目录

- [兼容版本](#兼容版本)
- [服务端必须单独装的三类文本](#服务端必须单独装的三类文本)
- [包内容](#包内容)
- [安装](#安装)
- [验证](#验证)
- [不包含的内容](#不包含的内容)
- [安全性说明](#安全性说明)

## 兼容版本

| 项 | 版本 |
|---|---|
| 整合包 | All the Mons **v@@MCVER@@** 专用服务器 |
| Minecraft | 1.21.1 |
| 加载器 | NeoForge @@NEOFORGE@@ |

**客户端包与服务端包必须匹配同一版本**，且服务器每个玩家的客户端也要装对应的客户端汉化包。

## 服务端必须单独装的三类文本

有三类文本由**服务端下发给客户端**，客户端单方面安装无法覆盖：

1. **任务书**（量最大）：FTB Quests 的章节名、任务标题 / 副标题 / 描述由服务端下发。
   服务端未安装时，玩家客户端装了也不生效，所有人读到的仍是服务端那一份。
2. **资源蜜蜂的蜂笼 / 实体名**：抓蜂时服务端把蜂名解析成纯字符串烙进物品 NBT。
   `kubejs/server_scripts/pb_hanhua_cage_migrate.js` 会按 NBT 里的真实蜂种 ID，
   把蜂笼名与实体名改写为权威译名（与客户端资源包**同源**）。
   旧蜂笼放入背包数秒后自动完成改写；**玩家用命名牌起的名字不作任何改动**。
3. **RFTools 建造机 / 形状卡的聊天反馈**（「未选择建造机！」等）：由服务端逻辑发送。
   `mods/vaultpatcher.jar` + `vaultpatcher/modules/` 里的 RFTools 定向模块让服务端发出的就是中文。

> **本包不采用「服务端语言注入 mod」。** 那种做法会让服务端**现算**的文本变成中文，
> 而 JEI 与配方（客户端拿英文数据现算）不变，两边名字对不上，玩家照服务器里的名字
> 在 JEI 里搜不到东西。本包只做「按 NBT ID 精确改写纯显示字段」这一件事。

## 包内容

```
mods/vaultpatcher.jar                          # 字节码文本补丁工具（上游原版，未改）
vaultpatcher/modules/*.json                    # 仅 10 个 RFTools/mcjty 类定向模块（清单见 scripts/server_modules.txt）
kubejs/server_scripts/pb_hanhua_cage_migrate.js # 蜂笼/实体显示名按 NBT ID 迁移
config/ftbquests/…                             # 任务书中文（服务端也要，否则任务标题/描述回退英文）
config/vaultpatcher_asm/…                       # VaultPatcher 主配置
请安装前务必看我.md · LICENSE · 项目主页与反馈.url
```

> **关于任务书语言文件。** All the Mons 自带十种语言，**没有中文**。所以
> `config/ftbquests/quests/lang/zh_cn/` 下发的这 57 个章节文件是**整份中文任务书**，
> 不是往整合包自带的中文里打补丁——整合包那边压根没有这一份，覆盖不到任何东西。
>
> 文件名与整合包英文章节同名是有意的：任务书语言按**键**合并，一个键只由一份文件
> 持有，`ftbquestslangsplitter` 的合并顺序就完全不参与决策。这一点很重要，因为它
> 合并同目录下的 `*.snbt` 时**不排序**（`chapters/` 里是 `Files.list(...).forEach(...)`，
> 一个 comparator 都没有），而 `Files.list` 不保证顺序——NTFS/APFS 恰好按名字返回，
> **ext4 返回哈希序**。同一个键要是躺在两份文件里，谁生效在 Linux 服务器上是随机的。
>
> 也因此，本包的 `zh_cn/` 下**没有**任何内容为 `{}` 的空壳文件。

## 安装

1. **先备份**服务器数据目录里的 `config/`、`kubejs/`、`vaultpatcher/`、`mods/vaultpatcher.jar`
   （若已存在）。本包不带自动安装器，请手动备份以便回退。
2. 把本包内的 `mods/` `vaultpatcher/` `kubejs/` `config/` **覆盖**到服务器数据目录
   （含 `mods/`、`server.properties` 的那一层）。
3. **完整重启服务器**（VaultPatcher 在类加载时生效，热重载无效）。

> **只更新任务书文本时可以不重启**：`config/ftbquests/quests/lang/` 下的语言文件
> 覆盖后，执行 `ftbquests reload` 即可让所有在线玩家生效（玩家侧重新打开任务书，
> 或重连一次）。Docker 部署可用：
>
> ```bash
> docker exec <容器名> rcon-cli ftbquests reload
> ```
>
> 在服务端控制台直接执行 `ftbquests reload` 效果相同。VaultPatcher / kubejs 的改动仍需完整重启。

## 验证

- 服务器**能正常启动、无报错**（尤其不应出现 `error creating crop with id null`；若出现，
  说明误把客户端包的 `config/mysticalcustomization` 上了服务器，见下）。
- 进服后：任务书标题 / 描述为中文；建造机未选择时的聊天提示为中文；
  抓到的新蜂 / 放进背包的老蜂笼名字为中文。
- 任务书里提到的物品名，应当与你在 JEI 里搜到的**完全一致**（本包以「任务绑定的
  物品真名」为单一真源做过全量反查对齐）。若发现对不上，请
  [提 Issue](https://github.com/chiba233/atmons-zh_cn/issues) 附任务截图。

## 不包含的内容

⚠️ **神秘农业作物名配置（`config/mysticalcustomization`）是纯客户端的，绝不能上服务器**。
服务器带上改名后的作物配置，会让**所有玩家进服时刷**
`An error occurred creating crop with id null`。
**本服务端包已不含该目录**；亦请确认未从客户端包手动复制该目录上去。

## 安全性说明

服务端只附带**类定向**（target_class 指向具体 GUI/逻辑类）的 VaultPatcher 模块，
清单与准入标准见 `scripts/server_modules.txt`。**全局替换模块**（如客户端的蜂名基因模块）
绝不能装到服务端——会污染 NBT / 注册名导致存档损坏。CI 会拦截对该清单的越界变更。
