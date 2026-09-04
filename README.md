<p align="center">
  <img src="src/pack/pack.png" width="96" height="96"
       alt="All the Mons 汉化补丁资源包图标">
</p>

# All the Mons 汉化补丁

[![GitHub](https://img.shields.io/badge/GitHub-chiba233%2Fatmons--zh__cn-181717?logo=github)](https://github.com/chiba233/atmons-zh_cn)
[![Contributing](https://img.shields.io/badge/Contributing-guide-blue.svg)](./CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/Security-policy-red.svg)](./SECURITY.md)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](./LICENSE)

All the Mons 的简体中文汉化补丁，对应整合包 **1.2.0**。
整理／补译：**星野夢華 (Hoshino Yumeka)**。

> **装这一个就够。** 本包是完整的一份汉化，**不需要**其他汉化当前置——
> 同时装两份会互相覆盖。整合包装好后直接装本包即可。

## 兼容版本

| 整合包版本 | Minecraft | NeoForge |
|---|---|---|
| All the Mons **1.2.0** | 1.21.1 | 21.1.248 |

只做这一个版本。整合包出新版时本包重新核验后另行发布。

## 汉化范围

整合包内 **398 个模组 jar**，其中 200 个命名空间自带官方中文，本包不做重复翻译。
出货 **306 个语言文件、10.8 万余条**，其中 **132 个模组**的游戏内中文完全依赖本包。

| 范围 | 数量 |
|---|---|
| 任务书（FTB Quests） | 9,169 条，覆盖 78 个章节文件 |
| 任务书标题图 | 重绘 204 张（文字烤进 PNG 的那种） |
| 模组导览书 | 15 个模组、813 个条目 |
| 字节码硬编码文本 | 156 个模块 |
| RFTools / XNet 界面 | 重写 24 个 `.gui` |
| 主菜单按钮 | 重绘 10 个（常态 + 高亮共 20 张） |
| 结构名 | 304 个 |

宝可梦、招式、道具、地名、人名一律取**官方中文**（52poke 收录的任天堂译名），不自拟。

各项均有 CI 闸兜底，未通过即无法发布，清单见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 下载哪个包

**客户端请下载文件名含 `client` 的，含 `server` 的是开服的人才需要。**

| 文件（见 [Releases](../../releases)） | 装在哪 | 谁需要 |
|---|---|---|
| `atmons-zh_cn-client-<补丁版本>-mons<整合包版本>.zip` | 你自己电脑上的 All the Mons 实例 | **所有人。** 单人玩家只装这一个 |
| `atmons-zh_cn-server-<补丁版本>-mons<整合包版本>.zip` | 服务器（开服那台机器 / 面板） | 只有**开服的人** |

文件名里 `r1` 是**补丁自己的版本**，`mons1.2.0` 才是**整合包版本**。

⚠️ 不要把客户端包丢到服务器上。

## 客户端安装

### 1. 找到实例文件夹

含 `mods` 文件夹和 `options.txt` 的那一层。CurseForge / Prism / HMCL 里右键实例 →
「打开文件夹」，常见路径形如 `...\.minecraft\versions\All the Mons\`。

### 2. 解压，把**整个文件夹**放进去

```
All the Mons\             ← 实例根目录
├─ mods\
├─ options.txt
└─ atmons-zh_cn-client\   ← 刚放进来的
   ├─ 双击安装-Windows.bat
   ├─ install.sh
   └─ ...
```

放错地方也没关系，安装器会提示你手动输入实例路径。

### 3. 运行安装器，选 [1] 应用汉化

- **Windows**：双击 `双击安装-Windows.bat`
- **macOS / Linux**：在该文件夹里终端运行 `bash install.sh`

原文件会先备份到 `backups/<时间戳>/` 再覆盖。

> 也可以直接把压缩包**内容**解压到实例根目录当场覆盖，汉化一样生效，
> 但原文件在解压那一刻就没了，没有备份可退。

### 4. 确认装上了

进游戏，主菜单按钮应该是中文，任务书的章节名与标题图也应是中文。

> 刚覆盖完就在原来那局里看，任务书可能仍有个别条目是英文。
> **退回标题画面再进一次**，或在游戏里执行 `/ftbquests reload`。这不是漏翻。

### 卸载 / 回退

再运行一次安装器，选 **[3] 恢复备份**。

## 服务端安装

**只有开服的人需要，单人玩家跳过。**

下载 `atmons-zh_cn-server-…` 解压，按包内 `请安装前务必看我.md` 覆盖到服务器目录后
完整重启服务端。详见 [SERVER.md](SERVER.md)。

## 已知限制

- **9 条专有名词保持英文**：PKMNCC、Gootastic、LostMyself、TedXenon、BlueMap。
- **蘑菇与作物的拉丁学名保持拉丁文**（`Tuber melanosporum` 这类）。
- **Borrius 地区译作「波留斯」**，该模组自创的 Alice、Jax、Marlon、Milo、Penny、Zeph
  等 20 余个角色名保持英文——52poke 查不到，同名于官方的两个也不套官方译名。
- **天境模组内置的「物品能力提示」资源包未汉化**（137 条），整合包默认不启用它。

## 参与与反馈

[Issues](https://github.com/chiba233/atmons-zh_cn/issues)。报翻译问题请附**截图**与所在界面——
很多问题是「同一个东西在两个地方叫法不同」，只有截图能看出是哪两处。

想动手改的看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证与致谢

代码 GPL-3.0，译文 CC BY-NC-SA 4.0，**按目录分别适用**。详见 [LICENSE](LICENSE) 与
[LICENSE-GPL-3.0](LICENSE-GPL-3.0)，来源与致谢见 [CREDITS.md](CREDITS.md)。
