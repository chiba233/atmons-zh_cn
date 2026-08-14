@echo off
REM atm10-zh-cn - Simplified Chinese localization patch for All the Mods 10
REM Copyright (C) 2026 Hoshino Yumeka
REM SPDX-License-Identifier: GPL-3.0-or-later
REM
REM Keep this file pure ASCII with CRLF line endings.
REM cmd.exe parses .bat bytes in the OEM code page; non-ASCII bytes here would
REM be mis-decoded, and switching code pages mid-file can desync the parser.
setlocal
REM Capture the script directory BEFORE chcp: cmd re-reads the batch file by byte
REM offset, and a code page switch can corrupt later expansions on non-ASCII paths.
set "DIR=%~dp0"
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%DIR%install.ps1"
pause
