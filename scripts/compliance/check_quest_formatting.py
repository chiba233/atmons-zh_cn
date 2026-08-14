#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh_cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""任务书里的 `&` 颜色码必须合法——不合法整段描述会被红字报错顶掉。

## 事故

玩家报「遗物」那条任务显示成

    Invalid formatting! Unknown formatting symbol after &: 'M'!

整段描述没了，只剩这行红字。根因在整合包**自带的中文**里：

    quest.692183ACBB2AABF7.quest_desc: ["遗物是在你的&2&Minecraft&r世界中…"]
                                                    ↑↑ &2 合法，紧跟的 &M 不是

英文原文是 `&2&lMinecraft&r`，翻译时把颜色码的 `l` 吃掉了。同一形状扫出来一共 5 处
（难得素护甲标题、开裂石头标题、遗物描述、高级磁盘外壳描述、木头之歌的译者注），
全部在整合包自带中文里，全部靠 zz_hanhua_*.snbt 覆盖修掉。

## 合法的写法有哪些

从 ftb-library 的 `dev/ftb/mods/ftblibrary/util/TextComponentParser` 字节码里读的：

  - `CODE_TO_FORMATTING`   0-9 a-f k l m n o r   （22 条，就是原版 ChatFormatting）
  - `SPECIAL_COLOR_CODES`  z                     （彩虹色，FTB 自己加的）
  - `&#RRGGBB`             走 TextColor.parseColor
  - `\\&`                   转义成字面量的 &（报错文案里写明的写法）

其余一律报错。这份集合硬写在下面：ftb-library 每个整合包版本都不同（2101.1.31 /
.32 / .33），钉单一哈希没意义。将来 FTB 真加了新码，这里会**误报**——那是安全的
方向：误报会被人查，漏报会把坏掉的任务发出去。

## 判据：跟英文原文比，不是绝对合法性

只有「英文原文这条是好的、中文这条坏了」才算数——那才是翻译过程弄坏的。中英文
一模一样的（比如 industrial_foregoing 里 URL 的 `?si=…&t=427`）是上游自己的写法，
不该由我们背，也不该每次构建都红。

用法:
    python3 scripts/compliance/check_quest_formatting.py <整合包根目录或 overrides 目录>
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DELTA = ROOT / 'src' / 'config' / 'ftbquests' / 'quests' / 'lang' / 'zh_cn'
REL = 'config/ftbquests/quests/lang'

CODES = set('0123456789abcdefklmnorz')
HEX = re.compile(r'^#[0-9a-fA-F]{6}')
KEY = re.compile(r'^\s*([A-Za-z0-9_.]+)\s*:')


def bad_in(s):
    """s 是 snbt 文件里的**原始**一行，返回其中所有非法的 & 用法。"""
    out, i = [], 0
    while i < len(s):
        if s.startswith('\\\\&', i):          # 文件里的 \\& = 转义过的字面 &
            i += 3
            continue
        if s[i] == '\\':
            i += 2
            continue
        if s[i] == '&':
            r = s[i + 1:]
            if not r:
                out.append('(行尾)')
            elif HEX.match(r):
                i += 8
                continue
            elif r[0] in CODES:
                i += 2
                continue
            else:
                out.append(r[0])
            i += 1
            continue
        i += 1
    return out


def entries(path):
    """{键: [该键名下的原始行…]}。多行 [ ] 块里的行都算在同一个键上。"""
    out, cur = {}, None
    for line in path.read_text(encoding='utf-8').splitlines():
        m = KEY.match(line)
        if m:
            cur = m.group(1)
        if cur:
            out.setdefault(cur, []).append(line)
        if line.strip() in (']', '}'):
            cur = None
    return out


def collect(d):
    """某种语言下的全部键。

    两处都要覆盖，漏一处就是静默少查：

    - **顶层与 chapters/ 都要收**。上游 en_us 下有 5 个顶层 .snbt（chapter /
      chapter_group / file / reward / reward_table）外加 chapters/ 里 75 个；
      我们这边顶层也有 chapter.snbt 与 reward_table.snbt 共 106 条。原先只扫
      chapters/，这 106 条一次都没查过。
    - **.snbt 与 .snbt_merged 都要认**。ftbquestslangsplitter 进过一次游戏后会把
      xxx.snbt 改名成 xxx.snbt_merged，所以拿装好的实例当输入时上游全是后一种；
      只 glob *.snbt 的话 en 会收成空表，「英文原文本来就这么写」那条豁免就静默
      失效（CI 取的是没进过游戏的 overrides 树，是前一种，所以只在本机翻车）。
    """
    all_ = {}
    for p in sorted(list(d.glob('*.snbt*')) + list((d / 'chapters').glob('*.snbt*'))):
        for k, lines in entries(p).items():
            all_.setdefault(k, (p.name, []))[1].extend(lines)
    return all_


def main(argv):
    root = Path(argv[0]) if argv else Path(os.environ.get('ATM_PACK_ROOT', ''))
    base = root / REL
    # 判据挂在 **en_us** 上，不挂在 zh_cn 上。
    #
    # 本包所在的整合包自带十种语言、没有 zh_cn，我们的中文就是整份任务书。原先
    # 这里要求上游有 zh_cn/chapters，于是整条检查退 0 走人——而**最需要查 & 的
    # 恰恰是我们自己那 7000 多条**，一次都没跑过。这是 fail-open，最难发现的那种。
    #
    # en_us 是任何一个整合包都必然有的，拿它当「包取到了没有」的判据：缺了就红，
    # 不看 GATE_STRICT。上游没有 zh_cn 只是 zh 为空，我们那份照查不误。
    if not (base / 'en_us').is_dir():
        print('❌ 任务书格式码检查没跑成：没有整合包的英文任务书目录 %s\n'
              '   多半是整合包没取到或路径写错（给个整合包目录或设 ATM_PACK_ROOT）。'
              % (base / 'en_us'))
        return 1

    up_zh = base / 'zh_cn'
    zh = collect(up_zh) if up_zh.is_dir() else {}
    en = collect(base / 'en_us')
    ours = collect(DELTA)
    if not ours:
        print('❌ 任务书格式码检查没跑成：%s 下一个 .snbt 都没有' % DELTA)
        return 1

    bad = []
    for key, (src, lines) in sorted(zh.items()):
        # 我们盖过的以我们的为准
        src, lines = ours.get(key, (src, lines))
        got = [c for ln in lines for c in bad_in(ln)]
        if not got:
            continue
        # 英文同一条也这么写 = 上游本来就这样，不是翻译弄坏的
        en_bad = [c for ln in en.get(key, ('', []))[1] for c in bad_in(ln)]
        if set(got) <= set(en_bad):
            continue
        bad.append((src, key, got, ' '.join(x.strip() for x in lines)[:150]))

    # 上游中文里没有的键也要查。**同样要拿英文原文豁免**——判据是「英文这条是好的、
    # 中文这条坏了」，跟上面那个循环一模一样。
    #
    # 原先这里漏了这层豁免。上游自带 zh_cn 时它藏得住：绝大多数键都走上面那个循环，
    # 这里只剩零星几个。而本包所在的整合包没有 zh_cn，**所有**键都从这里过，
    # 于是 industrial_foregoing 那条 YouTube 链接里的 `?si=…&t=427` 当场变成
    # 「非法 &t」——那串是上游自己写的，中英文一字不差，不该由我们背。
    for key, (src, lines) in sorted(ours.items()):
        if key in zh:
            continue
        got = [c for ln in lines for c in bad_in(ln)]
        if not got:
            continue
        en_bad = [c for ln in en.get(key, ('', []))[1] for c in bad_in(ln)]
        if set(got) <= set(en_bad):
            continue
        bad.append((src, key, got, ' '.join(x.strip() for x in lines)[:150]))

    if not bad:
        print('✅ 任务书格式码：%d 个键逐条查过，没有会被 FTB 顶成红字报错的 &'
          % len(set(zh) | set(ours)))
        return 0

    print('\n❌ 这些任务的 & 用法不合法，进游戏整段描述会被红字报错顶掉（%d 处）：\n' % len(bad))
    for src, key, got, text in bad:
        print('  %s  %s' % (src, key))
        print('     非法：%s' % '、'.join('&' + c for c in got))
        print('     %s' % text)
    print('\n合法的只有：&0-9 &a-f &k &l &m &n &o &r &z &#RRGGBB，字面量的 & 要写成 \\&。')
    print('本包的中文任务书就是 src/config/ftbquests/quests/lang/zh_cn/ 那份，直接改那一条。')
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
