#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh_cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""把**真实存在的**蓝图类别路径放进替换表里跑一遍，改动一个字就红。

## 为什么需要它

2026-07-29，issue #3：玩家用建筑棒预览「豪华」类里的建筑，游戏 NPE 闪退。
根因是我们自己：

    WindowExtendedBuildTool$4.updateElement       楼层行
        row.findPaneOfTypeByID("id", Text.class)
           .setText(Component.literal(depth + ":" + i));      ← 数据塞进 Text 控件
    WindowExtendedBuildTool.onButtonClicked
        currentBlueprintCat = button.getParent()
            .findPaneOfTypeByID("id", Text.class)
            .getText().getString().replace(":$back", "");     ← 又读回来
        handleBlueprintCategory(currentBlueprintCat, false);
            cache.get(split[0]).get(split[1])                 ← 拿去查 Map

`depth` 是 `craftsmanship/luxury` 这样的类别路径。VaultPatcher 的 dynamic 模块
钩的是 `LiteralContents.<init>`，按**栈里出现过的类名**过滤——`updateLevels` 就在
栈上，所以内部类里造的这个 literal 照样被替换。我们那 167 条 `/luxury → /豪华`
子串替换于是把 458 条真实路径改坏了 277 条，`cache.get` 落空返回 null，
下一个 `.get` 直接 NPE。

和 blockui 的对齐标志串是同一个病：**一个字符串既当界面文字又当数据**。
`vp-no-path-prefix-keys` 拦的是「以 / 开头的键」这个形状；这个脚本拦的是后果——
不管键长什么样，只要它能改动任何一条真实路径，就红。

## 怎么判定

从 mod jar 里把 `blueprints/<所属>/<包>/<类别…>/<文件>.blueprint` 全抽出来，
还原出建筑棒会构造的那些字符串：

    类别路径                    craftsmanship/luxury
    路径:蓝图名                 craftsmanship/luxury:chefshut
    路径:蓝图名:序号            craftsmanship/luxury:chefshut:0
    路径:蓝图名:$back           craftsmanship/luxury:chefshut:$back

然后按 VaultPatcher 的语义套一遍 minecolonies_styles 的替换表
（`@` 开头 = 子串替换，其余 = 全串匹配）。**期望结果是一个字都不变。**

用法:
    python3 scripts/compliance/check_minecolonies_paths.py <mods 目录>
"""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MODULE = ROOT / 'src' / 'vaultpatcher' / 'modules' / 'minecolonies_styles.json'

# 这些 jar 里装着结构包。少一个不算错（整合包可能换附属），但一个都找不到就是错。
PACK_JAR_HINTS = ('minecolonies', 'stylecolonies', 'byzantine')


def collect_paths(mods: Path):
    """还原建筑棒会拿来当 Map 键的全部字符串。"""
    depths, blueprints = set(), {}
    for jar in sorted(mods.glob('*.jar')):
        if not any(h in jar.name.lower() for h in PACK_JAR_HINTS):
            continue
        try:
            z = zipfile.ZipFile(jar)
        except Exception:                                          # noqa: BLE001
            continue
        with z:
            for n in z.namelist():
                if not (n.startswith('blueprints/') and n.endswith('.blueprint')):
                    continue
                parts = n.split('/')
                if len(parts) < 4:
                    continue
                rest, base = parts[3:-1], parts[-1][:-len('.blueprint')]
                for k in range(1, len(rest) + 1):
                    depths.add('/'.join(rest[:k]))
                blueprints.setdefault('/'.join(rest), set()).add(base)
    cases = set(depths)
    for dep, bases in blueprints.items():
        for b in sorted(bases)[:8]:          # 每层取几个就够，形状一样
            cases |= {'%s:%s' % (dep, b), '%s:%s:0' % (dep, b),
                      '%s:%s:$back' % (dep, b), '%s:%s:default:0' % (dep, b)}
    return depths, cases


def load_pairs():
    doc = json.loads(MODULE.read_text(encoding='utf-8'))
    out = []
    for blk in doc[1:]:
        subs, exact = [], {}
        for p in blk.get('pairs', []):
            v = str(p['value'])
            if v.startswith('@'):
                subs.append((p['key'], v[1:]))
            else:
                exact[p['key']] = v
        out.append((blk['target_class'][0], subs, exact))
    return out


def apply(s, subs, exact):
    if s in exact:                       # 全串匹配优先，命中就整串换掉
        return exact[s]
    for k, v in subs:                    # 其余按子串替换，和 MatchUtils 一致
        if k in s:
            s = s.replace(k, v)
    return s


def main():
    if len(sys.argv) < 2:
        print('用法: check_minecolonies_paths.py <mods 目录>')
        return 2
    mods = Path(sys.argv[1])
    if not mods.is_dir():
        print('❌ mods 目录不存在: %s' % mods)
        return 1
    depths, cases = collect_paths(mods)
    if not depths:
        # 0 命中就静默通过的闸等于没有闸——2026-07-28 的对抗审计一次抓到三个。
        # 但「MineColonies 根本不在这一版整合包里」是另一回事：那时候没有蓝图路径
        # 是正常的，这道闸也就无从谈起。两者要分开，靠**正面证明**模组不在：
        # 全包没有一个 jar 提供 assets/minecolonies/ 下的任何文件。
        # 只看 jar 文件名不够——附属包名字五花八门，得看 jar 里到底有没有这个命名空间。
        # 先排除「mods 根本没备齐」：0 个 jar 时「模组不在包里」和「包没取到」
        # 长得一模一样，放过就是静默全绿。真整合包必然有一堆 jar。
        if not list(mods.glob('*.jar')):
            print('❌ %s 下一个 jar 都没有——这不是「整合包不带 MineColonies」，'
                  '是 mods 没备齐或路径不对，判不了就不许放行' % mods)
            return 1
        ns_present = False
        for jar in sorted(mods.glob('*.jar')):
            try:
                with zipfile.ZipFile(jar) as z:
                    if any(n.startswith('assets/minecolonies/') for n in z.namelist()):
                        ns_present = True
                        break
            except Exception:                                  # noqa: BLE001
                continue
        # 不许闸自己判「模组不在就跳过」——登记过才行，见 absent.py
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from absent import allow_skip
        allow_skip('minecolonies', 'check_minecolonies_paths.py', mods, ns_present)
        return 0
        print('❌ 在 %s 里一条蓝图路径都没找到，但 assets/minecolonies/ 是在的——'
              '要么 jar 没备齐，要么结构包换了布局；这时候「通过」是假的。' % mods)
        return 1
    bad = []
    for cls, subs, exact in load_pairs():
        for s in sorted(cases):
            t = apply(s, subs, exact)
            if t != s:
                bad.append((cls.rsplit('.', 1)[-1], s, t))
    if bad:
        print('❌ 替换表改动了 %d 条**真实存在**的蓝图路径。这些串会被拿去查 Map，'
              '改一个字符就查不到，轻则楼层列表空白，重则 NPE 闪退：' % len(bad))
        for cls, s, t in bad[:25]:
            print('   [%s] %s\n            → %s' % (cls, s, t))
        if len(bad) > 25:
            print('   …另有 %d 条' % (len(bad) - 25))
        print('   修法：把命中的键从 minecolonies_styles.json 里删掉。'
              '子分类按钮显示的是路径最后一段的首字母大写形式，用精确键单独译。')
        return 1
    print('✅ 蓝图类别路径：%d 条类别、%d 条数据串回放后一字未改' % (len(depths), len(cases)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
