#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topic_score.py —— AIHOT 热点「短视频可做性」打分器（确定性规则，不调用大模型）

为什么需要它：
    每天 AIHOT 有 10 条热点，但一个号一天只能产出 1-2 条内容。
    热度榜按「讨论量」排序，不等于「短视频可做性」——
    一条讲财报数字的新闻热度很高，但做成视频没人看完；
    一条「某国封杀某模型」热度可能只有第 5，但情绪拉满、30 秒能讲完、完播率高。

    这个脚本把「做视频」这件事拆成 5 个可量化维度，给每条热点打分并推荐内容形态。
    它是筛子，不是决策者：输出的是「先做哪 2 条」，最终选题仍需人判断。

用法：
    python3 tools/topic_score.py                          # 用最新抓取的数据
    python3 tools/topic_score.py --file data/raw/2026-10-20/hot-topics.json
    python3 tools/topic_score.py --top 3 --json           # 只要前 3，JSON 输出
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "data/raw/2026-10-20/hot-topics.json"

# ---------------------------------------------------------------- 关键词词表
# 情绪/冲突：决定「3 秒钩子」能不能立住
CONFLICT = [
    "封杀", "禁令", "下令", "移除", "失控", "入侵", "黑客", "被捕", "起诉",
    "诉讼", "破产", "窃密", "泄密", "警告", "叫停", "下架", "翻车", "抵制",
    "失控", "白宫", "联邦", "国土安全部", "FBI", "审查", "停用", "禁用",
]
# 实用价值：决定「收藏/转发」——工具号的核心指标
UTILITY = [
    "发布", "上线", "开源", "免费", "降价", "折扣", "五折", "开放", "更新",
    "教程", "支持", "接入", "参数", "价格", "API", "权重", "可用", "领取",
]
# 国内受众相关度：AI 资讯号的主力人群关心国产模型
CN_RELEVANT = [
    "DeepSeek", "深度求索", "Qwen", "通义", "千问", "豆包", "Kimi", "月之暗面",
    "智谱", "GLM", "MiniMax", "蚂蚁", "阿里", "字节", "腾讯", "百度", "开源",
    "硅基流动", "可灵", "即梦",
]
# 可视化友好度：有具体数字/对比 → 适合做卡片图、数据对比镜
VISUAL = ["亿", "万", "倍", "token", "Token", "%", "分", "美元", "元"]
# 纯抽象（政策/资本/人事）→ 需要背景解释，适合「深度口播」而非快讯
ABSTRACT = ["估值", "融资", "IPO", "法案", "股份", "基金", "并购", "收购", "任命"]

WEIGHTS = {
    "heat": 0.30,       # 有多少人在讨论
    "conflict": 0.25,   # 情绪张力 → 完播率
    "utility": 0.25,    # 实用价值 → 收藏率
    "cn_relevant": 0.10,  # 受众相关度
    "visual": 0.10,     # 可视化友好度
}

# 同一批热点，不同号型的取舍完全不同。用 --profile 切换。
PROFILES = {
    # 工具号：粉丝来学怎么用，收藏率 = 命
    "tool":  {"heat": 0.25, "conflict": 0.10, "utility": 0.40, "cn_relevant": 0.15, "visual": 0.10},
    # 资讯号：要传播，完播与转发 = 命
    "news":  {"heat": 0.30, "conflict": 0.40, "utility": 0.10, "cn_relevant": 0.10, "visual": 0.10},
    # 观点号：靠「这事意味着什么」立人设，情绪 + 深度各半
    "opinion": {"heat": 0.20, "conflict": 0.35, "utility": 0.10, "cn_relevant": 0.15, "visual": 0.20},
}


def hits(text: str, words: list[str]) -> int:
    return sum(1 for w in words if w in text)


def norm(value: float, ceiling: float) -> float:
    """把原始值压到 0~1，超过上限按 1 计。"""
    return max(0.0, min(1.0, value / ceiling))


def load_digests(story_dir: Path) -> dict[str, str]:
    """把抓下来的 story/*.json 按 publicId 建索引，用 AI 综述补足 hot-topics 缺失的摘要。"""
    out: dict[str, str] = {}
    if not story_dir.is_dir():
        return out
    for f in story_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        story = d.get("story") or d
        pid = story.get("publicId") or f.stem
        digest = story.get("digest") or ""
        if digest:
            out[pid] = digest
    return out


def story_id_of(it: dict) -> str:
    """hot-topics 的 links.story 是 aihot.virxact.com/story/<uuid> 旧域名链接，取末尾 UUID。"""
    url = (it.get("links") or {}).get("story", "") or ""
    return url.rstrip("/").rsplit("/", 1)[-1] if url else ""


def score_item(it: dict, max_signal: float, max_part: float,
               digests: dict[str, str] | None = None,
               weights: dict[str, float] | None = None) -> dict:
    title = it.get("title", "") or ""
    digest = (digests or {}).get(story_id_of(it), "")
    # 摘要可能不存在（hot-topics 本身不带摘要）；有 story 综述就用上，评分口径才准
    text = title + " " + (it.get("summary") or "") + " " + digest

    heat = 0.5 * norm(it.get("signalCount", 0), max_signal) + \
           0.5 * norm(it.get("participantCount", 0), max_part)

    conflict = norm(hits(text, CONFLICT), 2)
    utility = norm(hits(text, UTILITY), 3)
    cn = norm(hits(text, CN_RELEVANT), 2)
    visual = norm(hits(text, VISUAL), 3)

    w = weights or WEIGHTS
    total = (
        w["heat"] * heat
        + w["conflict"] * conflict
        + w["utility"] * utility
        + w["cn_relevant"] * cn
        + w["visual"] * visual
    )

    # ---- 推荐内容形态（规则，不是玄学） ----
    abstract = hits(text, ABSTRACT)
    if conflict >= 0.5 and utility < 0.34:
        form = "30秒口播 + 背景解释"          # 情绪型：讲清「为什么」
    elif utility >= 0.67 and conflict < 0.5:
        form = "对比图表卡 + 上手演示"          # 工具型：收藏导向
    elif conflict >= 0.5 and utility >= 0.34:
        form = "口播 + 数据分屏"                # 又有情绪又有信息
    elif abstract >= 1:
        form = "深度口播（需补背景）"           # 资本/政策：快讯讲不完
    else:
        form = "图文卡片（信息密度优先）"

    return {
        "rank": it.get("rank"),
        "title": title,
        "score": round(total * 100, 1),
        "dims": {
            "热度": round(heat * 100, 1),
            "冲突/情绪": round(conflict * 100, 1),
            "实用价值": round(utility * 100, 1),
            "受众相关": round(cn * 100, 1),
            "可视化": round(visual * 100, 1),
        },
        "form": form,
        "id": it.get("id"),
        "story": (it.get("links") or {}).get("story", ""),
        "hot_dims": {
            "signalCount": it.get("signalCount"),
            "sourceCount": it.get("sourceCount"),
            "participantCount": it.get("participantCount"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="AIHOT 热点短视频可做性打分")
    ap.add_argument("--file", default=str(DEFAULT_FILE), help="hot-topics.json 路径")
    ap.add_argument("--top", type=int, default=10, help="输出前 N 条")
    ap.add_argument("--profile", choices=sorted(PROFILES), default=None,
                    help="号型预设：tool=工具号 / news=资讯号 / opinion=观点号；不填用均衡权重")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"[!] 数据文件不存在：{path}\n    先跑：python3 tools/aihot_fetch.py hot", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", data if isinstance(data, list) else [])
    if not items:
        print("[!] 数据里没有 items", file=sys.stderr)
        return 1

    max_signal = max((i.get("signalCount") or 0) for i in items) or 1
    max_part = max((i.get("participantCount") or 0) for i in items) or 1

    story_dir = path.parent / "story"
    digests = load_digests(story_dir)
    if digests:
        print(f"[i] 已用 {len(digests)} 条 story 的 AI 综述补全摘要", file=sys.stderr)
    weights = PROFILES[args.profile] if args.profile else None
    scored = [score_item(i, max_signal, max_part, digests, weights) for i in items]
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[: args.top]

    if args.json:
        print(json.dumps(top, ensure_ascii=False, indent=2))
        return 0

    print("AIHOT 热点 · 短视频可做性打分")
    print(f"数据：{path}  共 {len(items)} 条，取前 {len(top)}")
    w = weights or WEIGHTS
    label = f"（{args.profile} 号型）" if args.profile else "（均衡）"
    print(f"维度权重{label}：" + " ".join(f"{k}{int(v*100)}%" for k, v in w.items()))
    print("=" * 74)
    for i, s in enumerate(top, 1):
        d = s["dims"]
        print(f"\n{i:>2}. [{s['score']:>5.1f}] {s['title']}")
        print(f"    原榜 #{s['rank']} · 热度 信号{s['hot_dims']['signalCount']} "
              f"信源{s['hot_dims']['sourceCount']} 参与{s['hot_dims']['participantCount']}")
        print(f"    维度  热度{d['热度']:>5.1f} 冲突{d['冲突/情绪']:>5.1f} "
              f"实用{d['实用价值']:>5.1f} 受众{d['受众相关']:>5.1f} 可视{d['可视化']:>5.1f}")
        print(f"    形态  {s['form']}")
        print(f"    id    {s['id']}")
    print("\n" + "=" * 74)
    print("提示：分数只是筛子。前 2 条值得做，第 3 条之后除非你有独特视角，否则别碰。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
