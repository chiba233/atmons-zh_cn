#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""把 src/upstream/ 里的映射套用到**目标版本的官方文件**上。

仓库里没有任何一份上游文件的副本（见 extract_upstream_patch.py 里的原因），
构建时现取官方文件、套上我们的改动。

**找不到原文就退出，绝不静默跳过。** 这条是整套结构的支点：
上游哪天把某行改了，构建当场红给你看，而不是发出去一个「旧上游 + 我们的改动」
——那种包会把上游的修复整个覆盖掉，还没人发现。

用法:
    python3 scripts/gen_upstream_patches.py <整合包根目录> <输出目录>
    # 整合包根目录 = 解出来的 overrides/，或装好的实例目录
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'upstream'


def apply_one(text, edits, rel):
    lines = text.splitlines(keepends=True)
    for k, e in enumerate(edits, 1):
        find, repl = e['find'], e['replace']
        n, m = len(lines), len(find)
        at = [i for i in range(n - m + 1) if lines[i:i + m] == find]
        # all=true：这一段在文件里出现几次就换几次。任务书的 hover 就是这样——
        # 同一件物品在一章里被提到好几遍，英文一模一样，中文当然也该一模一样，
        # 为了「唯一」去凑上下文只会让映射变脆（上游动一行就全崩）。
        if e.get('all'):
            if not at:
                sys.exit('❌ %s 第 %d 处改动在官方文件里找不到\n   原文首行: %r'
                         % (rel, k, (find[0] if find else '').rstrip('\r\n')[:100]))
            for i in reversed(at):
                lines[i:i + m] = repl
            continue
        if len(at) != 1:
            head = (find[0] if find else '').rstrip('\r\n')[:100]
            sys.exit(
                '❌ %s 第 %d 处改动在官方文件里%s\n'
                '   原文首行: %r\n'
                '   多半是上游改了这一段。请拿新版官方文件重做映射：\n'
                '     python3 scripts/extract_upstream_patch.py <官方文件> <改过的文件> %s'
                % (rel, k, '找不到' if not at else '出现了 %d 次' % len(at), head, rel))
        i = at[0]
        lines[i:i + m] = repl
    return ''.join(lines)


def main(pack_root, out_dir):
    pack_root, out_dir = Path(pack_root), Path(out_dir)
    if not SRC.is_dir():
        sys.exit('❌ 没有 %s' % SRC)
    maps = sorted(SRC.rglob('*.json'))
    if not maps:
        sys.exit('❌ %s 下一个映射都没有' % SRC)
    total = 0
    for mp in maps:
        doc = json.loads(mp.read_text(encoding='utf-8'))
        rel = doc['src']
        official = pack_root / rel
        if not official.is_file():
            sys.exit('❌ 目标版本里没有这个官方文件：%s\n'
                     '   （整合包根目录: %s）\n'
                     '   上游删掉了它的话，把 %s 一起删掉。' % (rel, pack_root, mp.relative_to(ROOT)))
        text = apply_one(official.read_text(encoding='utf-8'), doc['edits'], rel)
        t = out_dir / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(text, encoding='utf-8', newline='')
        total += len(doc['edits'])
    print('上游文件汉化：%d 个文件、%d 处改动 → %s' % (len(maps), total, out_dir))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
