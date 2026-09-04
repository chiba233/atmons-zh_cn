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

> **装这一个就够。** 语言文件 10.8 万余条、任务书 9,169 条、15 本模组手册、
> 304 条结构名、204 张任务书标题图都在里面，是完整的一份，不是叠加在别家之上的补充包。
> **不需要**先装其他汉化当前置——同时装两份会互相覆盖。整合包装好后直接装本包即可。
>
> 宝可梦、招式、道具、地名、人名一律取**官方中文**（52poke 收录的任天堂译名），不自拟。

## 兼容版本

| 整合包版本 | Minecraft | NeoForge |
|---|---|---|
| All the Mons **1.2.0** | 1.21.1 | 21.1.248 |

**只做这一个版本，不能跨版本用。** 整合包出新版时本包重新核验后另行发布。

## 我该下载哪个包？

[Releases](../../releases) 里有两个文件：

| 文件 | 装在哪 | 谁需要 |
|---|---|---|
| `atmons-zh_cn-**client**-<补丁版本>-mons<整合包版本>.zip` | 你自己电脑上的 All the Mons 实例 | **所有人都要装。** 单人玩家只装这一个 |
| `atmons-zh_cn-**server**-<补丁版本>-mons<整合包版本>.zip` | 服务器那台机器 | 只有**开服的人**要装 |

文件名里有两个版本号：`r1` 是**补丁的版本**，`mons1.2.0` 才是**你的整合包版本**。认后者下载。

**单人玩家只装客户端包**——单人时你的客户端兼任服务端。

⚠️ **别把客户端包丢到服务器上。**

## 客户端安装

### 1. 找到实例文件夹

含 `mods` 文件夹和 `options.txt` 的那一层。启动器里右键实例 →「打开文件夹」。
路径通常长这样：`...\.minecraft\versions\All the Mons\`

### 2. 解压，把整个文件夹放进去

解压后得到一个 `atmons-zh_cn-client` 文件夹，**整个拖进实例目录**：

```
All the Mons\             ← 实例根目录
├─ mods\
├─ options.txt
└─ atmons-zh_cn-client\   ← 刚放进来的
   ├─ 双击安装-Windows.bat
   ├─ install.sh
   └─ ...
```

放错地方也没关系，安装器会提示你手动输入路径。

> ⚠️ **尽量不要把压缩包内容直接解压覆盖到实例根目录**。那样虽然也能用，但**没有任何备份**，之后无法一键回退。

### 3. 运行安装器

- **Windows**：双击 `双击安装-Windows.bat`
- **macOS / Linux**：终端里 `bash install.sh`

选 **[1] 应用汉化**。它会把将被覆盖的原文件备份到 `backups/<时间戳>/`，再复制汉化文件并启用资源包。

### 4. 确认装上了

进游戏，主菜单按钮应该是中文，任务书的章节名与标题图也应是中文。

> 刚覆盖完就在原来那局里看，任务书可能仍有个别条目是英文。**退回标题画面再进一次**，
> 或在游戏里执行 `/ftbquests reload`。这不是漏翻。

### 卸载 / 回退

再运行一次安装器，选 **[3] 恢复备份**，回到安装前的状态。

## 服务端安装

**只有开服的人需要。单人玩家跳过。**

下载 `...-server-...zip`，把包内的 `mods/` `vaultpatcher/` `kubejs/` `config/` 覆盖到服务器数据目录，然后**完整重启服务端**。详见 [SERVER.md](SERVER.md)。

装完后玩家仍需各自安装客户端包——服务器管不了你屏幕上的物品名。

## 仍是英文的部分

- **9 条专有名词**：画作署名 PKMNCC / Gootastic、模型作者 LostMyself / TedXenon、地图模组名 BlueMap。
- **蘑菇与作物的拉丁学名**（`Tuber melanosporum` 这类）——那是学名，不是描述。
- **Borrius 阵营的自创角色名**：Alice、Jax、Marlon、Milo、Penny、Zeph 等 20 余个，52poke 查不到。地区名 Borrius 自主译作「波留斯」。
- **天境模组内置的「物品能力提示」资源包**（137 条）——整合包默认没启用它，装不装本包都不显示。

发现漏翻 / 错译请[提 Issue](https://github.com/chiba233/atmons-zh_cn/issues)，附截图与位置。

## 参与与反馈

- 汉化问题（漏翻 / 错译 / 崩溃）→ [Issues](https://github.com/chiba233/atmons-zh_cn/issues)，请附**截图**与所在界面
- 想改译名或贡献翻译、了解仓库结构与构建流程 → [CONTRIBUTING.md](CONTRIBUTING.md)
- 安全问题 → [SECURITY.md](SECURITY.md)

## 许可证与致谢

代码 GPL-3.0，译文 CC BY-NC-SA 4.0，**按目录分别适用**，详见 [LICENSE](LICENSE) 与 [LICENSE-GPL-3.0](LICENSE-GPL-3.0)。

整理／补译：**星野夢華 (Hoshino Yumeka)**。来源与致谢见 [CREDITS.md](CREDITS.md)。
