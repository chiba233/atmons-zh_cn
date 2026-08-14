#!/usr/bin/env bash
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# 取任务书横幅生成脚本要用的点阵中文字体。
#
# 字体本身不入 git（十来 MB，而生成好的 PNG 已经在仓库里，玩家和 CI 都不需要它），
# 只有要重跑 scripts/gen_quest_banners.py 时才需要跑这个。版本号写死，
# 保证同一份脚本任何时候跑出来的图都一样。
#
# 字体：缝合像素字体 Fusion Pixel Font（OFL-1.1），TakWolf 出品，
# 由方舟像素字体 + Cubic 11 + Galmuri 拼合补全覆盖，随包 OFL 一并下载。
# 选它而不是方舟本体，是因为方舟 zh_cn 12px 缺「旋热然聚嗡蟒骏」这类常用字，
# 缺字会渲染成 .notdef 豆腐块。
set -euo pipefail

VER=2026.07.20
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/assets-src/fonts"
BASE="https://github.com/TakWolf/fusion-pixel-font/releases/download/${VER}"

mkdir -p "$DIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# GitHub 的 release CDN 会偶发把连接掐断（curl 35 Recv failure: Connection reset
# by peer），2026-08-10 的 Build 就这么红过一次，而且红在第一个字体上。
# 不带重试的话，一次网络抖动就要人手动重跑整条流水线。
#
# 重试不会放坏字节进来：下完还要过 toolchain.py --fonts 逐个核哈希，
# 半截文件或换了版本的字体在那一步必红。
dl() {
    curl -fsSL --retry 5 --retry-delay 2 --retry-all-errors -o "$1" "$2"
}

for px in 10 12; do
    f="fusion-pixel-font-${px}px-proportional-ttf-v${VER}.zip"
    echo "下载 ${f} ..."
    dl "$TMP/$f" "$BASE/$f"
    unzip -o -q "$TMP/$f" -d "$TMP/x$px"
    cp "$TMP/x$px/fusion-pixel-${px}px-proportional-zh_hans.ttf" "$DIR/pixel-${px}.ttf"
done
cp "$TMP/x12/OFL.txt" "$DIR/pixel-OFL.txt"
rm -rf "$DIR/pixel-LICENSES"
cp -R "$TMP/x12/LICENSES" "$DIR/pixel-LICENSES"

# ---- 矢量三档：思源黑体 / 思源宋体（Noto CJK，OFL-1.1）
# 原先这三档直接用 macOS 自带的冬青黑与宋体，结果只有 Mac 能生成图，
# CI 跑不了。换成 OFL 的近似字体后 Linux 上的产出与本机像素级基本一致
# （200 张横幅 197 张完全相同，3 张因 freetype 版本差异有细微栅格化区别，目视等价）。
#   bold  ← 思源黑体 Bold   （原冬青黑 W6）
#   thin  ← 思源黑体 Light  （原冬青黑 W3）
#   serif ← 思源宋体 Black  （原宋体 SC Black）
echo "下载 思源黑体 SC ..."
dl "$TMP/sans.zip" \
  "https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/18_NotoSansSC.zip"
unzip -o -q "$TMP/sans.zip" -d "$TMP/sans"
cp "$TMP/sans/NotoSansSC-Bold.otf"  "$DIR/bold.otf"
cp "$TMP/sans/NotoSansSC-Light.otf" "$DIR/thin.otf"
cp "$TMP/sans/LICENSE" "$DIR/noto-OFL.txt"

echo "下载 思源宋体 SC ..."
dl "$TMP/serif.zip" \
  "https://github.com/notofonts/noto-cjk/releases/download/Serif2.003/14_NotoSerifSC.zip"
unzip -o -q -j "$TMP/serif.zip" 'SubsetOTF/SC/NotoSerifSC-Black.otf' -d "$TMP"
cp "$TMP/NotoSerifSC-Black.otf" "$DIR/serif.otf"

# 下完必须核哈希：字形栅格化直接决定 PNG 的每一个像素，
# 上游哪天重传一版字体，图会**悄悄**变，而产物哈希对不上时根本看不出是这里出的问题。
echo "核对字体哈希 ..."
python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/toolchain.py" --fonts

echo "完成："
ls -1 "$DIR"
