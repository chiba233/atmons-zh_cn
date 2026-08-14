# 致谢与技术说明

本文件随发布包一起分发，说明**语言文件之外**的改动都动了什么、为什么这么动，以及本包依赖了谁的成果。

## 一、本包不含广告，也不含任何加载器 / 启动器模组

必装的只有一个 jar：`mods/vaultpatcher.jar`（[VaultPatcher](https://modrinth.com/mod/vault-patcher) 1.5.2，
作者 [FengMing3093](https://github.com/3093FengMing/VaultPatcher)，GPL-3.0-only，
字节码文本替换框架，替换表全部在 `vaultpatcher/modules/` 里，明文可查）。
它不入本仓库，构建时按 `src/mods.lock.json` 里记的 sha256 从 Modrinth 现取并校验。
随它分发的许可证正文是 GPL-3.0 原文本身，不含本项目的版权声明——那个 jar 不是本项目的作品。

另有一个**可选**的 jar 单独放在一边：`jecharacters`（[Just Enough Characters](https://github.com/Towdium/JustEnoughCharacters)，MIT），
装了之后 JEI / EMI 的搜索框认拼音。不装不影响任何汉化。

资源包的启用与语言设置由安装器直接改 `options.txt` 完成，不需要任何常驻模组代劳。

## 二、语言文件够不着的三类文本

Minecraft 的 `assets/<模组>/lang/zh_cn.json` 只能翻译**走翻译键**的文本。以下三类走不了语言文件，本包分别用不同手段处理：

### 1. 硬编码在 Java 字节码里的界面文字（VaultPatcher）

有些模组把界面字符串直接写死在 class 里。`vaultpatcher/modules/*.json` 给出「英文原文 → 中文」的替换表，由 VaultPatcher 在类加载时改写常量池。

- 源里 159 个模块，出货 156 个、替换对 2,552 条，以 RFTools 系为主。
  另外 3 个模块只留在源里不出货，其中两个是因为条数太大——这张表每次替换调用都要线性扫一遍，
  出货会全局掉帧。
- **红线**：枚举协议值（如 RedstoneMode 的 `Ignored`/`Off`/`On`）绝不能翻——McJtyLib 按名字反查，翻了直接崩存档。
  blockui 的 `top horizontal` 这类对齐串同理，它按 `contains("horizontal")` 决定行为，译了整个界面的对齐会失效。
  `scripts/check.py` 把这两条都做成了硬检查。

### 2. 写死在 data 包里的导览书正文（Patchouli）

Patchouli 系导览书把正文直接写在 `data/<模组>/patchouli_books/**` 的 JSON 里，不引用翻译键。
本包为此存了 813 份「原文 → 译文」映射，构建时套用。

- 只改显示文本，不动任何游戏逻辑（配方产物、条件、数量一律保持原样）。
- 模组更新新增内容时，新内容会显示英文，需要重新提取。

### 3. 整合包自带的脚本与配置

整合包自己的 `kubejs/**`、`config/**` 是**上游的东西**，本包不存它的副本，只存「找这几行 → 换成这几行」
的定点映射（`src/upstream/`，11 个文件、32 处）。构建时对着目标版本的官方文件套用，上游改了哪一行都会
当场报错，而不是发出一个「旧上游 + 我们的改动」的包把人家的修复覆盖掉。

本包另外注入三个自己的 KubeJS 脚本：资源包生效自检、更新提示，以及资源蜜蜂的 tooltip 汉化。
前两个只在客户端跑，删掉即完全回退。

## 三、翻译来源与致谢

| 来源 | 说明 | 许可 |
|---|---|---|
| **[atm10-zh-cn](https://github.com/chiba233/atm10-zh-cn)** | 本包的语言文件、导览书与任务书译文由该项目迁入。两个整合包同源，共用的部分不重复翻译。 | 同本包 |
| **CFPA 社区翻译**（[Minecraft-Mod-Language-Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package)） | 上述内容中有相当一部分与 CFPA 1.21 语言包一致。感谢 CFPA 团队与众多贡献者。 | **CC BY-NC-SA 4.0**（署名—非商业性使用—相同方式共享） |
| **All the Mods 团队** | 整合包本身，以及它自带的中文（任务书之外，`kubejs/assets/**/lang/zh_cn.json` 也由上游提供）。 | 见整合包 |
| 各模组原作者 | 大量模组自带官方中文，本包直接沿用，不做重复翻译。 | 各自许可 |

本包尚未发布，所以这里不写译文来源的分项占比——那组数字要由构建时的逐条比对得出，
等第一个正式版出来再补。

### 授权

按目录拆开，详见 [LICENSE](LICENSE)：**代码**（脚本与安装器）GPL-3.0-or-later，
**译文内容** CC BY-NC-SA 4.0（署名—非商业性使用—相同方式共享）。
译文的 NC 条款来自 CFPA，不是本项目自行附加的。

## 四、反馈

翻译问题、漏翻、显示异常都请提到 [Issues](https://github.com/chiba233/atmons-zh_cn/issues)，
附截图与所在界面。
