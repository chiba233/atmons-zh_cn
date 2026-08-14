#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh_cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""**跳过一道闸必须先登记。**

有几道闸盯的是某个具体模组（建筑棒的蓝图路径、MineColonies 的 GUI 贴图、
神谕目录里某本书的目录约定）。换一个整合包，这些模组可能压根不在，闸就无从谈起。

危险的做法是让闸自己判「模组不在就跳过」——那样一来，**模组哪天被上游拿掉、
或者 mods 目录没备齐**，闸都会安静地退 0，而它本来是防事故用的
（建筑棒那条闸对应的是 issue #3：译坏一条蓝图路径，玩家点开预览直接 NPE 闪退）。

所以跳过这件事挪到仓库里显式登记：

  - 登记在 src/absent_mods.json 的，且**当场核实该命名空间确实不在包里**，才跳过；
  - 没登记的模组缺失 → 红；
  - 登记了、但那个模组其实**在**包里 → 也红。登记条目过期了得有人知道，
    否则上游把模组加回来，这道闸就永远地睡着了。

登记条目要写明 approved_by / date / why，跟 protect.py 的 released 一样在版本库里留疤。

用法（给闸调用）:
    from absent import allow_skip
    if allow_skip('minecolonies', 'check_minecolonies_paths.py', mods_dir, present):
        ...
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST = ROOT / 'src' / 'absent_mods.json'


def _load():
    if not MANIFEST.is_file():
        sys.exit('❌ 缺 %s —— 没有这份登记就没人能跳过任何一道闸' % MANIFEST)
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    out = {}
    for row in doc.get('absent') or []:
        for f in ('namespace', 'gates', 'why', 'approved_by', 'date'):
            if not row.get(f):
                sys.exit('❌ %s 里有条目缺 %s —— 跳过闸必须写明谁批的、为什么、哪天'
                         % (MANIFEST.name, f))
        out[row['namespace']] = row
    return out


def allow_skip(namespace, gate, where, present):
    """能不能因为「本包不带这个模组」而跳过这道闸。

    ``present`` 由调用方现测：该命名空间此刻在不在包里。这里**不替调用方去查**，
    因为每道闸判「在不在」的办法不同（有的看 assets/<ns>/，有的看某个具体文件）。

    返回 True 才允许跳过；其余情况一律 SystemExit，不给调用方留「静默放行」的口子。
    """
    rows = _load()
    row = rows.get(namespace)
    if row is None:
        sys.exit('❌ %s 在 %s 里找不到，而这道闸需要它。\n'
                 '   如果本整合包确实不带这个模组，把它登记进 %s（写明谁批的、'
                 '为什么、哪天）；在那之前不许跳过。\n   （查的目录: %s）'
                 % (namespace, MANIFEST.name, MANIFEST.name, where))
    if gate not in row['gates']:
        sys.exit('❌ %s 登记了「本包不带」，但没写它管到 %s 这道闸。\n'
                 '   要跳过就把这道闸加进它的 gates 里，别让登记条目替别的闸背书。'
                 % (namespace, gate))
    if present:
        sys.exit('❌ %s 登记着「本整合包不带」，但它此刻**在**包里（%s）。\n'
                 '   登记过期了：把这一条从 %s 删掉，让闸重新跑起来。'
                 % (namespace, where, MANIFEST.name))
    print('ℹ️ 跳过：本整合包不带 %s（%s 已登记，%s 于 %s 批准）\n   理由：%s'
          % (namespace, MANIFEST.name, row['approved_by'], row['date'], row['why']))
    return True


def main(argv):
    """`absent.py --check <mods 目录>`：登记表自检。

    登记条目**只允许**在那个命名空间确实不在包里时存在。上游哪天把模组加回来，
    这里当场红——否则那条登记会一直挂着，等下一次有人复用它去跳过别的闸。
    """
    if len(argv) != 3 or argv[1] != '--check':
        sys.exit('用法: absent.py --check <mods 目录>')
    import zipfile
    mods = Path(argv[2])
    jars = sorted(mods.glob('*.jar'))
    if not jars:
        sys.exit('❌ %s 下一个 jar 都没有——判不了登记条目是否过期' % mods)
    # 登记项可以是命名空间（minecolonies），也可以是命名空间下的一段路径
    # （oracle_index/books/mffs）。后者必须按**完整前缀**判：oracle_index 这个
    # 模组在包里，不在的只是 mffs 那本书，按首段判会误报成过期。
    names = set()
    for j in jars:
        try:
            with zipfile.ZipFile(j) as z:
                names.update(n for n in z.namelist() if n.startswith('assets/'))
        except Exception:                                      # noqa: BLE001
            continue
    rows = _load()
    stale = [ns for ns in rows
             if any(n.startswith('assets/%s/' % ns) for n in names)]
    for ns, row in sorted(rows.items()):
        print('  %-34s %s 于 %s 批准' % (ns, row['approved_by'], row['date']))
    if stale:
        sys.exit('\n❌ 这些登记过期了——它们此刻**在**包里，相关的闸本该跑起来：\n   '
                 + '\n   '.join(stale) + '\n   把它们从 %s 里删掉。' % MANIFEST.name)
    print('✅ 登记表：%d 条，逐条核过对应命名空间确实不在这一版整合包里' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
