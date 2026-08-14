#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# atmons-zh-cn — All the Mons 简体中文汉化补丁
# Copyright (C) 2026 星野夢華 (Hoshino Yumeka)
# SPDX-License-Identifier: GPL-3.0-or-later
"""按 `src/mods.lock.json` 把随包分发的第三方 jar 取下来，逐个核 sha256。

仓库里不放二进制。锁文件写死了「哪个项目、哪个版本、什么地址、什么哈希」，
构建时现取——**哈希对不上就退出**，不会把一个来路不明的 jar 打进包里。

下载缓存在 `build/modcache/<sha256>.jar`，重复构建不重复下。

**全部**随包 jar 都走这条路，包括只在 CurseForge 上有的 JEI 拼音搜索
（jecharacters）。之前那一个是入库的，理由写的是「CurseForge 接口挡机器人」——
搜索接口确实挡，但 `/api/v1/mods/<id>/files` 与 `/files/<id>/download` 是通的，
按 fileID 就能钉死地址。同一个项目里两套标准没有道理。

许可证正文也一并取：MIT 的唯一实质义务就是再分发时附上版权声明与许可全文，
jar 里没带，那就由我们放到它旁边。

用法:
    python3 scripts/fetch_mods.py <输出目录>       # 一般是 build/common
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

from paths import BUILD, ROOT, SRC

LOCK = SRC / 'mods.lock.json'
CACHE = BUILD / 'modcache'
UA = {'User-Agent': 'atm10-zh-cn/1.0 (+https://github.com/chiba233/atm10-zh-cn)'}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return r.read()


def main(out_dir):
    if not LOCK.is_file():
        sys.exit('❌ 没有 %s' % LOCK)
    lock = json.loads(LOCK.read_text(encoding='utf-8'))
    out = Path(out_dir)
    CACHE.mkdir(parents=True, exist_ok=True)
    for rel, info in sorted(lock.items()):
        want = info['sha256']
        cached = CACHE / (want + '.jar')
        if not cached.exists():
            data = get(info['url'])
            got = sha256(data)
            if got != want:
                sys.exit('❌ %s 哈希对不上——**不要用这个文件**\n'
                         '   期望 %s\n   实得 %s\n   地址 %s\n'
                         '   要么上游把同一个地址的内容换了，要么下载被人动了手脚。'
                         % (rel, want, got, info['url']))
            cached.write_bytes(data)
        else:
            # 缓存也要复核：磁盘上的东西同样可能被改
            if sha256(cached.read_bytes()) != want:
                cached.unlink()
                sys.exit('❌ 缓存 %s 哈希对不上，已删除，请重跑' % cached)
        t = out / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(cached.read_bytes())
        # MIT / Apache 这类许可要求再分发时附许可全文，jar 里没带就由我们放
        if info.get('license_file'):
            # 仓库里已经有这份许可证正文（GPL-3.0 就是本项目代码用的那份），
            # 没有理由再去网上取——出货构建跑在锁定容器里，少一个网络依赖少一个
            # 挂点。gnu.org 在容器里就取不到，Build 一直红在这儿。
            #
            # 但「本项目也用同一个许可证」不等于这份文件可以带本项目的版权声明：
            # 它是随**别人的** jar 一起分发的，掺进「Copyright (C) …」就成了替
            # 别人的作品声明作者。所以正文必须逐字节等于许可证原文，拿哈希钉死。
            src = ROOT / info['license_file']
            data = src.read_bytes()
            want_lic = info.get('license_file_sha256')
            if not want_lic:
                sys.exit('❌ %s 记了 license_file，却没记 license_file_sha256' % rel)
            if sha256(data) != want_lic:
                sys.exit('❌ %s 的许可证正文 %s 哈希对不上\n'
                         '   期望 %s\n   实得 %s\n'
                         '   这份文件随第三方 jar 分发，必须是许可证原文本身，'
                         '不得掺入本项目的版权声明。'
                         % (rel, info['license_file'], want_lic, sha256(data)))
            (t.parent / ('LICENSE-%s.txt' % info.get('project', 'third-party'))
             ).write_bytes(data)
        elif info.get('license_url'):
            lic = CACHE / (info['license_sha256'] + '.txt')
            if not lic.exists():
                data = get(info['license_url'])
                if sha256(data) != info['license_sha256']:
                    sys.exit('❌ %s 的许可证正文哈希对不上' % rel)
                lic.write_bytes(data)
            (t.parent / ('LICENSE-%s.txt' % info.get('project', 'third-party'))
             ).write_bytes(lic.read_bytes())
        print('  %-28s %s %s (%d KB)'
              % (rel, info.get('project', ''), info.get('version', ''),
                 len(cached.read_bytes()) // 1024))
    print('随包 jar：%d 个，sha256 全部核对通过' % len(lock))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
