# 服务端汉化包 · 安装说明

[![GitHub](https://img.shields.io/badge/GitHub-chiba233%2Fatmons--zh__cn-181717?logo=github)](https://github.com/chiba233/atmons-zh_cn)
[![Contributing](https://img.shields.io/badge/Contributing-guide-blue.svg)](./CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/Security-policy-red.svg)](./SECURITY.md)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](./LICENSE)

> 适用于 All the Mons @@MCVER@@ **专用服务器**（dedicated server）。
> **单机玩家不需要本包**，客户端包里已经包含所需内容。

## 兼容版本

| 项 | 版本 |
|---|---|
| 整合包 | All the Mons **v@@MCVER@@** 专用服务器 |
| Minecraft | 1.21.1 |
| 加载器 | NeoForge @@NEOFORGE@@ |

**客户端包与服务端包必须是同一版本**，且服务器上每个玩家也要装对应的客户端汉化包。

## 包内容

```
mods/vaultpatcher.jar                           # 字节码文本补丁工具（上游原版，未改）
vaultpatcher/modules/*.json                     # 10 个 RFTools/mcjty 类定向模块
kubejs/server_scripts/pb_hanhua_cage_migrate.js # 蜂笼 / 实体显示名迁移
config/ftbquests/…                              # 任务书中文
config/vaultpatcher_asm/…                       # VaultPatcher 主配置
请安装前务必看我.md · LICENSE · 项目主页与反馈.url
```

⚠️ `config/ftbquests/quests/lang/zh_cn/` 是**整份替换**同名文件，不是往里加文件。

## 安装

1. **先备份**服务器数据目录里的 `config/`、`kubejs/`、`vaultpatcher/`、
   `mods/vaultpatcher.jar`（若已存在）。本包不带安装器，请手动备份以便回退。
2. 把本包内的 `mods/` `vaultpatcher/` `kubejs/` `config/` **覆盖**到服务器数据目录
   （含 `mods/`、`server.properties` 的那一层）。
3. **完整重启服务器。**

> **之后只更新任务书文本可以不重启**：覆盖 `config/ftbquests/quests/lang/` 后执行
> `ftbquests reload`，玩家重开任务书或重连一次即可生效。Docker 部署用
> `docker exec <容器名> rcon-cli ftbquests reload`。
> VaultPatcher / kubejs 的改动仍需完整重启。

## 验证

- 服务器能正常启动、无报错。
- 进服后：任务书标题 / 描述为中文；建造机未选择时的聊天提示为中文；
  新抓的蜂与放进背包的老蜂笼名字为中文。
- 任务书里提到的物品名，与你在 JEI 里搜到的**完全一致**。对不上请
  [提 Issue](https://github.com/chiba233/atmons-zh_cn/issues) 附任务截图。

## 两条红线

⚠️ **不要把客户端包的 `config/mysticalcustomization` 放到服务器上。** 会让所有玩家进服时刷
`An error occurred creating crop with id null`。本服务端包已不含该目录，请确认没有手动复制过去。

⚠️ **不要往服务端加全局替换的 VaultPatcher 模块**（如客户端的蜂名基因模块），会污染
NBT / 注册名导致存档损坏。服务端只收类定向模块，清单见 `scripts/server_modules.txt`，
CI 会拦截对该清单的越界变更。
