#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""**保护清单** —— src/ 下的东西，只许加，不许悄悄少。

为什么要有这个文件：这个仓库被删过 1033 个文件，分四笔，全部是我
（写这段代码的 AI）自己论证出一套「这批是上游死重 / 游戏根本不读 / 会自动
回落到英文」的理由之后动手删的，事后逐笔回滚。历史里已经有两笔专门的
「救回」提交（`6d37e00` 捞回 104 条、`72a5cc8` 救回 oracle_index），
那本身就是那套理由不成立的证据。

问题不在于「查得不够仔细」，在于**同一条推理链既当证据又当裁判**——
下一次换个上下文、忘掉这段历史，同样的理由会被重新论证一遍。所以拦它的
不能是记忆或自觉，只能是一道机械闸：

    清单里有的路径，文件必须在。不在，CI 直接红。

要真删，必须在 `released` 里留一条**永久记录**（谁批的、什么理由、哪天），
而且这条记录以后不许再被抹掉。也就是说删除这件事在版本库里**留疤**，
review 的时候一眼能看见，而不是混在一笔「清理」提交的 500 个文件里。

用法:
    python3 scripts/protect.py --check     # CI 用；少一个文件就退出 1
    python3 scripts/protect.py --update    # 新增汉化后跑一次，把新文件收进清单
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # scripts/ 下的公共模块

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST = ROOT / 'src' / 'protected.json'
# 保护范围就是整个 src/：这里放的全是汉化源，没有一个是生成物
# （出货树 kubejs/ config/ resourcepacks/ mods/ 都是构建时现摊的）。
# 不按类型挑，也就没有「这个算不算汉化」可争的余地。
SCOPE = 'src/'

HEADER = ('src/ 下的文件只许加不许删。要删必须挪进 released 并写明谁批的、'
          '为什么——见 scripts/protect.py 顶部。')


MANIFEST_REL = 'src/protected.json'


def git(*args):
    """跑一条 git，取不到就返回 None——**绝不抛异常**。

    出货构建跑在容器里，仓库的 owner 与容器里的 uid 不同，git 会以
    `detected dubious ownership` 退 128。第一版没兜这个，闸自己崩成一个
    traceback：那等于「闸坏了」和「真删了文件」长得一模一样，最坏的结果。
    所以 safe.directory 先放开，仍失败就降级——最要紧的那条
    「清单里的文件必须在」是纯文件系统检查，不依赖 git，任何情况下都跑。
    """
    r = subprocess.run(['git', '-c', 'safe.directory=*',
                        '-c', 'core.quotepath=false', *args],
                       cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def tracked():
    """git 认得的 src/ 下全部文件；git 用不了则返回 None。

    清单自己也在 src/ 下，所以它也进清单——把清单删掉同样要红。
    刚跑第一次 --update 时它还没被 git add，得手动补上，否则下一次
    --check 会反过来说「这个文件没收进清单」。
    """
    out = git('ls-files', SCOPE)
    if out is None:
        return None
    return sorted(set(p for p in out.splitlines() if p) | {MANIFEST_REL})


def load(text):
    d = json.loads(text)
    return d, set(d.get('protected') or []), {r['path'] for r in (d.get('released') or [])}


def read_manifest():
    if not MANIFEST.is_file():
        return {'_说明': HEADER, 'protected': [], 'released': []}, set(), set()
    return load(MANIFEST.read_text(encoding='utf-8'))


ABSENT = 'absent'      # 那个提交上还没有清单这个文件
BROKEN = 'broken'      # 有文件但解析不了


def at(rev):
    """某个提交上的清单，或 ABSENT / BROKEN。

    这两种要分开：「那时还没有这个文件」是正常的（清单是后来引入的），
    「有文件但解析不了」不正常，不许当没事。
    """
    out = git('show', '%s:%s' % (rev, MANIFEST_REL))
    if out is None:
        return ABSENT
    try:
        return load(out)
    except Exception:                                          # noqa: BLE001
        return BROKEN


def have(rev):
    return git('rev-parse', '--verify', '--quiet', rev + '^{commit}') is not None


def base_rev():
    """跟哪一版比，返回 `(rev, 可以跳过的理由)`。

    rev 有值就一定解析得出来。rev 为 None 且理由为 None = **取不到**，
    调用方必须按失败处理，不许静默跳过——见 check() 里第 3 条的注释。

    浅克隆是常态而不是意外：CI 的 checkout 只要几层，而 `github.event.before`
    可能落在更早的提交上（一次 push 好几笔就会）。所以取不到先按需补取一个，
    补不到才算取不到。
    """
    raw = (os.environ.get('PROTECT_BASE') or '').strip()
    if raw and set(raw) == {'0'}:
        # github.event.before 在新建分支的首次 push 上是全零，确实没有上一版
        return None, '上一版是全零 sha（新建分支的首次 push），没有可比的清单'
    rev = raw or 'HEAD~1'
    if have(rev):
        return rev, None
    # 只对看着像 sha 的做补取：HEAD~1 这种相对引用 fetch 不了
    if len(rev) >= 7 and all(c in '0123456789abcdefABCDEF' for c in rev):
        git('fetch', '--quiet', '--depth=1', 'origin', rev)
        if have(rev):
            return rev, None
    return None, None


def update():
    d, prot, rel = read_manifest()
    now = tracked()
    if now is None:
        print('❌ git 用不了，列不出 src/ 下有哪些文件——清单不能凭空更新')
        return 1
    add = [p for p in now if p not in prot and p not in rel]
    d['_说明'] = HEADER
    d['protected'] = sorted(prot | set(add))
    d.setdefault('released', [])
    MANIFEST.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8')
    print('保护清单：%d 个文件（新收 %d 个）' % (len(d['protected']), len(add)))
    for p in add[:20]:
        print('   + %s' % p)
    if len(add) > 20:
        print('   … 还有 %d 个' % (len(add) - 20))
    return 0


def check():
    d, prot, rel = read_manifest()
    if not prot:
        print('❌ src/protected.json 是空的或不存在——先跑 --update')
        return 1
    bad = []

    # 1. 清单里的文件必须还在，且不是空壳
    gone = [p for p in sorted(prot) if not (ROOT / p).is_file()]
    empty = [p for p in sorted(prot)
             if (ROOT / p).is_file() and (ROOT / p).stat().st_size == 0]
    if gone:
        bad.append(('这些文件在保护清单里，但已经从仓库消失', gone))
    if empty:
        bad.append(('这些文件还在，但是空的', empty))

    # 2. src/ 下新加的文件必须收进清单，否则保护范围会被「新增的不算」蚕食
    now = tracked()
    if now is None:
        # 本地/奇怪环境里降级放过（出货容器曾因 dubious ownership 让闸崩成
        # traceback，那比漏查更坏）。但**流水线里必须红**：git 一用不了，第 2、3
        # 两条就一起静默关掉，而「删文件 + 从清单抹掉」只有第 3 条能拦。
        # 真出过这个事故：build.yml 的容器镜像里没有 git，checkout 检测不到 git
        # 就退化成 REST API 下 tarball，压根不建 .git 目录——于是这两条闸在出货
        # 流水线里一次都没跑过，而闸照样退 0。所以工作流一律传 PROTECT_REQUIRE_GIT=1。
        if (os.environ.get('PROTECT_REQUIRE_GIT') or '').strip() not in ('', '0'):
            bad.append(('git 用不了，「新增必须登记」与「清单不许变短」两条没跑成——'
                        '本环境声明了 PROTECT_REQUIRE_GIT，按失败处理。'
                        '常见成因：容器里没装 git，checkout 退化成 REST API 下 tarball，'
                        '没有 .git 目录', ['git ls-files %s 失败' % SCOPE]))
        else:
            print('ℹ️ git 用不了（容器里的 ownership 之类），跳过「新增必须登记」'
                  '与「清单不许变短」两条；上面那条「文件必须在」已经查过了')
    else:
        miss = [p for p in now if p not in prot and p not in rel]
        if miss:
            bad.append(('这些文件在 src/ 里但不在保护清单里——跑 --update 收进去', miss))

    # 3. 防洗白：清单本身也不许悄悄变短。
    #    上一版清单里出现过的路径，现在必须仍在 protected 或 released 里。
    #    想删文件？可以，但必须在 released 留下一条永久记录。
    #
    #    这条**取不到 base 就必须红**。早先是打一行 ℹ️ 然后返回成功，于是
    #    ci.yml（fetch-depth: 2，而 github.event.before 在三笔之外）和
    #    build.yml（checkout 默认 depth 1，HEAD~1 根本不存在）里这条一直没跑成，
    #    而闸退 0——「闸没跑」和「查过了没问题」长得一模一样。同时删文件 + 从清单
    #    抹掉的那种洗白改动，正好撞上浅克隆就会整个漏过去。
    #    git 完全用不了是另一码事，上面第 2 条已经整段跳过并说明了。
    if now is not None:
        rev, skip_why = base_rev()
        if rev:
            prev = at(rev)
            if prev is ABSENT:
                print('ℹ️ %s 上还没有 %s，跳过「清单不许变短」这一条' % (rev, MANIFEST_REL))
            elif prev is BROKEN:
                bad.append(('上一版的保护清单解析不出来，没法比对——不许当没事', [rev]))
            else:
                _, pprot, prel = prev
                lost = sorted((pprot | prel) - (prot | rel))
                if lost:
                    bad.append(('保护清单自己被改短了——这些路径上一版还在，现在两边都查无此条',
                                lost))
        elif skip_why:
            print('ℹ️ %s，跳过「清单不许变短」这一条' % skip_why)
        else:
            bad.append((
                '取不到用来比对的上一版，「清单不许变短」这条没跑成——按失败处理。'
                '克隆里没有这个提交，--depth=1 补取也失败。'
                'CI 里请把 checkout 的 fetch-depth 设为 0',
                ['PROTECT_BASE=%s' % (os.environ.get('PROTECT_BASE') or '(未设，回落 HEAD~1)')]))

    # 4. released 必须写清楚谁批的、为什么。没有理由的放行不算放行。
    for r in (d.get('released') or []):
        if not str(r.get('why', '')).strip() or not str(r.get('approved', '')).strip():
            bad.append(('released 里这条没写 approved / why，不算有效放行',
                        [json.dumps(r, ensure_ascii=False)]))

    if not bad:
        print('✅ 保护清单：%d 个文件全部在位（另有 %d 个经批准放行）'
              % (len(prot), len(rel)))
        return 0
    for title, items in bad:
        print('\n❌ %s（%d 个）：' % (title, len(items)))
        for p in items[:30]:
            print('     %s' % p)
        if len(items) > 30:
            print('     … 还有 %d 个' % (len(items) - 30))
    print('\n' + '=' * 72)
    print('src/ 下的汉化只许加不许删。这个仓库因为「我觉得这批没用」被删过 1033 个')
    print('文件，每一笔都回滚了。如果你（AI）又想删：**停下，去问用户**。')
    print('确实获批了，就把路径挪进 src/protected.json 的 released，写上 approved 与 why。')
    print('=' * 72)
    return 1


if __name__ == '__main__':
    if '--update' in sys.argv:
        sys.exit(update())
    if '--check' in sys.argv:
        sys.exit(check())
    sys.exit(__doc__)
