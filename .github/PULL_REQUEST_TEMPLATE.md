<!-- 感谢贡献！Thanks for contributing! 一个 PR 只做一件事。Keep the diff focused — one concern per PR. -->

## 改了什么 / What does this change?

<!-- 一两句话说清楚。A short, plain summary. -->

## 为什么 / Why

<!-- 解决的问题，或关联的 issue。The problem it solves, or a linked issue. -->
Closes #

## 怎么验证的 / How was it verified?

- [ ] `python3 scripts/check.py` 通过 / passed
- [ ] 改了安装脚本：`python3 scripts/test_installer.py` 本地通过（CI 会在三系统再跑） / installer test passed locally (CI re-runs it on 3 OSes)
- [ ] 进游戏实测过改动的界面/物品（附截图更好） / verified in-game (screenshot welcome)
- [ ] 纯文档改动，无需验证 / docs-only change

## 检查项 / Checklist

- [ ] 改动范围与标题一致，没夹带无关重构。 / Scope matches the title.
- [ ] **没有翻译任何枚举协议值**（`Ignored` / `Copy` / `Move` 等模式选项，翻了会崩游戏）。 / No enum protocol values translated (they crash the game).
- [ ] 资源包改动改在 `resourcepacks/ATM10汉化包/` 源码目录，**没有提交任何 zip**。 / Resource pack edits go in the source directory; no zips committed.
- [ ] 用户可见改动已更新 `CHANGELOG.md`。 / CHANGELOG.md updated for user-facing changes.
