#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
new_day.py —— 新建一天的工作区

为什么要有它：
    这个项目按「一天一个文件夹」组织。靠人记日期迟早会串，
    所以开工第一步永远是跑这个脚本，让它告诉你今天是几号、该建哪些目录。

用法：
    python3 tools/new_day.py              # 用北京时间今天
    python3 tools/new_day.py --date 2026-10-21
    python3 tools/new_day.py --force      # 目录已存在时强制重建（会保留已有文件）
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Asia/Shanghai")

TOPIC_TEMPLATE = """# {date} · 当日选题

> 每天最多做 2 条。先判梗，再判信息。
> 规则见 `CONVENTIONS.md`；方法论见 `skills/ai-news-content/references/08-meme-engine.md`。

## 今日热点（从 data/hot-trends.md 抄关键几条）

- 

## 选题 1
- 新闻：
- 梗方向（置换/对决/预告）：
- 输出模式（meme / meme-video / flash / xhs / douyin）：
- 借用热点：
- 风险：

## 选题 2（可选）
- 新闻：
- 梗方向：
- 输出模式：
- 借用热点：
- 风险：

## 今天不做什么（明确放弃的题）
- 
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="新建一天的工作区")
    ap.add_argument("--date", help="YYYY-MM-DD（默认北京时间今天）")
    ap.add_argument("--force", action="store_true", help="目录已存在也继续（不覆盖已有文件）")
    args = ap.parse_args()

    today = args.date or datetime.now(TZ).strftime("%Y-%m-%d")
    try:
        datetime.strptime(today, "%Y-%m-%d")
    except ValueError:
        print(f"[!] 日期格式不对：{today}（要 YYYY-MM-DD）", file=sys.stderr)
        return 1

    raw_dir = ROOT / "data" / "raw" / today
    out_dir = ROOT / "out" / today
    existed = raw_dir.exists() or out_dir.exists()

    if existed and not args.force:
        print(f"[!] {today} 的工作区已经存在：")
        print(f"    {raw_dir}")
        print(f"    {out_dir}")
        print("    继续做昨天/已经开始的活，直接用现有目录；")
        print("    确实要重建加 --force（不会删已有文件）。")
        _print_checklist(today, raw_dir, out_dir)
        return 0

    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 热点快照：当天的一份，便于以后复盘「当时是什么热点」
    trends = ROOT / "data" / "hot-trends.md"
    if trends.exists():
        shutil.copy2(trends, raw_dir / "hot-trends.md")
        print(f"[+] 热点快照 → {raw_dir / 'hot-trends.md'}")
    else:
        print("[i] 没有 data/hot-trends.md，跳过热点快照（建议先建一份）")

    topic = out_dir / "00-当日选题.md"
    if not topic.exists():
        topic.write_text(TOPIC_TEMPLATE.format(date=today), encoding="utf-8")
        print(f"[+] 选题模板 → {topic}")
    else:
        print(f"[i] 选题文件已存在，未覆盖：{topic}")

    _print_checklist(today, raw_dir, out_dir)
    return 0


def _print_checklist(today: str, raw_dir: Path, out_dir: Path) -> None:
    print(f"""
================= {today} =================
数据目录  data/raw/{today}/
产出目录  out/{today}/

开工清单：
  1. 更新 data/hot-trends.md（今天什么在火，标 ✅/🟡/❌）
  2. 取数：python3 tools/aihot_fetch.py hot --save data/raw/{today}/hot-topics.json
  3. 选题：python3 tools/topic_score.py --profile news
  4. 归一：python3 skills/ai-news-content/scripts/prep_input.py --aihot-story <id> \\
            --out data/raw/{today}/<slug>/material.json
  5. 写稿：加载 skills/ai-news-content/SKILL.md，按 meme → 文案 → 视觉 走
  6. 自检：python3 skills/ai-news-content/scripts/check_copy.py <稿件> \\
            --material data/raw/{today}/<slug>/material.json
  7. 收工：python3 tools/doctor.py && git add -A && git commit -m "data: {today}"
===========================================
""")


if __name__ == "__main__":
    raise SystemExit(main())
