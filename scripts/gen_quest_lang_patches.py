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

## 上游不带中文时，底本取上游的 en_us

**底本一律取上游自己的字节**：上游自带 zh_cn 时取它，没有时取 en_us。
本包所在的整合包自带十种语言，没有 zh_cn，走的是后一种。

底本决定「有哪些键、哪个文件持有它」。取上游的，这两件事就始终跟着上游走：
上游加一章、挪一个键，出货文件如实反映，键对不上时下面那几道自检当场报出来。

取英文当底还有一层好处：出货的是**完整**文件，有中文的填中文、没中文的留英文。
没译到的键不会从文件里消失，缺口也是可数的——本版 9255 键里 7338 条中文、
1917 条英文。

此时 `src/config/…/lang/zh_cn/` 是**覆盖**（优先级见 collect_delta），盖在英文
底本上，不参与「有哪些键」的决定。

走这条路之前要**正面证明**上游确实不带 zh_cn（任务书 lang 目录在、且至少有一种
别的语言）。上游哪天开始自带中文任务书，这里当场变红：底本换回 zh_cn，
`src/` 那边也要改回真正的 delta 形态。

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


def collect_delta(tree, mc, include_ours=False):
    """本包的覆盖，按优先级从低到高叠。

    - ``include_ours``：上游不带 zh_cn 时，我们自己那棵 zh_cn 树也是覆盖的一部分
      （它盖的是**英文底本**）。此时优先级最低——生成器现推的东西该压过它。
    - ``zz_hanhua_*.snbt``：构建时现产的覆盖（如资源树育种副标题，从本版的授粉
      配方现推）。压过上一条：同一批键上，现推的比搬来的更贴合这一版。
    - ``versions/<版本>/quest_overrides.snbt``：该版专属，优先级最高。
    """
    srcs = sorted((tree / LANG).rglob(DELTA_PREFIX + '*.snbt'))
    if not srcs:
        raise SystemExit('❌ 出货树里一个 %s*.snbt 都没有——assemble.py 没跑？' % DELTA_PREFIX)
    ver = ROOT / 'versions' / str(mc) / 'quest_overrides.snbt' if mc else None
    delta, owner = {}, {}
    if include_ours:
        ours = [p for p in sorted((tree / LANG).rglob('*.snbt'))
                if not p.name.startswith(DELTA_PREFIX)]
        if not ours:
            raise SystemExit('❌ 出货树 %s 下一份中文都没有——assemble.py 没跑？' % (tree / LANG))
        for p in ours:
            for k, blk in blocks(p):
                if k in delta:
                    raise SystemExit('❌ 本包自己重键：%s 同时在 %s 与 %s'
                                     % (k, owner[k], p.name))
                delta[k], owner[k] = blk, p.name
    for p in srcs + ([ver] if ver and ver.is_file() else []):
        per_version = ver is not None and p == ver
        for k, blk in blocks(p):
            if k in delta and not per_version and owner[k].startswith(DELTA_PREFIX):
                # 两个 delta 文件定义同一个键 = 又回到「靠顺序」，check.py 也拦这条
                raise SystemExit('❌ 覆盖键 %s 在 %s 与 %s 里都定义了' % (k, owner[k], p.name))
            delta[k], owner[k] = blk, p.name
    return srcs, delta, ver


def assert_no_upstream_zh(uproot):
    """确认「上游确实不带 zh_cn 任务书」，而不是包没取到 / 路径写错。

    「上游没有 zh_cn」与「压根没取到上游」在代码里长得一模一样，后者静默放过
    就会发出一个把上游中文整个丢掉的包。所以这里要求**正面证明**看到的是一个
    真实的整合包：任务书 lang 目录必须在，且里面至少有一种别的语言。
    """
    lang_root = uproot / LANG.rsplit('/', 1)[0]
    if not lang_root.is_dir():
        raise SystemExit('❌ 上游连 %s 都没有：%s\n'
                         '   多半是整合包没取到或路径写错，不是「上游不带中文」。'
                         % (LANG.rsplit('/', 1)[0], uproot))
    others = sorted(p.name for p in lang_root.iterdir()
                    if p.name != 'zh_cn' and (p.is_dir() or p.suffix == '.snbt'))
    if not others:
        raise SystemExit('❌ 上游 %s 下一种语言都没有：%s\n'
                         '   空目录不能当作「上游不带中文」的证据。'
                         % (LANG.rsplit('/', 1)[0], uproot))
    if (uproot / LANG).exists():
        raise SystemExit(
            '❌ 上游开始自带 zh_cn 任务书了：%s\n'
            '   本包的 src/config/…/lang/zh_cn/ 用的是上游章节名、整份出货，\n'
            '   照这样发下去会把上游那份**整个盖掉**（2026-07 只有 2 个键的\n'
            '   aether.snbt 盖掉上游同名文件 167 个键，就是这个）。\n'
            '   要改回 delta 机制：源文件加 %s 前缀，只留我们要改的键。'
            % (uproot / LANG, DELTA_PREFIX))
    print('   上游不带 zh_cn 任务书（另有 %d 种语言：%s）'
          % (len(others), '、'.join(others[:4])))


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    uproot, tree = Path(sys.argv[1]), Path(sys.argv[2])
    mc = sys.argv[3] if len(sys.argv) > 3 else None

    upstream_dir = uproot / LANG
    base_dir = upstream_dir
    up_files = sorted(base_dir.glob('*.snbt')) + sorted((base_dir / 'chapters').glob('*.snbt'))
    fallback_en = not up_files

    if up_files:
        srcs, delta, ver = collect_delta(tree, mc)
        # 上游有 zh_cn，而我们树里同时躺着一批**非 delta**的中文文件——那是「按上游
        # 章节名整份出货」的形态，会把上游同名文件整个盖掉。两者不能并存。
        ours = [p for p in sorted((tree / LANG).rglob('*.snbt'))
                if not p.name.startswith(DELTA_PREFIX)]
        if ours:
            raise SystemExit(
                '❌ 上游开始自带 zh_cn 任务书了（%d 个文件），而本包仍按上游章节名\n'
                '   整份出货（树里有 %d 份非 delta 的中文，如 %s）。\n'
                '   照这样发会把上游那份**整个盖掉**——2026-07 只有 2 个键的 aether.snbt\n'
                '   盖掉上游同名文件 167 个键，就是这个。\n'
                '   要改回 delta 形态：src/config/…/lang/zh_cn/ 下的文件加 %s 前缀，\n'
                '   只保留我们真正要改的键。'
                % (len(up_files), len(ours), ours[0].name, DELTA_PREFIX))
    else:
        # 上游一条中文都没有 → **底本取上游的 en_us**（见本文件顶部）。
        # 不能拿我们自己那棵 zh_cn 当底：那等于把「我们译过什么」当成「有哪些键」，
        # 没译到的键就从出货文件里整个消失了。取英文当底，出去的是一份**完整**文件，
        # 有中文的填中文、没中文的**显式留英文**，缺口也随之变成可数的。
        assert_no_upstream_zh(uproot)
        base_dir = uproot / (LANG.rsplit('/', 1)[0] + '/en_us')
        up_files = sorted(base_dir.glob('*.snbt*')) + sorted((base_dir / 'chapters').glob('*.snbt*'))
        if not up_files:
            raise SystemExit('❌ 上游 %s 下一个 .snbt 都没有——判不了有哪些键' % base_dir)
        srcs, delta, ver = collect_delta(tree, mc, include_ours=True)
        print('   底本取上游 en_us（%d 个文件）' % len(up_files))

    up_pairs, home = {}, {}
    for p in up_files:
        # splitter 进过一次游戏后会把 xxx.snbt 改名成 xxx.snbt_merged，而整合包**就是
        # 按 .snbt_merged 发的**。出货必须还原成 .snbt：splitter 的 isValidLangFile
        # 只认 .snbt 结尾，发成 .snbt_merged 等于这份文件永远不会被读。
        rel = p.relative_to(base_dir).as_posix().replace('.snbt_merged', '.snbt')
        up_pairs[rel] = blocks(p)
        for k, _ in up_pairs[rel]:
            if k in home:
                raise SystemExit('❌ 底本自己重键：%s 同时在 %s 与 %s' % (k, home[k], rel))
            home[k] = rel

    # 打补丁：底本全文 + 我们的覆盖，位置不动
    #
    # 一个覆盖都没命中的底本文件写不写，两种模式不一样：
    #   底本是上游 zh_cn —— 不写。那份中文本来就在玩家盘上，原样留着即可。
    #   底本是上游 en_us —— **要写**。zh_cn 这一侧本来空无一物，不写这份键就没有
    #     中文文件持有，等于把「没译到的键」从出货里抹掉；写出来才是完整的一份，
    #     没译的位置显式留英文。
    placed, touched = set(), []
    for rel, pairs in up_pairs.items():
        hits = [k for k, _ in pairs if k in delta]
        if not hits and not fallback_en:
            continue
        write(tree / LANG / rel, [(k, delta[k] if k in delta else blk) for k, blk in pairs])
        placed.update(hits)
        if hits:
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
            raise SystemExit('❌ %s 的键数从 %d 变成了 %d——底本内容被吃掉了'
                             % (rel, len(up_pairs[rel]), len(got)))
        for k in got:
            if k in seen:
                raise SystemExit('❌ 出货树里 %s 同时出现在 %s 与 %s（又回到靠顺序了）'
                                 % (k, seen[k], rel))
            seen[k] = rel
    for k in delta:
        if k not in seen:
            raise SystemExit('❌ 覆盖键 %s 没出现在出货树里' % k)

    total = sum(len(v) for v in up_pairs.values())
    print('✅ 任务书语言：%d 条覆盖打进底本 %d 个文件%s，底本没有的 %d 条进 %s'
          % (len(placed), len(touched),
             '（含 %s 专属 %d 条）' % (mc, len(blocks(ver))) if ver and ver.is_file() else '',
             len(extra), ADDITIONS))
    if fallback_en:
        # 底本是英文，所以出货文件里没被覆盖到的都还是英文——这个数就是翻译缺口
        print('   底本 %d 键：中文 %d 条，仍是英文 %d 条'
              % (total, len(placed), total - len(placed)))


if __name__ == '__main__':
    try:
        main()
    except SnbtShapeError as e:
        # 生成阶段块结构坏了就当场死；报错要跟以前一样是一行人话，不是堆栈。
        raise SystemExit('❌ %s' % e)
