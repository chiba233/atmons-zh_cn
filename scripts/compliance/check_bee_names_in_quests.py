#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""任务书里提到某只蜜蜂时，用的必须是玩家在 JEI 里搜得到的那个名字。

## 为什么要这道闸

2026-08-02 玩家截图：任务正文写「倒在**幽灵蜜蜂**蛋上」，而 JEI 里那个物品叫
**恶魂蜜蜂**。照着任务书搜是搜不到的——这比漏翻难受得多，漏翻至少能拿英文去搜。

顺着同一条线索机械地扫了一遍，同类的还有：正文里直接留着 `BeeBee`、`KamikazBee`
两个英文原名（物品名是「蜂蜂」「“神风特攻队”蜜蜂」），以及英文的
`Ghostly Bee or Shroombees` 在中文里把 Shroombees 整个漏掉了。
**一次报告 = 一个表面，剩下三个是扫出来的。** 所以这件事不能靠人眼。

## 判定

对每个任务条目：英文原文里出现某只蜜蜂的英文名 → 我们的中文里必须出现它的中文名。

英文名取自 productivebees 的 `en_us.json`，中文名取自本包资源包的 `zh_cn.json`
（同一个键，所以是一一对应，不靠猜）。

**蜜脾、蜜脾块、刷怪蛋的名字是拿蜂名现拼的，也得一起判。** 2026-08-03 玩家截图：
任务标题写「凋亡蜜脾块」，而游戏里那个方块叫「凋灵蜜蜂蜜脾块」。这类名字在 lang 里
根本没有独立的键，扫静态键表永远扫不到它们。

拼法是从 `CombBlockItem` / `Honeycomb` 的字节码里读出来的，不是猜的：
取 `entity.productivebees.<type>_bee` 的**本地化**名字，删掉字面量 `" Bee"`，
再填进 `%s Comb Block` / `%s蜜脾块` 这类模板。中文名里没有 `" Bee"` 可删，
所以中文那边填进去的是**整个蜂名**——这正是「凋灵蜜蜂蜜脾块」多出「蜜蜂」两个字的原因。
模板本身也从两张表里现取（`*_configurable` 那几个键），不写死。

**最长匹配优先**：`Dragonsteel Bee` 会带着词边界落在 `Lightning Dragonsteel Bee`
里边，不排掉就会误报——第一版扫描器就是这么多报了一条，而「龙霆钢蜜蜂」本来是对的。
所以某条英文名命中时，若同一段文字里还命中了包含它的更长的名字，这条不算。

## fail-closed

拿不到 jar、读不到两张表、上游英文任务书目录不在、一个任务条目都没对上——全部当红。
这道闸最没用的失败形态就是「没扫到东西所以通过」。

用法:
    python3 scripts/compliance/check_bee_names_in_quests.py <mods 目录> <上游树> <出货树>
"""
import json
import re
import sys
import zipfile
from pathlib import Path

EN_LANG = 'assets/productivebees/lang/en_us.json'
ZH_LANG = 'resourcepacks/ATM10汉化包/assets/productivebees/lang/zh_cn.json'
EN_QUESTS = 'config/ftbquests/quests/lang/en_us'
ZH_QUESTS = 'config/ftbquests/quests/lang/zh_cn'
KEY = re.compile(r'^[\t ]+([A-Za-z0-9_.]+):\s*(.*)$')
# 拿蜂名现拼的那几类名字的模板键（`%s Comb Block` / `%s蜜脾块` 这种）
DERIVED = ('block.productivebees.comb_configurable',
           'item.productivebees.honeycomb_configurable',
           'item.productivebees.spawn_egg_configurable')
# 太短的英文名（Bee、Egg 之类）拿去全文搜必然满地假阳性，判不了就不判。
MIN_LEN = 6
WORD = re.compile(r'\w+')
# 颜色码和转义换行会把词边界吃掉：`&8Withered` 里 `8` 和 `W` 都是 \w，
# 按单词切会切成一个 `8Withered`，整条静默漏判。非法码（ATM 任务书里真有 `&z`）也要剥。
NOISE = re.compile(r'[&§](?:#[0-9A-Fa-f]{6}|[0-9A-Za-z])|\\+n')


def die(msg):
    print('❌ %s' % msg)
    sys.exit(1)


def bee_names(mods, tree):
    jars = sorted(Path(mods).glob('productivebees*.jar'))
    if not jars:
        die('%s 里没有 productivebees 的 jar —— 英文名表取不到，这道闸等于没跑' % mods)
    try:
        with zipfile.ZipFile(jars[-1]) as z:
            en = json.loads(z.read(EN_LANG))
    except Exception as e:
        die('%s 里读不出 %s：%s' % (jars[-1].name, EN_LANG, e))
    zp = Path(tree) / ZH_LANG
    if not zp.is_file():
        die('%s 不在 —— 资源包没摊出来' % zp)
    try:
        zh = json.loads(zp.read_text(encoding='utf-8'))
    except Exception as e:
        die('%s 解析失败：%s' % (zp, e))

    # 一个英文名可能对应多只蜜蜂：上游把 chaos_bee 和 chaotic_bee 都叫 "Chaos Bee"，
    # 而中文得分开（混沌蜜蜂 / 混沌锭蜜蜂）。这时静态判不出正文说的是哪一只，
    # 所以只要命中其中任意一个中文名就算过——宁可漏报，不许拿判不了的事去红。
    # 蜜脾/蜜脾块/刷怪蛋的名字模板，两张表里现取
    tmpl = []
    for k in DERIVED:
        if isinstance(en.get(k), str) and isinstance(zh.get(k), str) \
                and '%s' in en[k] and '%s' in zh[k]:
            tmpl.append((en[k], zh[k]))
    if not tmpl:
        die('%s 这几个模板键一个都没配上 —— 蜜脾/刷怪蛋这类拼出来的名字判不了'
            % '、'.join(DERIVED))

    byname = {}
    for k in en:
        if not (k.startswith('entity.productivebees.') and k in zh):
            continue
        e, c = en[k], zh[k]
        if not (isinstance(e, str) and len(e) >= MIN_LEN):
            continue
        if not (isinstance(c, str) and c.strip()):
            continue
        byname.setdefault(e, set()).add(c)
        # mod 是这么拼的：本地化蜂名删掉字面量 " Bee" 再填模板。
        # 中文名里没有 " Bee"，所以中文那边填的是整个蜂名。
        stem_en = e[:-4] if e.endswith(' Bee') else e   # 跟 CombBlockItem 的 endsWith 判定一致
        for te, tz in tmpl:
            byname.setdefault(te % stem_en, set()).add(tz % c)
    pairs = sorted((e, frozenset(cs)) for e, cs in byname.items())
    if not pairs:
        die('一对「英文名→中文名」都没配上 —— 两张表对不上，判不了')
    return pairs


def quest_text(root):
    """把一棵任务书语言树读成 键 -> 全文（多行数组拼成一串，只为查词）。"""
    out = {}
    for p in sorted(Path(root).rglob('*.snbt*')):
        cur = None
        for line in p.read_text(encoding='utf-8', errors='replace').split('\n'):
            m = KEY.match(line)
            if m:
                cur = m.group(1)
                out[cur] = out.get(cur, '') + m.group(2)
            elif cur:
                out[cur] = out.get(cur, '') + line
    return out


def main(argv):
    if len(argv) != 4:
        die('用法: check_bee_names_in_quests.py <mods 目录> <上游树> <出货树>')
    mods, uproot, tree = argv[1], Path(argv[2]), Path(argv[3])
    pairs = bee_names(mods, tree)

    if not (uproot / EN_QUESTS).is_dir():
        die('上游树里没有 %s —— 英文原文取不到，无从判断译名对不对（树: %s）'
            % (EN_QUESTS, uproot))
    up = quest_text(uproot / EN_QUESTS)
    ours = quest_text(tree / ZH_QUESTS)
    if not up:
        die('%s 里一条任务文本都没读到' % (uproot / EN_QUESTS))
    if not ours:
        die('%s 里一条任务文本都没读到 —— 出货树没摊好' % (tree / ZH_QUESTS))

    common = [k for k in up if k in ours]
    if not common:
        die('英文与中文一个键都对不上 —— 两棵树不是同一版，判了也没意义')

    # 加上蜜脾/蜜脾块/刷怪蛋之后名字表涨了三倍，逐条跑正则是分钟级的。
    # 改成按首词建索引：只在正文里每个单词的位置上试以这个词开头的名字。
    by_first = {}
    for e, cs in pairs:
        m = WORD.match(e)
        if m:
            by_first.setdefault(m.group(0).lower(), []).append((e, cs))

    hits = []
    for k in common:
        text, mine = NOISE.sub(' ', up[k]), ours[k]
        found = []
        for m in WORD.finditer(text):
            for e, cs in by_first.get(m.group(0).lower(), ()):
                end = m.start() + len(e)
                if text[m.start():end].lower() != e.lower():
                    continue
                if end < len(text) and (text[end].isalnum() or text[end] == '_'):
                    continue                  # 右边界，别把 Bees 当成 Bee
                found.append((e, cs))
        for e, cs in found:
            # 最长匹配优先：短名落在长名里不算命中
            if any(len(e2) > len(e) and e.lower() in e2.lower() for e2, _ in found):
                continue
            if not any(c in mine for c in cs):
                hits.append((k, e, '／'.join(sorted(cs))))

    if hits:
        print('❌ 任务书里的蜜蜂名跟物品名对不上（玩家照任务书去 JEI 搜会搜不到）：')
        for k, e, c in sorted(hits):
            print('   %-42s 英文 %-24s 中文应出现 %s' % (k, e, c))
        return 1
    print('✅ %s：%d 条任务文本对过 %d 个蜜蜂名，全部与物品名一致'
          % (tree, len(common), len(pairs)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
