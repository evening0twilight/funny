#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doctor.py —— 全项目体检

为什么要有它：
    文档可以写得很漂亮，但规则不落到机器上就一定会被违反。
    这个脚本检查「结构 / 引用 / 跨日 / 脏文件」，提交前跑一次。

用法：
    python3 tools/doctor.py
    python3 tools/doctor.py --strict     # 把警告也当失败
"""
from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Asia/Shanghai")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors: list[str] = []
warns: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


# ----------------------------------------------------------------- 1. 结构
def check_structure() -> None:
    must = [
        "README.md", "CONVENTIONS.md",
        "docs/daily-sop.md", "docs/handoff.md",
        "tools/aihot_fetch.py", "tools/topic_score.py",
        "tools/new_day.py", "tools/doctor.py",
        "skills/ai-news-content/SKILL.md",
        "data/hot-trends.md",
    ]
    for rel in must:
        if not (ROOT / rel).exists():
            err(f"缺少必备文件：{rel}")

    for base in ("data/raw", "out"):
        p = ROOT / base
        if not p.exists():
            warn(f"目录不存在（还没开工？）：{base}/")
            continue
        for d in p.iterdir():
            if d.is_dir() and not DATE_RE.match(d.name):
                err(f"{base}/ 下有非日期目录：{d.name}（规范要求 YYYY-MM-DD）")


# ----------------------------------------------------------------- 2. 引用
def check_skill_refs() -> None:
    skill = ROOT / "skills/ai-news-content"
    sk = skill / "SKILL.md"
    if not sk.exists():
        return
    text = sk.read_text(encoding="utf-8")
    refs = set(re.findall(r"`((?:references|assets|scripts)/[^`]+\.(?:md|py))`", text))
    for r in sorted(refs):
        if not (skill / r).exists():
            err(f"SKILL.md 引用了不存在的文件：{r}")

    # 反向：references 下每个文件都该被 SKILL.md 索引
    ref_dir = skill / "references"
    if ref_dir.exists():
        for f in sorted(ref_dir.glob("*.md")):
            if f"references/{f.name}" not in text and f.name != "arcloop-models.md":
                warn(f"references/{f.name} 未被 SKILL.md 索引")


# ----------------------------------------------------------------- 3. 编译
def check_scripts() -> None:
    files = list((ROOT / "tools").glob("*.py")) + list((ROOT / "skills/ai-news-content/scripts").glob("*.py"))
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True, cfile=str(ROOT / ".doctor.tmpc"))
        except py_compile.PyCompileError as e:
            err(f"脚本编译失败：{f.relative_to(ROOT)} — {e.msg}")
        finally:
            tmp = ROOT / ".doctor.tmpc"
            if tmp.exists():
                tmp.unlink()


# ----------------------------------------------------------------- 4. 跨日（防串日核心）
def check_cross_day() -> None:
    out = ROOT / "out"
    if not out.exists():
        return
    for day in sorted(d for d in out.iterdir() if d.is_dir() and DATE_RE.match(d.name)):
        topic = day / "00-当日选题.md"
        if not topic.exists():
            warn(f"out/{day.name}/ 缺少 00-当日选题.md")
        for f in day.rglob("*.md"):
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"data/raw/(\d{4}-\d{2}-\d{2})", text):
                ref = m.group(1)
                if ref != day.name:
                    err(f"跨日引用：{f.relative_to(ROOT)} 引用了 data/raw/{ref}（本目录是 {day.name}）")

        # material.json 路径是否存在
        for f in day.rglob("*.md"):
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"(data/raw/[\w\-./]+material\.json)", text):
                if not (ROOT / m.group(1)).exists():
                    warn(f"{f.relative_to(ROOT)} 引用的素材卡不存在：{m.group(1)}")


# ----------------------------------------------------------------- 5. 脏文件
def check_junk() -> None:
    junk: list[str] = []
    for pat in ("**/__pycache__", "**/.DS_Store", "tmp", "data/.cache"):
        junk.extend(str(p.relative_to(ROOT)) for p in ROOT.glob(pat))
    if junk:
        warn(f"存在临时/缓存文件（提交前清理或确认已 gitignore）：{', '.join(sorted(set(junk))[:6])}")


# ----------------------------------------------------------------- 6. 日期健康度
def check_dates() -> None:
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    out = ROOT / "out"
    if out.exists():
        days = sorted(d.name for d in out.iterdir() if d.is_dir() and DATE_RE.match(d.name))
        if days and days[-1] != today:
            warn(f"最新产出目录是 {days[-1]}，今天（北京时间）是 {today}——如果隔天开工了，先跑 tools/new_day.py")


def main() -> int:
    ap = argparse.ArgumentParser(description="全项目体检")
    ap.add_argument("--strict", action="store_true", help="警告也当失败")
    args = ap.parse_args()

    check_structure()
    check_skill_refs()
    check_scripts()
    check_cross_day()
    check_junk()
    check_dates()

    print("=" * 64)
    print("项目体检")
    print("=" * 64)
    for e in errors:
        print("❌ " + e)
    for w in warns:
        print("⚠️  " + w)
    print("-" * 64)
    print(f"错误 {len(errors)} · 警告 {len(warns)}")

    if errors or (args.strict and warns):
        print("结论：不通过，修完再提交。")
        return 1
    print("结论：通过。可以提交。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
