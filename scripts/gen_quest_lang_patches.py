#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh_cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""任务书语言：把本包的覆盖打进 ATM 自己那份章节文件，按**原文件名**出货。

## 为什么不能再靠 zz_ 前缀

`ftbquestslangsplitter` 的合并顺序**不是文件名字母序**。1.0.5 的字节码：

    // lang/<locale>/ 这一层
    Files.list(dir).sorted(Comparator.comparingInt(p -> isDirectory(p) ? 1 : 0))
    // chapters/ 里面
    Files.list(chapters).forEach(...)            // ← 一个 sort 都没有

第一层只保证「文件排在目录前面」，第二层完全不排。`Files.list` 本身不保证顺序：
NTFS / APFS 恰好按名字返回，**ext4 返回的是哈希序**。于是同一个键出现在两个文件里
时，谁生效在 Linux 上是随机的。

本包 1249 条覆盖里有 923 条与 ATM 自带的中文撞键（散在 62 个章节文件）。只要这两拨
文件**同时处于未合并状态**——也就是在服务器/客户端第一次启动之前就把包装进去——
就会有随机一批覆盖被顶回上游原文，其中包括 R16 刚修好的、会被 FTB 换成红字报错的
那两条描述。跑过一次之后再装包的机器（比如我们自己的测试服）永远看不到这个 bug：
ATM 那批早就改名成 `.snbt_merged` 了，目录里没有竞争者。

## 绕法：一个键只让一份文件持有

把覆盖直接打进上游那份章节文件，用原文件名出货，安装时覆盖掉 ATM 的同名文件。
顺序就再也不参与决策：

  - 全新实例：上游那份被我们换掉了，目录里只有一份，直接生效；
  - 已经跑过的实例：上游那份是 `.snbt_merged`（不再被读），我们这份是唯一未合并的，
    后合并覆盖先合并的。

上游自己没译的键（在任何上游文件里都找不到）留在 `chapters/hanhua_additions.snbt`，
它们不与任何文件撞键，放哪都一样。

⚠️ 用原文件名出货的前提是**整份文件都在**：只带我们那几条会把上游同名文件整个盖掉。
所以这里写出去的是「上游全文 + 我们的覆盖」，不是 delta。（2026-07 就踩过一次：
只有 2 个键的 aether.snbt 盖掉了上游同名文件的 167 个键。）

用法:
    python3 scripts/gen_quest_lang_patches.py <上游目录> <出货树> [整合包版本]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT                                              # noqa: E402

LANG = 'config/ftbquests/quests/lang/zh_cn'
DELTA_PREFIX = 'zz_hanhua_'
ADDITIONS = 'chapters/hanhua_additions.snbt'
# 上游这批文件的缩进并不统一（同一个 chapters/ 里既有 tab 也有 4 空格），所以只认
# 「行首若干空白 + 键 +冒号」，缩进原样保留——我们只换值，不重排版。
KEY = re.compile(r'^[\t ]+([A-Za-z0-9_.]+):')


class SnbtShapeError(Exception):
    """delta 文件的块结构坏了。

    单独立一个异常，是为了让 check.py 能把同一个解析器当**闸**用：
    生成阶段遇到它要当场死，校验阶段要把它变成一条带规则号的报错继续往下查。
    以前这里直接 `raise SystemExit`，check.py 想复用就只能自己再写一份解析器
    ——而 2026-08-02 的事故正是「两份解析器判得不一样」：按行 sort 把多行数组
    打散成 513 个游离的 `""`，check.py 的按行正则匹配不上就跳过，全绿放行，
    三分钟后才被真正用 blocks() 的 build.yml 拦下。
    """


def blocks(path):
    """把一个 .snbt 语言文件切成 [(键, 该键占的原始行)]，多行数组整块保留。"""
    lines = path.read_text(encoding='utf-8').split('\n')
    if not (lines and lines[0] == '{' and lines[-2:] == ['}', '']):
        raise SnbtShapeError('%s 不是预期的 snbt 语言文件（首行 { 尾行 }）' % path)
    body, out, i = lines[1:-2], [], 0
    while i < len(body):
        if not body[i].strip():          # 空行归给上一个键，输出时原样带回去
            if out:
                out[-1][1].append(body[i])
                i += 1
                continue
            raise SnbtShapeError('%s 开头就是空行' % path)
        m = KEY.match(body[i])
        if not m:
            raise SnbtShapeError('%s 第 %d 行不属于任何键: %r'
                                 % (path, i + 2, body[i][:60]))
        blk = [body[i]]
        if body[i].rstrip().endswith('['):          # 多行数组：吃到单独的 ]
            start = i
            i += 1
            while i < len(body) and body[i].strip() != ']':
                blk.append(body[i])
                i += 1
            if i >= len(body):
                # 数组没闭合就到文件尾。以前这里是 IndexError，堆栈里看不出是哪个键。
                raise SnbtShapeError('%s 第 %d 行的键 %s 起了个多行数组，直到文件尾都没闭合'
                                     % (path, start + 2, m.group(1)))
            blk.append(body[i])
        i += 1
        out.append((m.group(1), blk))
    return out


def write(path, pairs):
    path.parent.mkdir(parents=True, exist_ok=True)
    body = '\n'.join('\n'.join(b) for _, b in pairs)
    path.write_text('{\n' + body + '\n}\n', encoding='utf-8')


def collect_delta(tree, mc):
    """本包的覆盖：出货树里的 zz_hanhua_*.snbt，外加该版专属覆盖（优先级最高）。"""
    srcs = sorted((tree / LANG).rglob(DELTA_PREFIX + '*.snbt'))
    if not srcs:
        raise SystemExit('❌ 出货树里一个 %s*.snbt 都没有——assemble.py 没跑？' % DELTA_PREFIX)
    ver = ROOT / 'versions' / str(mc) / 'quest_overrides.snbt' if mc else None
    delta, owner = {}, {}
    for p in srcs + ([ver] if ver and ver.is_file() else []):
        per_version = ver is not None and p == ver
        for k, blk in blocks(p):
            if k in delta and not per_version:
                # 两个 delta 文件定义同一个键 = 又回到「靠顺序」，check.py 也拦这条
                raise SystemExit('❌ 覆盖键 %s 在 %s 与 %s 里都定义了' % (k, owner[k], p.name))
            delta[k], owner[k] = blk, p.name
    return srcs, delta, ver


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    uproot, tree = Path(sys.argv[1]), Path(sys.argv[2])
    mc = sys.argv[3] if len(sys.argv) > 3 else None

    upstream_dir = uproot / LANG
    if not upstream_dir.is_dir():
        raise SystemExit('❌ 上游目录里没有 %s：%s' % (LANG, uproot))

    srcs, delta, ver = collect_delta(tree, mc)

    # 上游每个键归属哪个文件（上游自己跨文件不许重键，重了说明我们的假设塌了）
    up_files = sorted(upstream_dir.glob('*.snbt')) + sorted((upstream_dir / 'chapters').glob('*.snbt'))
    if not up_files:
        raise SystemExit('❌ 上游 %s 下一个 .snbt 都没有' % LANG)
    up_pairs, home = {}, {}
    for p in up_files:
        rel = p.relative_to(upstream_dir).as_posix()
        up_pairs[rel] = blocks(p)
        for k, _ in up_pairs[rel]:
            if k in home:
                raise SystemExit('❌ 上游自己重键：%s 同时在 %s 与 %s' % (k, home[k], rel))
            home[k] = rel

    # 打补丁：上游全文 + 我们的覆盖，位置不动
    placed, touched = set(), []
    for rel, pairs in up_pairs.items():
        hits = [k for k, _ in pairs if k in delta]
        if not hits:
            continue
        write(tree / LANG / rel, [(k, delta[k] if k in delta else blk) for k, blk in pairs])
        placed.update(hits)
        touched.append((rel, len(hits)))

    # 上游没有的键：单独一个文件，它们跟谁都不撞
    extra = sorted(k for k in delta if k not in placed)
    if extra:
        write(tree / LANG / ADDITIONS, [(k, delta[k]) for k in extra])

    # 覆盖已经落进上游文件了，delta 文件不能再带键出货，否则同一个键又是两份。
    # 但**不能只是不发**：安装器只覆盖不删除，老版本装过的 zz_hanhua_*.snbt 会原样
    # 留在玩家硬盘上，而且多半还是未合并状态（内容没变化时 splitter 不改名），
    # 升级后就变成「旧值的 delta」和「新值的上游文件」抢同一个键——正是本文件要
    # 消灭的那个 bug，只不过是自己造出来的。所以照原名发一个空壳把它盖掉。
    # src/ 有保护清单（只增不删），所以这批文件名只会变多不会变少，
    # 空壳集合天然是「历史上发过的一切」的超集。
    for p in srcs:
        p.write_text('{\n}\n', encoding='utf-8')
        # r13 及更早还用过 `_<章节名>.snbt` 这个命名（`_` 0x5F 排在小写字母前面，
        # 当初以为字母序能决定覆盖关系）。那批文件同样只覆盖不删除，同样可能还是
        # 未合并状态、同样会跟新文件抢键，而它们的名字跟我们现在发的不一样，
        # 不会被 payload 覆盖掉。所以照样发一个同名空壳把它盖住。
        legacy = p.with_name('_' + p.name[len(DELTA_PREFIX):])
        if legacy.name != p.name:
            legacy.write_text('{\n}\n', encoding='utf-8')

    # ── 自检 ──────────────────────────────────────────────────────────────
    if len(placed) + len(extra) != len(delta):
        raise SystemExit('❌ 覆盖键 %d 条，落位 %d + %d 条，对不上'
                         % (len(delta), len(placed), len(extra)))
    seen = {}
    for p in sorted((tree / LANG).rglob('*.snbt')):
        rel = p.relative_to(tree / LANG).as_posix()
        got = [k for k, _ in blocks(p)]
        if len(got) != len(set(got)):
            raise SystemExit('❌ %s 内部有重复键' % rel)
        if rel in up_pairs and len(got) != len(up_pairs[rel]):
            raise SystemExit('❌ %s 的键数从 %d 变成了 %d——上游内容被吃掉了'
                             % (rel, len(up_pairs[rel]), len(got)))
        for k in got:
            if k in seen:
                raise SystemExit('❌ 出货树里 %s 同时出现在 %s 与 %s（又回到靠顺序了）'
                                 % (k, seen[k], rel))
            seen[k] = rel
    for k in delta:
        if k not in seen:
            raise SystemExit('❌ 覆盖键 %s 没出现在出货树里' % k)

    print('✅ 任务书语言：%d 条覆盖打进上游 %d 个文件%s，上游没有的 %d 条进 %s'
          % (len(placed), len(touched),
             '（含 %s 专属 %d 条）' % (mc, len(blocks(ver))) if ver and ver.is_file() else '',
             len(extra), ADDITIONS))


if __name__ == '__main__':
    try:
        main()
    except SnbtShapeError as e:
        # 生成阶段块结构坏了就当场死；报错要跟以前一样是一行人话，不是堆栈。
        raise SystemExit('❌ %s' % e)
