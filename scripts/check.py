# -*- coding: utf-8 -*-
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""发版前校验 —— **规则解释器**。

规则本身不在这个文件里，在 `src/rules/*.json`。这里只提供一批检查器
（`@checker('kind')`），按每条规则的 `kind` 分派。

    加一条同类规则  → 只改 src/rules 里的 JSON，这个文件一个字都不用动
    加一种新检查器  → 才需要在这里加一个函数

之前是 284 行顺序执行、注释编号 1..8，加第 9 条要改文件、加第 10 条再改一次。
更要命的是有两类东西会**持续累积**——废弃译名、豁免白名单——它们硬编码进脚本，
脚本就会慢慢长成垃圾桶。所以它们现在是数据。

每条规则的 `why` 是必填的：这些规则几乎每一条背后都有一次真事故，理由不写下来，
后人既不敢删也不敢改，最后只能绕过去。

用法:
    python3 scripts/check.py [出货树]        # 缺省 build/common
"""
import json
import os
import re
import sys
from pathlib import Path

from paths import COMMON, SRC

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = SRC / 'rules'

# 查的是**出货树**（含全部生成物）。默认 build/common；build_dist.sh 会把
# 「common + 该版上游补丁」合成好的那棵树传进来，于是每个版本都各查一遍。
TREE = Path(sys.argv[1]) if len(sys.argv) > 1 else COMMON
PACK_DIR = TREE / 'resourcepacks' / 'ATM10汉化包'

CJK = re.compile(r'[一-鿿]')
CHECKERS = {}

# 有几条检查的前提是**生成物**（要读 mod jar 才能产出）。没有 jar 的环境里它们
# 真的不存在，这时报错只会教人把闸关掉；但在**本该已经生成完**的流水线里，
# 「前提不在」意味着生成器静默没产出，而闸跟着一起消失——退出码上跟「查过了没问题」
# 一模一样。protect.py 那次就是这么漏的（详见它顶部的注释）。
# 所以：跑在生成之后的环节一律传 GATE_STRICT=1，让「闸没跑成」变成红。
STRICT = (os.environ.get('GATE_STRICT') or '').strip() not in ('', '0')


def absent(what, hint):
    """前提缺失时的统一出口。

    返回该 yield 出去的话（strict 下），或 None（非 strict，只打一行 ℹ️）。
    调用方一律写成 `m = absent(...); if m: yield m; return`。
    """
    if STRICT:
        return ('%s没跑成：%s。本环境声明了 GATE_STRICT——前提本该已经生成好，'
                '缺了就是生成环节出问题，不算通过' % (what, hint))
    print('ℹ️ 跳过%s：%s' % (what, hint))
    return None


def checker(kind):
    def deco(fn):
        CHECKERS[kind] = fn
        return fn
    return deco


def need(rule, *fields):
    for f in fields:
        if f not in rule:
            raise KeyError('规则 %s 缺字段 %s' % (rule.get('id', '?'), f))
    return [rule[f] for f in fields]


def files(pattern):
    """出货树里 glob 命中的文件。"""
    return sorted(p for p in TREE.glob(pattern) if p.is_file())


def rel(p):
    try:
        return p.relative_to(TREE).as_posix()
    except ValueError:
        return p.relative_to(ROOT).as_posix()


# ────────────────────────────── 通用检查器 ──────────────────────────────

@checker('json_parses')
def _json_parses(rule):
    g, = need(rule, 'glob')
    hit = files(g)
    if not hit:
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        try:
            json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            yield '%s: JSON 解析失败: %s' % (rel(p), e)


@checker('no_files')
def _no_files(rule):
    """出货树里不许存在匹配该 glob 的文件（用来拦「本该删掉却还在生成」的产物）。"""
    g, = need(rule, 'glob')
    hit = files(g)
    for p in hit:
        yield '不该出现的文件 %s —— %s' % (rel(p), rule['why'])


@checker('vp_no_single_word_keys')
def _vp_no_single_word(rule):
    """配置界面模块里不许出现单个词的键——那类词多半同时是枚举值。

    见 [vp-enum-protocol-values]：RFTools 把 `Ignored` / `Off` 这类界面词
    同时当枚举名反查，译了游戏直接抛异常。配置界面同理：下拉框里选的值和
    条目标签长得一模一样，分不清，所以整类放弃。
    """
    mods, = need(rule, 'modules')
    for mod in mods:
        f = ROOT / 'src' / 'vaultpatcher' / 'modules' / mod
        if not f.is_file():
            continue
        doc = json.loads(f.read_text(encoding='utf-8'))
        for blk in doc[1:]:
            for pair in blk.get('pairs', []):
                if len(pair['key'].split()) < 2:
                    yield '%s 出现单词键 %r —— %s' % (mod, pair['key'], rule['why'])


@checker('vp_no_key_prefix')
def _vp_no_key_prefix(rule):
    """键不许以这些前缀开头——以它们开头的字符串是**路径片段**，不是界面文字。

    2026-07-29 的实机崩溃（issue #3）：structurize 的建筑棒把「类别路径」
    （`craftsmanship/luxury` 这种）同时当三件事用——顶部面包屑显示、按钮 ID、
    以及 `currentBluePrintMappingAtDepthCache` 的 **Map 键**。楼层行还会把
    `路径:序号` 塞进一个隐藏的 Text 控件，点击时再 `getText().getString()`
    读回来当键查表。我们为了让面包屑显示中文，写了 167 条 `/luxury → /豪华`
    这样的子串替换，于是 458 条真实路径里有 277 条被改写，查表落空
    → `handleBlueprintCategory` 里 `cache.get(...)` 返回 null → NPE 闪退。

    路径片段几乎必然是数据：目录名要拿去查表、拼 ID、做 ResourceLocation。
    而按钮上真正显示的是「路径最后一段首字母大写」，那是个单独的短词，
    用精确键就能译——所以整类以 `/` 开头的键放弃，一条都不留。
    """
    prefixes, = need(rule, 'prefixes')
    mods = sorted((ROOT / 'src' / 'vaultpatcher' / 'modules').glob('*.json'))
    if not mods:
        yield 'src/vaultpatcher/modules 下一个模块都没有（规则失效了，比不加还危险）'
    for f in mods:
        try:
            doc = json.loads(f.read_text(encoding='utf-8'))
        except Exception:                                          # noqa: BLE001
            continue
        if not isinstance(doc, list):
            continue
        for blk in doc[1:]:
            for pair in blk.get('pairs', []):
                k = pair.get('key', '')
                if any(k.startswith(p) for p in prefixes):
                    yield '%s 的键 %r 是路径片段 —— %s' % (f.name, k, rule['why'])


@checker('vp_forbidden_keys')
def _vp_forbidden_keys(rule):
    """有些字符串是**行为标志**，不是界面文字，译了功能就坏。

    blockui 的 Alignment 是典型：`horizontalCentered = tag.contains("horizontal")`。
    把 'top horizontal' 译成 '顶部水平' 之后 contains 落空，整个 blockui 的对齐
    系统失效——所有界面文字一律贴左，连上游自己写的 textalign 都不生效。
    这类只能靠**点名禁译**兜住，因为从字面看它和普通界面文字没有区别。
    """
    keys, = need(rule, 'keys')
    ban = set(keys)
    for f in sorted((ROOT / 'src' / 'vaultpatcher' / 'modules').glob('*.json')):
        try:
            doc = json.loads(f.read_text(encoding='utf-8'))
        except Exception:                                          # noqa: BLE001
            continue
        if not isinstance(doc, list):
            continue
        for blk in doc[1:]:
            for pair in blk.get('pairs', []):
                if pair.get('key') in ban:
                    yield '%s 译了 %r —— %s' % (f.name, pair['key'], rule['why'])


@checker('xml_parses')
def _xml_parses(rule):
    """出货的界面 XML 必须能解析。

    2026-07-28 的实机事故：我们盖过去的 windowtownhall.xml 里同一个 <button>
    出现了两个 textoffset（上游本来就有一个，我们又插了一个），blockui 抛
    「Can't parse xml at: …」，玩家一右键市政厅游戏就崩。XML 坏了不像 JSON
    那样构建时就露馅——它要等玩家开那个界面才炸，所以必须在这里拦。
    """
    import xml.etree.ElementTree as ET
    g, = need(rule, 'glob')
    hit = files(g)
    if not hit:
        # 这些 XML 是 gen_literal_books.py 拿 mod jar 现套出来的。没有 jar 的环境
        # （只跑 assemble.py）根本没有它们，这时报错只会教人把闸关掉；有 jar 却一个
        # 都没命中，才是真出事了——所以按「装过书没有」来分。
        base = TREE / 'resourcepacks' / 'ATM10汉化包' / 'assets'
        if not any((base / ns / 'gui').is_dir() for ns in ('minecolonies', 'structurize')):
            # 这条**不接 GATE_STRICT**：0 个 XML 是当前的有意状态，不是生成失败。
            # aafe85f「根因修好之后，撤掉全部为它做的补偿性改动」之后我们不再发任何
            # 界面 XML（此前 74 个）——那笔的提交信息里写明了「两道闸留着，将来真要
            # 盖 XML 时仍然拦得住」。所以它是一道**刻意留空的待用闸**，
            # 把「没有文件」当失败等于反过来强迫我们重新发 XML。
            print('ℹ️ 跳过界面 XML 解析检查：本版不发任何界面 XML（见 aafe85f），'
                  '这道闸留给将来真要盖 XML 的时候')
            return
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        try:
            ET.fromstring(p.read_bytes())
        except Exception as e:
            yield '%s: XML 解析失败: %s —— %s' % (rel(p), e, rule['why'])


@checker('json_assert')
def _json_assert(rule):
    f, path, want = need(rule, 'file', 'path', 'equals')
    p = TREE / f
    if not p.is_file():
        yield '缺少 %s' % f
        return
    cur = json.loads(p.read_text(encoding='utf-8'))
    for step in path:
        cur = cur.get(step) if isinstance(cur, dict) else None
    if cur != want:
        yield '%s 的 %s 必须是 %r，实为 %r —— %s' % (f, '.'.join(path), want, cur, rule['why'])


@checker('file_absent')
def _file_absent(rule):
    p, = need(rule, 'path')
    if (TREE / p).exists():
        yield '%s 不应存在 —— %s' % (p, rule['why'])


@checker('filename_prefix')
def _filename_prefix(rule):
    g, pre = need(rule, 'glob', 'prefix')
    msg = rule.get('message', '{path} 缺少前缀 {prefix}')
    # scope=repo 时 glob 相对仓库根，用来查 src/ 里的**源文件**命名
    # （出货树里的文件名可能是生成器按上游原名写出去的，那是另一回事）
    hit = (sorted(p for p in ROOT.glob(g) if p.is_file())
           if rule.get('scope') == 'repo' else files(g))
    if not hit:
        # 和 json_parses 同款自爆：一个文件都没命中说明源文件被挪走/删了，
        # 闸会跟着静默消失——比不加闸更危险。（2026-07-28 对抗审计指出的不一致）
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        if not p.name.startswith(pre):
            yield msg.format(path=rel(p), prefix=pre)


@checker('js_no_duplicate_decl')
def _js_no_duplicate_decl(rule):
    """同一批 KubeJS 脚本之间不许有重名的顶层声明。

    KubeJS 的 client_scripts 共用**同一个全局作用域**。两个文件各写一句
    `const $Component = Java.loadClass(...)`，第二个加载时抛
    `TypeError: redeclaration of const $Component`，而且**整批客户端脚本一起挂**——
    连没问题的那个文件（蜂名 tooltip）也一起没了，玩家只看到一个红框。
    2026-08-01 实机踩到：新加的 occultism_flame_tooltip.js 与 pb_hanhua_tooltip.js
    撞了 `$Component` / `$ItemTooltipEvent`。

    检测按「顶格（第 0 列）声明」算，比真实的全局集合更宽——包在 IIFE 里的名字
    也会被算进来。宁可多报：重名改个名就行，漏报是整批脚本挂掉。
    """
    g, = need(rule, 'glob')
    hit = files(g)
    if len(hit) < 2:
        m = absent('「客户端脚本不许重名声明」', '%r 只命中 %d 个文件，凑不出两两比较'
                   % (g, len(hit)))
        if m:
            yield m
        return
    decl = re.compile(r'^(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)')
    seen = {}
    for p in hit:
        for ln in p.read_text(encoding='utf-8').splitlines():
            m = decl.match(ln)          # 顶格才算：match 而不是 search
            if not m:
                continue
            name = m.group(1)
            if name in seen and seen[name] != rel(p):
                yield ('%s 与 %s 都在顶层声明了 %s —— KubeJS 客户端脚本共用一个作用域，'
                       '第二个会抛 redeclaration，整批脚本一起加载失败'
                       % (seen[name], rel(p), name))
            seen.setdefault(name, rel(p))


@checker('js_no_const_inside_block')
def _js_no_const_inside_block(rule):
    """`try {}` / `if {}` / `for {}` 这类**普通块**内部不许 `const`，只许赋值。

    KubeJS 的 Rhino 里，写在普通块内部的 `const` 会抛
    `TypeError: redeclaration of var <名字>`——它把块里的 const 提升成了函数作用域的
    var，执行到声明那一句时撞上自己。要命的是它**运行时才抛**：脚本加载阶段照样
    `0 errors`，闸和 CI 全绿，而它躺在事件回调里就表现成「进游戏什么都没发生」，
    跟「这功能没被触发」完全无法区分。2026-08-01 实机连踩两次，第二次是我误判成
    `$` 前缀的问题、去掉 `$` 之后照样抛，才定位到真正的形状。

    函数体 / 回调体的**顶层** const 是安全的：拿整包 ATM10 的 kubejs 对照过，上游
    几十处缩进 const 全都在 `ServerEvents.recipes(x => {` 这类回调体顶层，没有任何
    一处写进普通块里；写进块里的只有本包那一个文件。所以这里只拦「最内层那个 `{`
    不是函数/箭头开的」这一种，函数体顶层照旧放行。
    """
    g, = need(rule, 'glob')
    hit = files(g)
    if not hit:
        m = absent('「块里不许 const」', '%r 一个文件都没命中' % g)
        if m:
            yield m
        return
    decl = re.compile(r'^[\t ]*const\s+([\w$]+)')
    # 这一行开出来的块算不算「函数体」：箭头、function、以及 `get x() {` 这类方法。
    funcish = re.compile(r'=>|\bfunction\b')
    for p in hit:
        stack = []                      # 每层一个布尔：True = 函数体
        for i, raw in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            ln = raw.split('//')[0]     # 注释里的花括号不算（本文件注释里就有 `try {}`）
            m = decl.match(raw)
            if m and stack and not stack[-1]:
                yield ('%s:%d 在块内部 `const %s` —— KubeJS 的 Rhino 会抛 '
                       'redeclaration of var，且只在这段代码真被执行时才炸；'
                       '把声明提到函数体顶层、块里只赋值' % (rel(p), i, m.group(1)))
            kind = bool(funcish.search(ln))
            for ch in ln:
                if ch == '{':
                    stack.append(kind)
                elif ch == '}' and stack:
                    stack.pop()


@checker('lang_value_forbidden')
def _lang_value_forbidden(rule):
    """lang 文件里，键匹配 key_regex 的条目，值不许匹配 value_regex。

    issue #8：物品 tooltip 是被 `Component.translatable(...)` 整条塞进
    `List<Component>` 的，vanilla 渲染 tooltip 走 `Component#getVisualOrderText`，
    **不做断行**——值里的 `\\n` 不会换行，而是按 U+000A 去字体里查字形，
    unifont 给控制字符画的是一个写着「LF」的小方框，玩家看到的就是一颗多余的符号。
    上游 en_us 里就有（英文同样是方框），所以升版重导上游译文时极易复发。
    """
    g, kre, vre = need(rule, 'glob', 'key_regex', 'value_regex')
    msg = rule.get('message', '{key}: 值里不许出现 {value_regex}')
    krx, vrx = re.compile(kre), re.compile(vre)
    hit = files(g)
    if not hit:
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        doc = json.loads(p.read_text(encoding='utf-8'))
        watched = [k for k in doc if krx.search(k)]
        if not watched:
            # 键被上游改名 / 文件被换掉 → 规则空转。空转和「查过了没问题」
            # 在退出码上一模一样，所以这里必须自爆。
            yield '%s: key_regex %r 一个键都没匹配到（规则失效了，比不加还危险）' % (rel(p), kre)
        for k in watched:
            if vrx.search(doc[k]):
                yield '%s: %s' % (rel(p), msg.format(key=k, value_regex=vre))


@checker('forbidden_text')
def _forbidden_text(rule):
    terms, = need(rule, 'terms')
    msg = rule.get('message', '含禁用词 "{term}"')
    allow = tuple(rule.get('allow_paths', []))
    skip_dirs = set(rule.get('skip_dirs', []))
    skip_suf = tuple(rule.get('skip_suffixes', []))
    base = ROOT if rule.get('scope') == 'repo' else TREE
    for p in base.rglob('*'):
        if not p.is_file() or skip_dirs & set(p.parts):
            continue
        r = p.relative_to(base).as_posix()
        if allow and r.endswith(allow):
            continue
        if p.suffix in skip_suf:
            continue
        try:
            txt = p.read_text(encoding='utf-8')
        except Exception:
            continue
        for t in terms:
            if t in txt:
                yield '%s: %s' % (r, msg.format(term=t))


# ─────────────────────────── VaultPatcher 检查器 ───────────────────────────

def vp_modules():
    out = []
    for p in sorted((TREE / 'vaultpatcher' / 'modules').glob('*.json')):
        try:
            out.append((p, json.loads(p.read_text(encoding='utf-8'))))
        except Exception:
            out.append((p, None))
    return out


def vp_pairs(only_risky=False):
    """产出 (文件名, target_class, 原文, 译文)。

    `only_risky`：只要**可能命中 McJtyLib 枚举常量池**的块——无 target_class 的
    全局替换，或定向到 mcjty.* 的非 client 类（枚举/协议类所在地）。
    定向到具体 GUI/Screen 类的同名显示标签（形状卡的 Solid）是安全的。
    """
    for p, mod in vp_modules():
        if not isinstance(mod, list):
            continue
        for blk in mod:
            if not isinstance(blk, dict):
                continue
            tcs = blk.get('target_class') or []
            if only_risky:
                risky = (not tcs) or any(
                    c.startswith('mcjty.') and '.client.' not in c for c in tcs)
                if not risky:
                    continue
            for pair in blk.get('pairs', []):
                yield p.name, tcs, pair.get('key', ''), pair.get('value', '')


@checker('vp_shape')
def _vp_shape(rule):
    for p, mod in vp_modules():
        if mod is None:
            yield '%s: JSON 解析失败' % p.name
        elif not isinstance(mod, list):
            yield '%s: 顶层必须是数组' % p.name
        else:
            for blk in mod:
                if not isinstance(blk, dict):
                    yield '%s: 模块元素必须是对象' % p.name


@checker('vp_pair_key_in')
def _vp_pair_key_in(rule):
    vals, = need(rule, 'values')
    vals = set(vals)
    msg = rule.get('message', '禁止替换 {key}')
    for name, tcs, k, v in vp_pairs(rule.get('only_risky_blocks', False)):
        if k.strip() in vals:
            where = '全局替换' if not tcs else '定向 %s' % tcs
            yield '%s: %s' % (name, msg.format(key=repr(k), value=repr(v), where=where))


@checker('vp_pair_regex')
def _vp_pair_regex(rule):
    pat, = need(rule, 'key_regex')
    rx = re.compile(pat)
    msg = rule.get('message', '原文 {key} 不许被替换成 {value}')
    for name, _tcs, k, v in vp_pairs():
        if not rx.match(k):
            continue
        if rule.get('value_has_cjk') and not CJK.search(v):
            continue
        yield '%s: %s' % (name, msg.format(key=repr(k), value=repr(v)))


@checker('vp_server_global')
def _vp_server_global(rule):
    lst, = need(rule, 'list')
    names = [l.strip() for l in (ROOT / lst).read_text(encoding='utf-8').splitlines()
             if l.strip() and not l.startswith('#')]
    for name in names:
        p = TREE / 'vaultpatcher' / 'modules' / ('%s.json' % name)
        if not p.exists():
            yield '%s: 清单里的 %s.json 不存在' % (lst, name)
            continue
        for blk in json.loads(p.read_text(encoding='utf-8')):
            if isinstance(blk, dict) and 'pairs' in blk and not blk.get('target_class'):
                bad = [pr['key'] for pr in blk['pairs']
                       if not pr.get('key', '').startswith(' ')]
                if bad:
                    yield ('%s.json: 服务端模块含全局替换 %s'
                           '（会污染服务端数据，禁止入服务端清单）' % (name, bad))


@checker('vp_keybind_names')
def _vp_keybind_names(rule):
    g, = need(rule, 'data_glob')
    data = sorted(ROOT.glob(g))
    if not data:
        # 这条**不看 GATE_STRICT，一律红**：它的前提不是生成物，是入库的
        # （versions/db/*/keybinds.json 三个版本都在 git 里）。而 protect.py 的
        # 保护范围只有 src/，versions/ 不在里面——真被删了没有别的闸兜得住。
        yield ('按键注册名检查没跑成：%s 一个都没命中。这些文件是入库的，'
               '不是生成物，缺了说明被删/被挪走了（跑 scan_keybinds.py 重建）' % g)
        return
    names = set()
    for p in data:
        d = json.loads(p.read_text(encoding='utf-8'))
        names |= set(d.get('names', {}))
        names |= set(d.get('name_atoms', {}))
    msg = rule.get('message', '原文 {key} 是按键注册名')
    for name, _tcs, k, v in vp_pairs():
        if k in names:
            yield '%s: %s' % (name, msg.format(key=repr(k), value=repr(v)))


@checker('vp_value_conflict')
def _vp_value_conflict(rule):
    """同一个类、同一条原文、同一种匹配模式，只许有一种译文。

    一条 pair 有两种模式：value 以 `@` 开头是**子串替换**，其余是**全串匹配**
    （见 compliance/check_minecolonies_paths.py 里对 MatchUtils 的还原）。所以
    `Fortress→要塞` 与 `Fortress→@要塞` 是两种模式，成对出现是对的，不算冲突。

    真冲突是同类同原文同模式下有两句不同的译文：哪句生效取决于模块加载顺序
    与表内顺序，本机看到的和玩家看到的可以不是同一句，而且改了其中一句还查不出
    为什么没生效。2026-08-07 rftoolsbase.json 与 rftoolsbase_filter_zh.json 对同一个
    GuiFilterModule 的三条原文各写了一套译文（「忽略耐久值」对「忽略损伤值」等）。
    """
    seen = {}
    total = 0
    for name, tcs, k, v in vp_pairs():
        total += 1
        sub = v.startswith('@')
        scope = tuple(sorted(tcs)) if tcs else ('<全局替换>',)
        seen.setdefault((scope, k, sub), {}).setdefault(v[1:] if sub else v, set()).add(name)
    if not total:
        yield 'vaultpatcher/modules 一条 pair 都没读到（规则失效了，比不加还危险）'
        return
    for (scope, k, sub), vs in sorted(seen.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if len(vs) < 2:
            continue
        where = '；'.join('%r ← %s' % (t, ','.join(sorted(fs))) for t, fs in sorted(vs.items()))
        yield ('%s 的原文 %r（%s）有 %d 种译文：%s'
               % (scope[0], k, '子串替换' if sub else '全串匹配', len(vs), where))


@checker('term_binding')
def _term_binding(rule):
    """英文词与中文词双向绑定：原文出现其一，译文就必须出现其二，反之亦然。

    专治「两个名字长得像的东西被互相译反」——这种错单看一条译文是通顺的，
    只有把原文和译文绑起来才拦得住。2026-08-07：ExpandedAE 的两张升级卡把
    Extended（AE2扩展的，mcmod 作 ME扩展样板供应器）译成「拓充」、把 Expanded
    （ExpandedAE 的，jar 自带中文作 拓充样板供应器）译成「拓展」，正好对调，
    而两句话各自读起来都没毛病。
    """
    terms, = need(rule, 'terms')
    scope = rule.get('files')            # 文件名清单；缺省 = 全表
    hits = {t['en']: 0 for t in terms}
    total = 0
    for name, _tcs, k, v in vp_pairs():
        if scope and name not in scope:
            continue
        total += 1
        for t in terms:
            in_en = t['en'].lower() in k.lower()
            in_zh = t['zh'] in v
            if in_en:
                hits[t['en']] += 1
            if in_en and not in_zh:
                yield ('%s: 原文含 %r，译文 %r 里却没有 %r' % (name, t['en'], v, t['zh']))
            elif in_zh and not in_en:
                yield ('%s: 译文含 %r，原文 %r 里却没有 %r' % (name, t['zh'], k, t['en']))
    if not total:
        yield ('files %r 一条 pair 都没读到（规则失效了，比不加还危险）'
               % (scope if scope else 'vaultpatcher/modules/*.json',))
        return
    for e, c in sorted(hits.items()):
        if not c:
            yield ('原文里一次都没出现过 %r —— 上游改了措辞或这些 pair 被挪走了，'
                   '这条绑定已经形同虚设' % e)


# ─────────────────────────────── 资源包检查器 ───────────────────────────────

@checker('tiered_family')
def _tiered_family(rule):
    """同一族的 N 档：词干必须完全相同，档位后缀写法必须全表统一。

    AllTheCompressed 有 1796 条这样的键（`_1x`..`_9x` 九档一族）。因为没有任何
    规则约束，同一族里曾经混着「1x荒古石」「荒古石 6x」「三重压缩荒古石」
    好几种写法，而且各档的词干本身也能飘（振动合金块与脉冲合金块一字不差）。
    键名带档位号，词干和后缀就都是可推导的，那就不该靠人记。
    """
    g, kr, tpl = need(rule, 'glob', 'key_regex', 'value_template')
    rx = re.compile(kr)
    hit = files(g)
    if not hit:
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
        return
    total = 0
    for p in hit:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            yield '%s: JSON 解析失败: %s' % (rel(p), e)
            continue
        fam = {}
        for k, v in sorted(d.items()):
            m = rx.match(k)
            if not m:
                continue
            total += 1
            fam.setdefault(m.group('stem'), []).append((k, m.group('tier'), v))
        for stem, items in sorted(fam.items()):
            roots = {}
            for k, tier, v in items:
                tail = tpl.format(tier=tier)
                if not v.endswith(tail):
                    yield ('%s: %s 的译文 %r 不是「词干+%r」的写法'
                           % (rel(p), k, v, tail))
                    continue
                roots.setdefault(v[:-len(tail)], []).append(k)
            if len(roots) > 1:
                yield ('%s: %s 这一族 %d 档的词干不一致：%s'
                       % (rel(p), stem, len(items),
                          '、'.join('%r(%s)' % (r, ks[0].rsplit('.', 1)[-1])
                                    for r, ks in sorted(roots.items()))))
    if not total:
        yield 'key_regex %r 一个键都没命中（规则失效了，比不加还危险）' % kr


@checker('gui_choice_ascii')
def _gui_choice_ascii(rule):
    g, = need(rule, 'glob')
    msg = rule.get('message', "choice('{value}') 必须保持英文")
    hit = files(g)
    if not hit:
        # 和 json_parses 同款自爆：一个文件都没命中说明源文件被挪走/删了，
        # 闸会跟着静默消失——比不加闸更危险。（2026-07-28 对抗审计指出的不一致）
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        text = p.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r"choice\(\s*'([^']*)'", text):
            if CJK.search(m.group(1)):
                yield '%s: %s' % (rel(p), msg.format(value=m.group(1)))


@checker('format_safety')
def _format_safety(rule):
    snap, = need(rule, 'snapshot')
    f = ROOT / snap
    if not f.exists():
        m = absent('占位符检查', '还没有 %s（gen_format_snapshot.py 要读 mod jar 才能产出）' % snap)
        if m:
            yield m
        return
    up = json.loads(f.read_text(encoding='utf-8'))
    allow = set(rule.get('allow', {}))
    TOK = re.compile(r'%(?:(\d+)\$)?(\d+)?(?:\.(\d+))?([a-zA-Z%])')
    TRAIL = re.compile(r'(?<!%)%$')
    SECT_OK = set('0123456789abcdefklmnorABCDEFKLMNOR')

    def profile(s):
        prof, seq = {}, 0
        for m in TOK.finditer(s):
            if m.group(4) == '%':
                continue
            if m.group(1):
                idx = int(m.group(1))
            else:
                seq += 1
                idx = seq
            prof.setdefault(idx, m.group(4))
        return prof

    def bad_sect(s):
        return {m.group(1) for m in re.finditer('§(.)', s) if m.group(1) not in SECT_OK}

    lang = list(PACK_DIR.rglob('lang/zh_cn.json'))
    lang += list((TREE / 'kubejs' / 'assets').rglob('lang/zh_cn.json'))
    for p in lang:
        r = rel(p)
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue                       # json_parses 那条已经报过了
        for k, zh in d.items():
            if not isinstance(zh, str) or k == '_comment' or k in allow:
                continue
            en = up.get(k)
            if en is None:
                continue
            pe, pz = profile(en), profile(zh)
            extra = sorted(set(pz) - set(pe))
            if extra:
                yield ('%s: %s 译文多出英文没有的占位符 %s（运行时参数不足会抛 '
                       'TranslatableFormatException）\n      en=%r\n      zh=%r'
                       % (r, k, extra, en, zh))
            down = sorted(i for i in set(pe) & set(pz) if pe[i] == 's' and pz[i] != 's')
            if down:
                yield ('%s: %s 第 %s 个参数把 %%s 降级成了 %%%s（类型对不上，必炸）'
                       '\n      en=%r\n      zh=%r' % (r, k, down, pz[down[0]], en, zh))
            if TRAIL.search(zh) and not TRAIL.search(en):
                yield '%s: %s 译文以裸 %% 结尾（MC 会当非法格式抛异常）\n      zh=%r' % (r, k, zh)
            new_sect = bad_sect(zh) - bad_sect(en)
            if new_sect:
                yield ('%s: %s 非法 § 颜色码 %s（§ 后面那个字会被渲染器吞掉）'
                       '\n      zh=%r' % (r, k, sorted(new_sect), zh))


@checker('pb_single_source')
def _pb_single_source(rule):
    lang, script = need(rule, 'lang', 'script')
    lp, sp = TREE / lang, TREE / script
    if not lp.is_file():
        yield '缺少 %s' % lang
        return
    pack = json.loads(lp.read_text(encoding='utf-8'))
    if not sp.exists():
        m = absent('蜂名漂移检查', '%s 是生成物，尚未生成' % script)
        if m:
            yield m
        return
    m = re.search(r'const PB_ID2ZH = (\{.*?\});', sp.read_text(encoding='utf-8'), re.S)
    if not m:
        yield '%s: 缺 PB_ID2ZH（必须由 gen_pb_hanhua.py 生成）' % script
        return
    for base, zh in json.loads(m.group(1)).items():
        expect = pack.get('entity.productivebees.%s_bee' % base,
                          pack.get('entity.productivebees.%s' % base))
        if expect is not None and expect != zh:
            yield ('蜂名漂移: %s 脚本=%r 资源包=%r'
                   '（真源是资源包，请重跑 gen_pb_hanhua.py）' % (base, zh, expect))


# ─────────────────────────────── 任务书检查器 ───────────────────────────────

@checker('snbt_blocks_parse')
def _snbt_blocks_parse(rule):
    """delta 文件必须能被**生成器那个**块解析器完整读通。

    2026-08-02：给 delta 排序时按行 sort，把 129 个多行数组打散成 513 个游离的
    `\t\t""`。ci.yml 全绿——因为 check.py 当时只有按行的正则检查，匹配不上的行
    直接跳过；三分钟后才被真正调用 blocks() 的 build.yml 拦下。

    所以这里**不另写一份解析器**，直接 import 生成器用的那个：两份判得不一样，
    就等于闸判绿、生成阶段判红，跟没有闸没区别。
    """
    from gen_quest_lang_patches import SnbtShapeError, blocks

    g, = need(rule, 'glob')
    # **只查结构，不查有没有键。** 空文件在这里是合法的，而且往往是正确终态：
    # gen_quest_lang_patches.py 把覆盖打进上游文件之后，会照原名发一个 `{\n}` 空壳
    # 去盖掉玩家硬盘上的旧 delta（安装器只覆盖不删除）。所以同一条规则在
    # ci.yml（生成之前，delta 带着键）和 build.yml（生成之后，delta 全是空壳）
    # 看到的是两个世界——「一个键都没有」在后者是 35 个文件全中。
    hit = files(g)
    if not hit:
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
        return
    for p in hit:
        try:
            blocks(p)
        except SnbtShapeError as e:
            yield '%s' % e


@checker('snbt_no_dup_keys')
def _snbt_no_dup_keys(rule):
    g, = need(rule, 'glob')
    # 上游那批文件缩进不统一（同一个 chapters/ 里既有 tab 也有 4 空格），
    # 只认 tab 会漏掉一整个文件的键——漏掉就等于这条闸对它不设防
    KEY = re.compile(r'^[\t ]+([A-Za-z0-9_.]+):\s*(.*)$')
    seen = {}
    hit = files(g)
    if not hit:
        # 和 json_parses/gui_choice_ascii/filename_prefix 同款自爆：一个文件都没命中
        # 说明任务书 delta 目录被挪走/改名/生成步骤漏跑了，这条闸会跟着静默消失
        # ——比不加闸更危险。（2026-07-28 对抗审计第二轮指出本检查器唯独漏了这层）
        yield 'glob %r 一个文件都没命中（规则失效了，比不加还危险）' % g
    for p in hit:
        lines = p.read_text(encoding='utf-8').split('\n')
        i = 0
        while i < len(lines):
            m = KEY.match(lines[i])
            if m:
                k, rest = m.group(1), m.group(2)
                bal = rest.count('[') - rest.count(']')
                while bal > 0 and i + 1 < len(lines):        # 跨行数组
                    i += 1
                    bal += lines[i].count('[') - lines[i].count(']')
                if k in seen:
                    yield ('任务书 delta 重复键 %s：%s 与 %s 都定义了'
                           '（哪份生效取决于合并顺序，必须只保留一份）'
                           % (k, seen[k], p.name))
                seen[k] = p.name
            i += 1


# ─────────────────────────────── 解释器 ───────────────────────────────

def load_rules():
    if not RULES_DIR.is_dir():
        sys.exit('❌ 规则目录不存在: %s' % RULES_DIR)
    rules = []
    for f in sorted(RULES_DIR.glob('*.json')):
        try:
            got = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            sys.exit('❌ 规则文件 %s 解析失败: %s' % (f.name, e))
        if not isinstance(got, list):
            sys.exit('❌ 规则文件 %s 顶层必须是数组' % f.name)
        for r in got:
            r['_file'] = f.name
            rules.append(r)
    ids = [r.get('id') for r in rules]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        sys.exit('❌ 规则 id 重复: %s' % dup)
    for r in rules:
        for k in ('id', 'kind', 'why'):
            if not r.get(k):
                sys.exit('❌ %s 里有规则缺 %s 字段: %r' % (r['_file'], k, r))
        if r['kind'] not in CHECKERS:
            # 认不出的 kind 必须让校验红，否则打错一个字母规则就静默失效了
            sys.exit('❌ 规则 %s 的 kind %r 没有对应的检查器；已有: %s'
                     % (r['id'], r['kind'], ' '.join(sorted(CHECKERS))))
    return rules


def main():
    if not TREE.is_dir():
        sys.exit('❌ 出货树不存在: %s\n'
                 '   先跑: python3 scripts/assemble.py && ./scripts/generate_all.sh' % TREE)
    rules = load_rules()
    errors = []
    for r in rules:
        try:
            errors += ['[%s] %s' % (r['id'], e) for e in CHECKERS[r['kind']](r)]
        except Exception as e:
            errors.append('[%s] 检查器自身出错: %r' % (r['id'], e))
    if errors:
        print('❌ 校验失败，共 %d 处：' % len(errors))
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('✅ %d 条规则全部通过：%s'
          % (len(rules), ' '.join(r['id'] for r in rules)))


if __name__ == '__main__':
    main()
