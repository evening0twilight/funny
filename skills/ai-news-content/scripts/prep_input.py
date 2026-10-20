#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prep_input.py —— AI 资讯「输入层」：把任意一条 AI 新闻归一成统一素材卡。

支持的四种输入（互斥）：
  --aihot-story <publicId>   AIHOT 事件全貌（复用 tools/aihot_fetch.py：缓存/限流/ETag/重试）
  --aihot-hot                AIHOT 当前热点榜（实时；失败回退 data/raw 最新快照）
  --url <URL>                任意新闻页（厂商官方博客 / 媒体 / HN 讨论页），正则抽正文
  --file <path> | -          纯文本 / Markdown（用户从别处复制来的），完全离线可用
                            不传参且 stdin 是管道时，自动从 stdin 读

输出：
  默认打印可读 Markdown 素材卡；--json 打印 JSON；
  --out PATH          落盘到指定文件（.json → JSON，.md → Markdown）
  --out-dir DIR       同时落盘 DIR/card.json 与 DIR/card.md
  --check             只打印 title + facts/numbers/quotes 等计数，便于人工确认

设计要点（详见 references/input-adapters.md）：
  * 每条 fact 都带 tier（official / first-party / third-party / unverified）+ tier_reason + evidence，
    下游写作可以按「可信度」决定能不能直接写、要不要标「据 XX 报道」。
  * 数字单独抽成 numbers[]，保留 raw/unit/context/来源，是后面事实核验的原料。
  * origin（aihot|url|file）决定商用风险：AIHOT 数据商用需授权，url/file 来源版权未知。
  * 只用 Python 标准库；不联网也能跑 --file / stdin。
"""

from __future__ import annotations

import argparse
import gzip
import html as html_lib
import importlib.util
import json
import os
import re
import sys
import time
import zlib
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib import error, parse, request

try:  # Python 3.9+；macOS/Linux 自带 tzdata 时可用
    from zoneinfo import ZoneInfo

    SH_TZ = ZoneInfo("Asia/Shanghai")
except Exception:  # pragma: no cover - 兜底
    SH_TZ = timezone(timedelta(hours=8))

SCHEMA_VERSION = "ai-news-card/v1"
ROOT = Path(__file__).resolve().parents[3]          # …/person/funny
DATA_RAW = ROOT / "data" / "raw"
DEFAULT_CACHE_DIR = ROOT / "data" / ".cache"
AIHOT_BASE = os.environ.get("AIHOT_BASE_URL", "https://aihot.news").rstrip("/")
AIHOT_STORY_PAGE = AIHOT_BASE + "/story/"

# 抓网页用的 UA：带浏览器特征 + 工具标识。部分站点会按 UA 拦爬虫，失败时报清楚错误，
# 不静默返回空卡。
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
    "ai-news-content/1.0 (+prep_input.py)"
)
MAX_BODY = 8 * 1024 * 1024
TIER_ORDER = ("official", "first-party", "third-party", "unverified")
TIER_LABEL = {
    "official": "official（官方发布）",
    "first-party": "first-party（同一方多渠道）",
    "third-party": "third-party（媒体/评测）",
    "unverified": "unverified（转述/未确认）",
}

# --------------------------------------------------------------------------- #
# 域名 / 信源分层
# --------------------------------------------------------------------------- #
# 厂商官方域名 → 厂商 key。命中即视为「厂商官方渠道」。
VENDOR_DOMAINS = {
    "minimax.io": "minimax",
    "minimaxi.com": "minimax",
    "openai.com": "openai",
    "anthropic.com": "anthropic",
    "claude.ai": "anthropic",
    "deepmind.google": "google",
    "blog.google": "google",
    "ai.google": "google",
    "gemini.google": "google",
    "deepseek.com": "deepseek",
    "api-docs.deepseek.com": "deepseek",
    "moonshot.cn": "moonshot",
    "kimi.com": "moonshot",
    "qwen.ai": "alibaba",
    "alibabacloud.com": "alibaba",
    "tongyi.aliyun.com": "alibaba",
    "zhipuai.cn": "zhipu",
    "bigmodel.cn": "zhipu",
    "chatglm.cn": "zhipu",
    "mistral.ai": "mistral",
    "meta.ai": "meta",
    "llama.com": "meta",
    "ai.meta.com": "meta",
    "x.ai": "xai",
    "cohere.com": "cohere",
    "stability.ai": "stability",
    "midjourney.com": "midjourney",
    "perplexity.ai": "perplexity",
    "nvidia.com": "nvidia",
    "microsoft.com": "microsoft",
    "huggingface.co": "huggingface",
    "github.blog": "github",
    "github.com": "github",
    "ollama.com": "ollama",
    "groq.com": "groq",
    "together.ai": "together",
    "openrouter.ai": "openrouter",
    "cursor.com": "cursor",
    "vercel.com": "vercel",
    "bytedance.com": "bytedance",
    "volcengine.com": "bytedance",
}

VENDOR_DISPLAY = {
    "minimax": "MiniMax",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "deepseek": "DeepSeek",
    "moonshot": "Moonshot",
    "alibaba": "Alibaba",
    "zhipu": "Zhipu",
    "mistral": "Mistral",
    "meta": "Meta",
    "xai": "xAI",
    "cohere": "Cohere",
    "stability": "Stability AI",
    "midjourney": "Midjourney",
    "perplexity": "Perplexity",
    "nvidia": "NVIDIA",
    "microsoft": "Microsoft",
    "huggingface": "Hugging Face",
    "github": "GitHub",
    "ollama": "Ollama",
    "groq": "Groq",
    "together": "Together AI",
    "openrouter": "OpenRouter",
    "cursor": "Cursor",
    "vercel": "Vercel",
    "bytedance": "ByteDance",
}

# 媒体 / 平台 / 聚合站域名（只当导航，不当事实源）。
MEDIA_DOMAINS = {
    "techcrunch.com": "TechCrunch",
    "theverge.com": "The Verge",
    "venturebeat.com": "VentureBeat",
    "wired.com": "WIRED",
    "the-decoder.com": "The Decoder",
    "marktechpost.com": "MarkTechPost",
    "technologyreview.com": "MIT Technology Review",
    "arstechnica.com": "Ars Technica",
    "zdnet.com": "ZDNet",
    "engadget.com": "Engadget",
    "reuters.com": "Reuters",
    "bloomberg.com": "Bloomberg",
    "cnbc.com": "CNBC",
    "forbes.com": "Forbes",
    "nytimes.com": "The New York Times",
    "ithome.com": "IT之家",
    "36kr.com": "36氪",
    "qbitai.com": "量子位",
    "jiqizhixin.com": "机器之心",
    "leiphone.com": "雷锋网",
    "tmtpost.com": "钛媒体",
    "infoq.cn": "InfoQ",
    "thepaper.cn": "澎湃新闻",
    "sina.com.cn": "新浪",
    "sohu.com": "搜狐",
    "163.com": "网易",
    "qq.com": "腾讯新闻",
    "news.ycombinator.com": "Hacker News",
    "reddit.com": "Reddit",
    "x.com": "X（原 Twitter）",
    "twitter.com": "Twitter",
    "linkedin.com": "LinkedIn",
    "youtube.com": "YouTube",
    "bilibili.com": "哔哩哔哩",
    "mp.weixin.qq.com": "微信公众号",
    "aihot.news": "AIHOT（聚合站）",
    "aihot.virxact.com": "AIHOT（聚合站）",
    "producthunt.com": "Product Hunt",
    "huggingface.co/papers": "Hugging Face Daily Papers",
}

# AIHOT 报告源名称里的第三方/平台线索。命中第三档；未知个人账号落到 unverified。
THIRD_PARTY_HINTS = (
    "TechCrunch", "The Verge", "VentureBeat", "WIRED", "The Decoder", "MarkTechPost",
    "Ars Technica", "ZDNet", "Engadget", "Reuters", "Bloomberg", "CNBC", "Forbes",
    "MIT Technology Review", "IT之家", "36氪", "量子位", "机器之心", "雷锋网", "钛媒体",
    "InfoQ", "新浪", "搜狐", "网易", "腾讯新闻", "澎湃", "界面", "财新", "第一财经",
    "Arena", "LMArena", "Artificial Analysis", "OpenRouter", "OpenCode", "opencode",
    "Ollama", "Cline", "GMI Cloud", "WorkBuddy", "SiliconFlow", "硅基流动",
    "Hacker News", "Reddit", "Product Hunt", "GitHub Trending", "Hugging Face",
)
UNVERIFIED_HINTS = (
    "Testing Catalog", "Rohan Paul", "爆料", "传闻", "传言", "据传", "匿名", "网友",
    "微博", "知乎", "贴吧", "博主",
)
OFFICIAL_CHANNEL_RE = re.compile(
    r"Blog|Newsroom|官方|公告|新闻稿|发布页|更新日志|Changelog|Release|博客|新闻中心",
    re.I,
)
_CHANNEL_PREFIXES = ("X：", "X:", "公众号：", "公众号:", "微博：", "微博:", "知乎：", "知乎:", "Bilibili：")

# --------------------------------------------------------------------------- #
# 实体词表（只做「可解释的已知实体」，不追求 NER 全覆盖）
# (canonical, type, [aliases])
# type: org / model / product / media / policy / platform
# --------------------------------------------------------------------------- #
ENTITY_LEXICON = [
    ("MiniMax", "org", ("MiniMax", "稀宇科技", "稀宇")),
    ("OpenAI", "org", ("OpenAI",)),
    ("Anthropic", "org", ("Anthropic",)),
    ("Google DeepMind", "org", ("Google DeepMind", "DeepMind")),
    ("Google", "org", ("Google", "谷歌")),
    ("DeepSeek", "org", ("DeepSeek", "深度求索")),
    ("Meta", "org", ("Meta", "Facebook")),
    ("xAI", "org", ("xAI",)),
    ("Mistral AI", "org", ("Mistral AI", "Mistral")),
    ("Alibaba", "org", ("Alibaba", "阿里巴巴")),
    ("Tencent", "org", ("Tencent", "腾讯")),
    ("ByteDance", "org", ("ByteDance", "字节跳动")),
    ("Baidu", "org", ("Baidu", "百度")),
    ("Huawei", "org", ("Huawei", "华为")),
    ("Zhipu", "org", ("Zhipu", "智谱", "智谱AI")),
    ("Moonshot", "org", ("Moonshot", "月之暗面")),
    ("NVIDIA", "org", ("NVIDIA", "英伟达")),
    ("Microsoft", "org", ("Microsoft", "微软")),
    ("Apple", "org", ("Apple", "苹果公司")),
    ("Amazon", "org", ("Amazon", "亚马逊")),
    ("Hugging Face", "org", ("Hugging Face",)),
    ("GitHub", "org", ("GitHub",)),
    ("Ollama", "org", ("Ollama",)),
    ("OpenRouter", "org", ("OpenRouter",)),
    ("Cline", "org", ("Cline",)),
    ("Cursor", "org", ("Cursor",)),
    ("Perplexity", "org", ("Perplexity",)),
    ("Stability AI", "org", ("Stability AI",)),
    ("Midjourney", "org", ("Midjourney",)),
    ("Cohere", "org", ("Cohere",)),
    ("Groq", "org", ("Groq",)),
    ("Together AI", "org", ("Together AI",)),
    ("Tencent WorkBuddy", "product", ("WorkBuddy",)),
    ("M3.1 Flash", "model", ("M3.1 Flash", "M3.1-Flash", "M3.1Flash")),
    ("M3", "model", ("M3",)),
    ("Space Bunny", "model", ("Space Bunny",)),
    ("MiniMax Code", "product", ("MiniMax Code",)),
    ("MPlan", "product", ("MPlan",)),
    ("V4.1-Flash", "model", ("V4.1-Flash", "V4.1 Flash", "V4.1-Flash-1017")),
    ("GPT-5", "model", ("GPT-5", "GPT 5")),
    ("Claude", "model", ("Claude",)),
    ("Gemini", "model", ("Gemini",)),
    ("Llama", "model", ("Llama",)),
    ("Qwen", "model", ("Qwen", "通义千问")),
    ("Kimi", "model", ("Kimi",)),
    ("GLM", "model", ("GLM",)),
    ("Grok", "model", ("Grok",)),
    ("Sora", "model", ("Sora",)),
    ("TechCrunch", "media", ("TechCrunch",)),
    ("The Verge", "media", ("The Verge",)),
    ("The Decoder", "media", ("The Decoder",)),
    ("MarkTechPost", "media", ("MarkTechPost",)),
    ("IT之家", "media", ("IT之家",)),
    ("36氪", "media", ("36氪",)),
    ("量子位", "media", ("量子位",)),
    ("机器之心", "media", ("机器之心",)),
    ("Hacker News", "media", ("Hacker News",)),
    ("Reddit", "media", ("Reddit",)),
    ("arXiv", "media", ("arXiv",)),
    ("Artificial Analysis", "platform", ("Artificial Analysis",)),
    ("Arena", "platform", ("Arena", "LMArena")),
    ("美国国土安全部", "policy", ("美国国土安全部", "国土安全部", "DHS")),
    ("白宫", "policy", ("白宫",)),
    ("欧盟委员会", "policy", ("欧盟委员会", "欧盟")),
    ("中国工信部", "policy", ("工信部", "工业和信息化部")),
    ("国家网信办", "policy", ("网信办", "国家网信办")),
]

# 型号类兜底（词表没收录时）：GPT-5.2 / M3.1 Flash / V4.1-Flash 等。
MODEL_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:MiniMax|GPT|Claude|Gemini|Llama|Qwen|Kimi|GLM|Grok|DeepSeek|Seed|Step|Yi|M|V)"
    r"\s?-?\d+(?:\.\d+)?(?:\s?[A-Za-z]{2,12})?",
    re.I,
)

# AIHOT 许可说明（下游判断能否商用）
AIHOT_LICENSE = {
    "commercial_ok": "requires_authorization",
    "note": (
        "AIHOT 数据受其使用条款约束：个人非商业、公益、组织内部使用免费；"
        "对外商业产品、客户交付、数据转售、公开镜像、批量公开再分发，"
        "以及训练/微调/评测/RAG 须事先取得 AIHOT 书面授权（aihot.news/terms）。"
        "下游若商用，请改用厂商官方源或先取得授权。"
    ),
    "url": "https://aihot.news/terms",
}

# --------------------------------------------------------------------------- #
# 基础工具
# --------------------------------------------------------------------------- #
def log(msg: str) -> None:
    """提示/诊断信息走 stderr，stdout 只放素材卡。"""
    print(msg, file=sys.stderr, flush=True)


class PrepError(RuntimeError):
    """可预期的输入错误：打印清晰信息并以非 0 退出。"""


def clip(text: str | None, limit: int) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def normalize_space(text: str) -> str:
    text = (text or "").replace("\u00a0", " ").replace("\u3000", " ")
    return " ".join(text.split())


def normalize_block(text: str) -> str:
    """保留段落内的单个空格，压缩多余空白与空行。"""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def now_iso() -> str:
    return datetime.now(SH_TZ).isoformat(timespec="seconds")


def hostname(url: str | None) -> str:
    if not url:
        return ""
    try:
        host = (parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def vendor_for_domain(host: str) -> str | None:
    if not host:
        return None
    for domain, vendor in VENDOR_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return vendor
    return None


def media_for_domain(host: str) -> str | None:
    if not host:
        return None
    for domain, name in MEDIA_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return name
    return None


def is_known_vendor_name(name: str) -> set[str]:
    """从信源名里识别厂商 key（用于判断「同一方多渠道」）。"""
    hits: set[str] = set()
    for vendor, display in VENDOR_DISPLAY.items():
        if display.lower() in name.lower():
            hits.add(vendor)
    for entry in ENTITY_LEXICON:
        canonical, etype = entry[0], entry[1]
        if etype != "org":
            continue
        for alias in entry[2]:
            if alias in name:
                vendor = alias_to_vendor(alias)
                if vendor:
                    hits.add(vendor)
    return hits


def alias_to_vendor(alias: str) -> str | None:
    mapping = {
        "MiniMax": "minimax", "稀宇科技": "minimax", "OpenAI": "openai", "Anthropic": "anthropic",
        "Google DeepMind": "google", "DeepMind": "google", "Google": "google", "谷歌": "google",
        "DeepSeek": "deepseek", "深度求索": "deepseek", "Meta": "meta", "xAI": "xai",
        "Mistral AI": "mistral", "Mistral": "mistral", "Alibaba": "alibaba", "阿里巴巴": "alibaba",
        "Tencent": "tencent", "腾讯": "tencent", "ByteDance": "bytedance", "字节跳动": "bytedance",
        "Baidu": "baidu", "百度": "baidu", "Huawei": "huawei", "华为": "huawei",
        "Zhipu": "zhipu", "智谱": "zhipu", "Moonshot": "moonshot", "月之暗面": "moonshot",
        "NVIDIA": "nvidia", "英伟达": "nvidia", "Microsoft": "microsoft", "微软": "microsoft",
        "Apple": "apple", "Amazon": "amazon", "Hugging Face": "huggingface", "GitHub": "github",
        "Ollama": "ollama", "OpenRouter": "openrouter", "Cline": "cline", "Cursor": "cursor",
        "Perplexity": "perplexity", "Stability AI": "stability", "Midjourney": "midjourney",
        "Cohere": "cohere", "Groq": "groq", "Together AI": "together",
    }
    return mapping.get(alias)


def detect_vendors(text: str) -> set[str]:
    """从标题/正文里找出「这条新闻的主角厂商」。"""
    vendors: set[str] = set()
    for entry in ENTITY_LEXICON:
        canonical, etype = entry[0], entry[1]
        if etype != "org":
            continue
        for alias in entry[2]:
            if alias_in_text(alias, text):
                vendor = alias_to_vendor(alias)
                if vendor:
                    vendors.add(vendor)
                break
    return vendors


def alias_in_text(alias: str, text: str) -> bool:
    if re.fullmatch(r"[A-Za-z0-9 .&+'\-/:]+", alias):
        return re.search(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", text) is not None
    return alias in text


# --------------------------------------------------------------------------- #
# 时间解析
# --------------------------------------------------------------------------- #
def normalize_datetime(raw, fallback_tz=SH_TZ):
    """尽量把时间统一成 ISO 8601；只有日期时保留 YYYY-MM-DD。失败返回 None。"""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.match(r"^(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?$", s)
    if m:
        y, mo, d = (int(x) for x in m.groups())
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            return None
    # 带 Z / ±HH:MM 时区后缀的 ISO 串交给 fromisoformat，别被下面的中文/空格格式分支截胡
    has_tz_suffix = bool(re.search(r"(?:Z|[+-]\d{2}:?\d{2})$", s))
    m = None if has_tz_suffix else re.match(
        r"^(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?[ T](\d{1,2})[:：](\d{2})(?:[:：](\d{2}))?",
        s,
    )
    if m:
        y, mo, d, hh, mm = (int(m.group(i)) for i in range(1, 6))
        ss = int(m.group(6) or 0)
        try:
            return datetime(y, mo, d, hh, mm, ss, tzinfo=fallback_tz).isoformat(timespec="seconds")
        except ValueError:
            return None
    iso = s.replace("Z", "+00:00")
    dt = None
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%d %b %Y %H:%M:%S",
            "%b %d, %Y",
            "%B %d, %Y",
        ):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            try:
                dt = parsedate_to_datetime(s)
            except (TypeError, ValueError):
                dt = None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=fallback_tz)
    return dt.astimezone(fallback_tz).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# HTTP 抓取（UA / 超时 / gzip / 重试 / 清晰报错）
# --------------------------------------------------------------------------- #
def decode_body(raw: bytes, headers) -> str:
    enc = (headers.get("Content-Encoding") or "").lower()
    try:
        if "gzip" in enc:
            raw = gzip.decompress(raw)
        elif "deflate" in enc:
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except (OSError, zlib.error) as exc:
        raise PrepError(f"响应解压失败（Content-Encoding: {enc}）：{exc}") from exc

    charset = ""
    ctype = headers.get("Content-Type", "") or ""
    m = re.search(r"charset=([\w-]+)", ctype, re.I)
    if m:
        charset = m.group(1).lower()
    if not charset:
        m = re.search(rb"<meta[^>]+charset=[\"']?([A-Za-z0-9_-]+)", raw[:8192], re.I)
        if m:
            charset = m.group(1).decode("ascii", "replace").lower()
    for enc_try in ([charset] if charset else []) + ["utf-8", "gb18030"]:
        try:
            return raw.decode(enc_try)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def http_get(url: str, timeout: float = 20.0, accept: str | None = None) -> tuple[str, str, str]:
    """GET 一个 URL，返回 (text, final_url, content_type)。失败抛 PrepError，绝不静默返回空。"""
    parsed = parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise PrepError(f"URL 不合法：{url!r}（需要 http(s):// 开头且带域名）")
    headers = {
        "User-Agent": UA,
        "Accept": accept or "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip",
    }
    last_err = ""
    for attempt in range(2):
        req = request.Request(url, headers=headers, method="GET")
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(MAX_BODY + 1)
                if len(raw) > MAX_BODY:
                    raise PrepError(f"页面超过 {MAX_BODY // 1024 // 1024}MB，拒绝处理：{url}")
                ctype = resp.headers.get("Content-Type", "") or ""
                return decode_body(raw, resp.headers), resp.geturl(), ctype
        except error.HTTPError as exc:
            try:
                body = exc.read(600).decode("utf-8", "replace")
            except Exception:
                body = ""
            detail = clip(strip_html(body), 140)
            msg = f"HTTP {exc.code} {exc.reason}：{url}"
            if detail:
                msg += f"（响应片段：{detail}）"
            if exc.code in (429, 500, 502, 503, 504) and attempt == 0:
                log(f"[重试] {msg}；2s 后重试一次")
                time.sleep(2)
                continue
            raise PrepError(
                msg + "。请检查 URL 是否可公开访问、站点是否限制爬虫；仍不行就改用 --file 粘贴正文。"
            ) from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            last_err = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                log(f"[重试] 网络错误 {last_err}；1.5s 后重试一次")
                time.sleep(1.5)
                continue
            raise PrepError(
                f"网络错误：{last_err}。目标 {url}，超时 {timeout:g}s；"
                "请检查网络/DNS/代理，或改用 --file 粘贴正文。"
            ) from exc
    raise PrepError(f"请求失败：{url}（{last_err}）")


# --------------------------------------------------------------------------- #
# HTML → 标题 / 时间 / 正文
# --------------------------------------------------------------------------- #
TAG_RE = re.compile(r"<[^>]+>")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
REMOVE_BLOCKS_RE = re.compile(
    r"<(script|style|noscript|svg|iframe|form|nav|header|footer|aside|template)\b[^>]*>.*?</\1\s*>",
    re.I | re.S,
)
META_RE = re.compile(r"<meta\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([\w:-]+)\s*=\s*(\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.S)
BLOCK_TAGS = ("h1", "h2", "h3", "p", "li", "blockquote", "div")
BOILER_RE = re.compile(
    r"(cookie|subscribe|newsletter|sign\s*in|log\s*in|登录|注册|订阅|关注我们|扫码|"
    r"下载\s*APP|版权所有|all rights reserved|privacy policy|terms of use|分享到|"
    r"相关阅读|推荐阅读|热门推荐|责任编辑|广告|点击查看更多|返回首页|上一篇|下一篇)",
    re.I,
)
CJK_RE = re.compile(r"[\u3400-\u9fff]")


def strip_html(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</(?:p|div|li|h[1-6]|tr|section|article|blockquote)>", "\n", fragment, flags=re.I)
    fragment = TAG_RE.sub("", fragment)
    fragment = html_lib.unescape(fragment)
    return normalize_space(fragment)


def parse_attrs(tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for m in ATTR_RE.finditer(tag):
        key = m.group(1).lower()
        value = m.group(3) if m.group(3) is not None else (
            m.group(4) if m.group(4) is not None else m.group(5)
        )
        attrs[key] = html_lib.unescape(value or "")
    return attrs


def extract_meta(html_text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for m in META_RE.finditer(html_text):
        attrs = parse_attrs(m.group(0))
        key = (attrs.get("property") or attrs.get("name") or attrs.get("itemprop") or "").lower()
        content = attrs.get("content")
        if key and content and key not in meta:
            meta[key] = normalize_space(content)
    return meta


def clean_title(raw: str, site_name: str | None = None) -> str:
    title = normalize_space(html_lib.unescape(raw or ""))
    for sep in (" | ", " — ", " – ", " - ", " _ "):
        if sep not in title:
            continue
        head, tail = title.rsplit(sep, 1)
        if len(head) < 8 or not tail:
            continue
        tail_l = tail.strip().lower()
        site_l = (site_name or "").strip().lower()
        looks_site = (
            (site_l and (tail_l in site_l or site_l in tail_l))
            or len(tail) <= 22
            or tail_l in {"minimax", "openai", "anthropic", "deepseek", "google", "meta"}
        )
        if looks_site:
            title = head.strip()
            break
    return title


def extract_main_region(html_text: str) -> str:
    cleaned = COMMENT_RE.sub("", html_text)
    cleaned = REMOVE_BLOCKS_RE.sub(" ", cleaned)
    candidates: list[str] = []
    for tag in ("article", "main"):
        for m in re.finditer(rf"<{tag}\b[^>]*>(.*?)</{tag}\s*>", cleaned, re.I | re.S):
            candidates.append(m.group(1))
    if candidates:
        return max(candidates, key=len)
    body = re.search(r"<body\b[^>]*>(.*?)</body>", cleaned, re.I | re.S)
    return body.group(1) if body else cleaned


def keep_paragraph(text: str) -> bool:
    if not text:
        return False
    if len(text) < 16 and len(CJK_RE.findall(text)) < 8:
        return False
    if BOILER_RE.search(text) and len(text) < 120:
        return False
    return True


_LABEL_LINK_RE = re.compile(
    r"^[^:：]{1,40}[:：]\s*(?:https?://|[\w.-]+\.[a-z]{2,}(?:/|\b))", re.I
)


def _looks_like_label_link(text: str) -> bool:
    """「API access: platform.minimax.io」这类导航/入口行不是事实。"""
    return bool(_LABEL_LINK_RE.match((text or "").strip()))


def extract_blocks(region: str) -> list[dict]:
    """返回 [{'kind': 'heading'|'body', 'text': ...}]，标题块不当事实用。"""
    pattern = re.compile(
        r"<(h[1-3]|p|li|blockquote)\b[^>]*>(.*?)</\1\s*>", re.I | re.S
    )
    out: list[dict] = []
    for tag, inner in pattern.findall(region):
        text = strip_html(inner)
        if keep_paragraph(text):
            out.append({"kind": "heading" if tag.lower().startswith("h") else "body", "text": text})
    return out


def fallback_blocks(region: str) -> list[dict]:
    text = re.sub(r"</(?:p|div|li|h[1-6]|section|article|tr|td|blockquote)>", "\n", region, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = strip_html(text)
    out: list[dict] = []
    for line in re.split(r"\n+", text):
        line = normalize_space(line)
        if keep_paragraph(line):
            out.append({"kind": "body", "text": line})
    return out


def parse_html_page(html_text: str, url: str) -> dict:
    """抽 title / site_name / published_at / description / paragraphs。抽不到正文抛错。"""
    meta = extract_meta(html_text)
    site_name = normalize_space(meta.get("og:site_name") or meta.get("application-name") or "")
    raw_title = (
        meta.get("og:title")
        or meta.get("twitter:title")
        or meta.get("title")
        or ""
    )
    if not raw_title:
        m = re.search(r"<h1\b[^>]*>(.*?)</h1>", html_text, re.I | re.S)
        if m:
            raw_title = strip_html(m.group(1))
    if not raw_title:
        m = re.search(r"<title\b[^>]*>(.*?)</title>", html_text, re.I | re.S)
        raw_title = strip_html(m.group(1)) if m else ""
    title = clean_title(raw_title, site_name or media_for_domain(hostname(url)) or "")
    description = normalize_space(
        meta.get("og:description") or meta.get("description") or meta.get("twitter:description") or ""
    )

    published_raw = ""
    for key in ("article:published_time", "og:published_time", "datepublished", "pubdate", "date"):
        if meta.get(key):
            published_raw = meta[key]
            break
    if not published_raw:
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html_text)
        if m:
            published_raw = m.group(1)
    if not published_raw:
        m = re.search(r"<time\b[^>]*datetime=[\"']([^\"']+)[\"']", html_text, re.I)
        if m:
            published_raw = m.group(1)

    region = extract_main_region(html_text)
    blocks = extract_blocks(region)
    if len(blocks) < 2:
        fallback = fallback_blocks(region)
        if len(fallback) > len(blocks):
            blocks = fallback
    if not blocks:
        fallback = fallback_blocks(html_text)
        if len(fallback) > len(blocks):
            blocks = fallback

    # 去重 / 去掉与标题重复的首段
    deduped: list[dict] = []
    seen: set[str] = set()
    for block in blocks:
        p = block["text"]
        key = re.sub(r"\W+", "", p)[:60]
        if not key or key in seen:
            continue
        seen.add(key)
        if title and re.sub(r"\W+", "", title)[:40] == key[:40]:
            continue
        deduped.append(block)
    blocks = deduped
    paragraphs = [block["text"] for block in blocks]

    total = sum(len(p) for p in paragraphs)
    if total < 120:
        raise PrepError(
            f"未能从页面抽取到足够正文（{total} 字，{len(paragraphs)} 段）：{url}。"
            "该页可能是 JS 动态渲染/需要登录/反爬；请改用 --file 粘贴正文，"
            "或换成原文/其他媒体页面。"
        )
    if not title:
        title = clip(paragraphs[0], 80)
    return {
        "title": title,
        "title_raw": normalize_space(raw_title),
        "site_name": site_name,
        "description": description,
        "published_at_raw": published_raw,
        "published_at": normalize_datetime(published_raw),
        "paragraphs": paragraphs,
        "blocks": blocks,
    }


# --------------------------------------------------------------------------- #
# 文本切分 / Markdown 处理
# --------------------------------------------------------------------------- #
def split_sentences(text: str) -> list[str]:
    text = normalize_space(text)
    if not text:
        return []
    out: list[str] = []
    for chunk in re.split(r"(?<=[。！？；!?；])\s*", text):
        chunk = chunk.strip()
        if not chunk:
            continue
        for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'（(])", chunk):
            sent = sent.strip()
            if sent:
                out.append(sent)
    return out


def split_paragraphs(text: str) -> list[str]:
    text = normalize_block(text)
    parts = [normalize_space(p) for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) == 1 and len(parts[0]) > 1600:
        # 单段长文：按句号切成若干段，便于阅读与抽句
        sents = split_sentences(parts[0])
        parts = ["".join(sents[i : i + 4]) for i in range(0, len(sents), 4)]
    return parts


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[a-zA-Z0-9_-]*\n?(.*?)```", lambda m: m.group(1), text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}(?:[-*+]|\d+\.)\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\|.*\|\s*$", lambda m: " ".join(x.strip() for x in m.group(0).strip().strip("|").split("|")), text, flags=re.M)
    text = re.sub(r"[*_~`]{1,3}", "", text)
    return normalize_block(text)


def detect_language(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk >= max(4, latin // 3):
        return "zh" if latin < cjk * 2 else "mixed"
    return "en" if latin else "unknown"


def infer_text_title(text: str, markdown: bool) -> str:
    if markdown:
        m = re.search(r"^\s{0,3}#{1,2}\s+(.+)$", text, re.M)
        if m:
            return normalize_space(m.group(1))[:80]
    for line in text.splitlines():
        line = normalize_space(re.sub(r"^\s{0,3}#{1,6}\s*", "", line))
        if not line:
            continue
        if len(line) <= 100 and not re.search(r"[。！？；!?]$", line):
            return line[:80]
        return clip(line, 60)
    return ""


def looks_markdown(text: str) -> bool:
    return bool(re.search(r"^(#{1,6})\s+\S", text, re.M)) or "```" in text or bool(
        re.search(r"^[-*+]\s+\S", text, re.M)
    )


# --------------------------------------------------------------------------- #
# 数字抽取（事实核验原料）
# --------------------------------------------------------------------------- #
# (label, 正则, 单位类别)
NUMBER_PATTERNS = [
    ("date_iso", re.compile(r"(?<!\d)(20\d{2})[-/](\d{1,2})[-/](\d{1,2})(?!\d)"), "date"),
    ("date_cn", re.compile(r"(?<!\d)(\d{1,2})\s*月\s*(\d{1,2})\s*日"), "date"),
    ("fraction", re.compile(r"(?<![\d.])\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?(?![\d.])"), "ratio"),
    ("percent_cn", re.compile(r"百分之\s*\d+(?:\.\d+)?"), "%"),
    ("percent", re.compile(r"(?<![\d.])\d+(?:\.\d+)?\s*%"), "%"),
    (
        "money",
        re.compile(
            r"[$¥€£]\s?\d+(?:\.\d+)?(?:\s*(?:/|每)\s*(?:\d+(?:\.\d+)?\s*[TBMK]?|百万|千)?\s*(?:tokens?|Token))?",
            re.I,
        ),
        "money",
    ),
    (
        "perf",
        re.compile(
            r"(?<![\d.])\d+(?:\.\d+)?\+?\s*(?:TPS|tokens?/s|tok/s|token/s|ms|FLOPS|GB|TB|MB|QPS)",
            re.I,
        ),
        "rate",
    ),
    ("duration", re.compile(r"(?<![\d.])\d+(?:\.\d+)?\s*(?:小时|分钟|秒|天|周|个月|年|倍)"), "duration"),
    ("scale_en", re.compile(r"(?<![\w.])\d+(?:\.\d+)?\s?[TBMK](?![A-Za-z])"), "scale_en"),
    (
        "scale_cn",
        re.compile(
            r"(?<![\d.])\d+(?:\.\d+)?\s*(?:万亿|亿|万|千)\s*(?:token|tokens|参数|用户|美元|元|次|台|人)?",
            re.I,
        ),
        "scale_cn",
    ),
    (
        "scale_word_en",
        re.compile(
            r"(?<![\d.])\d+(?:\.\d+)?\s*(?:trillion|billion|million|thousand)\s*"
            r"(?:tokens?|parameters?|params?|users?)?",
            re.I,
        ),
        "scale_word_en",
    ),
    (
        "count_cn",
        re.compile(r"(?<![\d.])\d+(?:\.\d+)?\s*(?:分|名|位|个|条|篇|项|次|台|人|轮|版|家|元)"),
        "count_cn",
    ),
    ("comma", re.compile(r"(?<![\d,])\d{1,3}(?:,\d{3})+(?![\d,])"), "count"),
    ("bare", re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])"), "bare"),
]
_CN_UNIT_CHARS = "分名位个条篇项次台人轮版家元天周月年秒倍"
_MONEY_UNIT = {"$": "USD", "¥": "CNY", "€": "EUR", "£": "GBP"}


def _sentence_around(text: str, start: int, end: int, limit: int = 180) -> str:
    left = max(
        text.rfind(ch, 0, start) for ch in "。！？；!?;\n"
    ) + 1
    right_candidates = [text.find(ch, end) for ch in "。！？；!?;\n"]
    right_candidates = [i for i in right_candidates if i != -1]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    return clip(normalize_space(text[left:right]), limit)


def _number_unit(raw: str, kind: str, text: str, start: int, end: int) -> tuple[str, str]:
    """返回 (value, unit)。"""
    num_match = re.search(r"\d+(?:\.\d+)?", raw)
    value = num_match.group(0) if num_match else raw
    if kind == "date":
        return raw, "date"
    if kind == "ratio":
        return raw, "ratio"
    if kind == "%":
        return value, "%"
    if kind == "money":
        symbol = raw.strip()[0]
        unit = _MONEY_UNIT.get(symbol, "money")
        if re.search(r"/\s*\d+(?:\.\d+)?\s*[TBMK]?\s*tokens?", raw, re.I):
            unit += "/tokens"
        return value, unit
    if kind == "rate":
        m = re.search(r"(TPS|tokens?/s|tok/s|token/s|ms|FLOPS|GB|TB|MB|QPS)$", raw, re.I)
        return value, (m.group(1) if m else "")
    if kind == "duration":
        m = re.search(r"(小时|分钟|秒|天|周|个月|年|倍)$", raw)
        return value, (m.group(1) if m else "")
    if kind == "scale_en":
        m = re.search(r"([TBMK])$", raw)
        return value, (m.group(1) if m else "")
    if kind == "scale_cn":
        m = re.search(r"(万亿|亿|万|千)", raw)
        return value, (m.group(1) if m else "")
    if kind == "scale_word_en":
        m = re.search(r"(trillion|billion|million|thousand)(?:\s*(tokens?|parameters?|params?|users?))?", raw, re.I)
        if not m:
            return value, ""
        unit = m.group(1).lower()
        if m.group(2):
            unit += " " + m.group(2).lower()
        return value, unit
    if kind == "count_cn":
        m = re.search(r"([分名位个条篇项次台人轮版家元])$", raw)
        return value, (m.group(1) if m else "")
    if kind == "count":
        return value.replace(",", ""), ""
    # bare：从上下文补单位
    before = text[max(0, start - 4) : start]
    after = text[end : end + 3]
    after_en = text[end : end + 16]
    if re.search(r"(?:第|Top|top|No\.?|NO\.?)\s*$", before):
        return value, "rank"
    after_l = after.lstrip()
    for unit in _CN_UNIT_CHARS:
        if after_l.startswith(unit):
            return value, unit
    m = re.match(
        r"\s?(points?|tokens?|parameters?|params?|users?|times|hours?|days?|minutes?|seconds?)",
        after_en,
        re.I,
    )
    if m:
        return value, m.group(1).lower()
    return value, ""



# 时长归一化：NEAR 的 "2 days, 6:28:26" 直接抽会变成 2 / 6 / 28 / 26 四个碎数字，
# 写稿时算成「54 小时 28 分」反而会被判「无出处」。先在源文本里归一成中文单位。
_DUR_DHMS = re.compile(
    r"(?P<d>\d+)\s*days?\s*[,，]?\s*(?P<h>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})", re.I
)
_DUR_HMS = re.compile(r"(?<!\d)(?P<h>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})(?!\d)")


def normalize_durations(text: str) -> str:
    """把 'X days, H:MM:SS' / 'H:MM:SS' 改写成 'X 天 Y 小时 Z 分 W 秒'，便于抽数与写稿。"""
    if not text:
        return text

    def _dhms(m: re.Match) -> str:
        d, h, mi, sec = int(m.group("d")), int(m.group("h")), int(m.group("m")), int(m.group("s"))
        return f"{d} 天 {h} 小时 {mi} 分 {sec} 秒（共 {d * 24 + h} 小时 {mi} 分）"

    def _hms(m: re.Match) -> str:
        h, mi, sec = int(m.group("h")), int(m.group("m")), int(m.group("s"))
        return f"{h} 小时 {mi} 分 {sec} 秒"

    text = _DUR_DHMS.sub(_dhms, text)
    return _DUR_HMS.sub(_hms, text)


def extract_numbers(text: str) -> list[dict]:
    """从一段文本抽所有数字（长匹配优先、去重叠），返回 [{value, raw, unit, context}]。"""
    if not text:
        return []
    text = normalize_durations(text)
    candidates: list[tuple[int, int, str, str]] = []
    for _label, pattern, kind in NUMBER_PATTERNS:
        for m in pattern.finditer(text):
            candidates.append((m.start(), m.end(), m.group(0), kind))
    candidates.sort(key=lambda x: (-(x[1] - x[0]), x[0]))
    chosen: list[tuple[int, int, str, str]] = []
    for start, end, raw, kind in candidates:
        if all(end <= s or start >= e for s, e, _r, _k in chosen):
            chosen.append((start, end, raw, kind))
    chosen.sort()
    out: list[dict] = []
    for start, end, raw, kind in chosen:
        value, unit = _number_unit(raw.strip(), kind, text, start, end)
        context = _sentence_around(text, start, end)
        value_num = None
        if kind not in ("ratio", "date"):
            try:
                value_num = float(value)
            except ValueError:
                value_num = None
        out.append(
            {
                "value": value,
                "value_num": value_num,
                "raw": raw.strip(),
                "unit": unit,
                "context": context,
            }
        )
    return out


# --------------------------------------------------------------------------- #
# 实体 / 引语
# --------------------------------------------------------------------------- #
def extract_entities(text: str) -> list[dict]:
    if not text:
        return []
    matches: list[tuple[int, int, str, str]] = []
    for name, etype, aliases in ENTITY_LEXICON:
        for alias in aliases:
            if re.fullmatch(r"[A-Za-z0-9 .&+'\-/:]+", alias):
                pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])")
            else:
                pattern = re.compile(re.escape(alias))
            for m in pattern.finditer(text):
                matches.append((m.start(), m.end(), name, etype))
    for m in MODEL_RE.finditer(text):
        raw = normalize_space(m.group(0))
        if len(raw) < 2:
            continue
        # 只收有明确型号词特征的（M3.1 Flash / GPT-5），过滤 v1.1、V2 这类版本号
        known_prefix = re.match(
            r"^(?:MiniMax|GPT|Claude|Gemini|Llama|Qwen|Kimi|GLM|Grok|DeepSeek|Seed|Step|Yi)", raw, re.I
        )
        if not known_prefix and not re.search(r"\s[A-Za-z]{2,}", raw):
            continue
        matches.append((m.start(), m.end(), raw, "model"))
    matches.sort(key=lambda x: (-(x[1] - x[0]), x[0]))
    chosen: list[tuple[int, int, str, str]] = []
    for start, end, name, etype in matches:
        if all(end <= s or start >= e for s, e, _n, _t in chosen):
            chosen.append((start, end, name, etype))
    counts: dict[str, dict] = {}
    for start, _end, name, etype in sorted(chosen):
        item = counts.setdefault(name, {"name": name, "type": etype, "mentions": 0, "_pos": start})
        item["mentions"] += 1
    entities = sorted(counts.values(), key=lambda d: (-d["mentions"], d["_pos"]))[:30]
    for item in entities:
        item.pop("_pos", None)
    return entities


QUOTE_MARK_RES = [
    re.compile(r"“([^”\n]{6,300})”"),
    re.compile(r"「([^」\n]{6,300})」"),
    re.compile(r"『([^』\n]{6,300})』"),
    re.compile(r'"([^"\n]{10,300})"'),
]
ATTRIB_CN_RE = re.compile(
    r"(?:据|根据|按照)?\s*(?P<speaker>[^，。；：:、\s]{0,20}?)\s*(?:官方|方面|公司)?\s*"
    r"(?<![简名统俗别])(?:称|表示|宣布|指出|透露|声称|发文称|发帖称|写道)\s*[，：:]?\s*"
    r"(?P<claim>[^。；;!?！？]{8,300})"
)
ATTRIB_EN_RE = re.compile(
    r"(?P<speaker>[A-Z][A-Za-z0-9.&'\- ]{1,40}?)\s+"
    r"(?:said|says|announced|claimed|noted|reported|wrote|confirmed|added)\b[,:]?\s*(?P<claim>.{10,300})"
)
_SPEAKER_STOPWORDS = {"其", "该", "这", "它", "他", "她", "本", "此"}


def _clean_speaker(raw: str) -> str:
    speaker = normalize_space(raw).strip("「」『』“”\"'()（）[]【】:：，,。 ")
    if not speaker or speaker in _SPEAKER_STOPWORDS:
        return ""
    if len(speaker) > 24:
        return ""
    return speaker


def extract_quotes(text: str, source_name: str, source_url: str | None, tier: str) -> list[dict]:
    """抽「带引号的原话」和「X 称/表示 …」这类归属句。"""
    quotes: list[dict] = []
    for sentence in split_sentences(text):
        found_marks = False
        for pattern in QUOTE_MARK_RES:
            for m in pattern.finditer(sentence):
                found_marks = True
                qt = normalize_space(m.group(1))
                if len(qt) < 6:
                    continue
                before = sentence[: m.start()]
                speaker = ""
                am = ATTRIB_CN_RE.search(before + "称")
                if am:
                    speaker = _clean_speaker(am.group("speaker"))
                quotes.append(
                    {
                        "text": qt,
                        "speaker": speaker,
                        "source": source_name,
                        "source_url": source_url,
                        "tier": tier,
                    }
                )
        if found_marks:
            continue
        for pattern in (ATTRIB_CN_RE, ATTRIB_EN_RE):
            for m in pattern.finditer(sentence):
                claim = normalize_space(m.group("claim")).strip("，,；;。 ")
                speaker = _clean_speaker(m.group("speaker"))
                if not speaker:
                    continue
                if len(claim) < 8:
                    continue
                quotes.append(
                    {
                        "text": claim,
                        "speaker": speaker,
                        "source": source_name,
                        "source_url": source_url,
                        "tier": tier,
                    }
                )
    # 去重
    out: list[dict] = []
    seen: set[str] = set()
    for q in quotes:
        key = re.sub(r"\W+", "", q["text"])[:50]
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out


# --------------------------------------------------------------------------- #
# tier 判定
# --------------------------------------------------------------------------- #
UNCERTAIN_RE = re.compile(
    r"(?:据称|据悉|传闻|传言|转述|尚未确认|未确认|无法确认|未经证实|未获确认|疑似|"
    r"据传|据说|未逐项确认|可能|或将)"
)
OFFICIAL_ATTRIB_RE = re.compile(
    r"(?:官方|厂商|公司|开发者|团队|MiniMax|OpenAI|Anthropic|DeepSeek|Google|Meta|xAI|"
    r"Mistral|阿里|腾讯|字节|百度|智谱|月之暗面|华为|英伟达|微软|苹果|亚马逊)"
    r"[^，。；]{0,14}?(?:正式)?(?:发布|宣布|公布|称|表示|上线|推出|开源|透露)"
)


def _third_party_hit(name: str) -> bool:
    low = name.lower()
    return any(hint.lower() in low for hint in THIRD_PARTY_HINTS)


def _unverified_hit(name: str) -> bool:
    low = name.lower()
    return any(hint.lower() in low for hint in UNVERIFIED_HINTS)


def classify_report(report: dict, primary_vendors: set[str]) -> tuple[str, str]:
    """把 AIHOT 的一条 report 判成 tier + 理由。"""
    src = report.get("source") or {}
    name = normalize_space(src.get("name") or "")
    orig = (report.get("links") or {}).get("original") or ""
    host = hostname(orig)
    owner = vendor_for_domain(host)

    if src.get("firstParty") is True:
        return "official", f"AIHOT 标记 firstParty：{name or host}"
    if owner and owner in primary_vendors:
        if OFFICIAL_CHANNEL_RE.search(name) or owner in ("openai", "anthropic", "deepmind", "google"):
            return "official", f"{VENDOR_DISPLAY.get(owner, owner)} 官方站点（{host or name}）"
        return "first-party", f"{VENDOR_DISPLAY.get(owner, owner)} 自有渠道（{name}）"
    if owner:
        return "third-party", f"其他厂商/平台渠道（{VENDOR_DISPLAY.get(owner, owner)}）"
    if name:
        vendors_in_name = is_known_vendor_name(name)
        if vendors_in_name & primary_vendors:
            if OFFICIAL_CHANNEL_RE.search(name):
                return "official", f"厂商官方渠道：{name}"
            return "first-party", f"厂商自有渠道（同一方多渠道）：{name}"
    if name and _third_party_hit(name):
        return "third-party", f"媒体/评测/平台信源：{name}"
    if host and media_for_domain(host):
        media_name = media_for_domain(host)
        if media_name in ("X（原 Twitter）", "Twitter", "微信公众号", "LinkedIn"):
            return "unverified", f"社媒个人/账号转述（{media_name}），需人工核验：{name or host}"
        return "third-party", f"媒体报道：{media_name}"
    if name:
        if _unverified_hit(name) or name.startswith(_CHANNEL_PREFIXES):
            return "unverified", f"个人/社媒转述，非媒体或厂商官方：{name}"
    if host:
        return "unverified", f"来源域名不在官方/媒体白名单：{host}"
    return "unverified", "无可靠出处信息"


def classify_page(url: str) -> tuple[str, str, str]:
    """URL 页面 → (tier, reason, 建议 source_name)。"""
    host = hostname(url)
    owner = vendor_for_domain(host)
    if owner:
        return (
            "official",
            f"域名 {host} 是 {VENDOR_DISPLAY.get(owner, owner)} 官方渠道",
            f"{VENDOR_DISPLAY.get(owner, owner)} 官方",
        )
    media = media_for_domain(host)
    if media:
        return "third-party", f"媒体/平台页面：{media}", media
    return (
        "unverified",
        f"域名 {host} 不在厂商官方/媒体白名单，事实需人工核验",
        host or "未知来源",
    )


def digest_sentence_tier(sentence: str, primary_vendors: set[str]) -> tuple[str, str]:
    """AIHOT 综述里的一句话判 tier：默认 third-party（保守），明确官方口径升 official。"""
    if UNCERTAIN_RE.search(sentence):
        return "unverified", "AIHOT 综述含「据称/未确认/未说明」等不确定表述"
    m = re.search(r"(?:据|根据)?\s*([^，。；：]{1,20}?)\s*(?:官方|方面)?\s*"
                  r"(?<![简名统俗别])(?:称|表示|宣布|指出|透露|发文称|发帖称)", sentence)
    speaker = _clean_speaker(m.group(1)) if m else ""
    if speaker:
        if speaker in ("官方", "厂商", "公司"):
            return "official", f"综述明确标注「{speaker}」口径"
        vendors_named = is_known_vendor_name(speaker)
        if vendors_named & primary_vendors:
            return "official", f"综述明确归属厂商：{speaker}"
        if _third_party_hit(speaker):
            return "third-party", f"综述归属第三方：{speaker}"
        return "third-party", f"综述归属：{speaker}"
    if OFFICIAL_ATTRIB_RE.search(sentence):
        return "third-party", "AIHOT 综述综合转述，未逐句标注出处（保守定级）"
    return "third-party", "AIHOT 综述转述，未标注出处（保守定级）"


def license_for_url(url: str) -> dict:
    host = hostname(url)
    owner = vendor_for_domain(host)
    if owner:
        return {
            "commercial_ok": "unknown",
            "note": (
                f"厂商官方页面（{VENDOR_DISPLAY.get(owner, owner)}）：事实可引用，"
                "转载全文/图片需遵守该站版权与转载政策，发布时注明原文链接。"
            ),
            "url": url,
        }
    if media_for_domain(host):
        return {
            "commercial_ok": "unknown",
            "note": (
                "媒体页面：通常只可引用短句并链接原文，整段/配图转载需授权；"
                "事实最终以厂商官方发布为准。"
            ),
            "url": url,
        }
    return {
        "commercial_ok": "unknown",
        "note": "来源域名未识别：使用前请人工确认版权与事实出处，优先改用厂商官方原文。",
        "url": url,
    }


LICENSE_FILE = {
    "commercial_ok": "unknown",
    "note": (
        "用户提供的文本：来源、版权、时效均未知。发布前必须找到原始出处"
        "（优先厂商官方发布）并逐个核对数字。"
    ),
}


# --------------------------------------------------------------------------- #
# 素材卡 Builder
# --------------------------------------------------------------------------- #
class CardBuilder:
    def __init__(self, origin: str, max_facts: int = 80, max_numbers: int = 200, max_quotes: int = 40):
        self.max_facts = max_facts
        self.max_numbers = max_numbers
        self.max_quotes = max_quotes
        self.card: dict = {
            "schema_version": SCHEMA_VERSION,
            "origin": origin,
            "title": "",
            "source_name": "",
            "source_url": "",
            "published_at": None,
            "fetched_at": now_iso(),
            "language": "unknown",
            "summary": "",
            "body": "",
            "entities": [],
            "facts": [],
            "numbers": [],
            "quotes": [],
            "timeline": [],
            "links": {"originals": [], "aihot": None, "related": []},
            "source_meta": {},
            "license": {},
            "warnings": [],
        }
        self._fact_keys: set[str] = set()
        self._num_map: dict[str, dict] = {}
        self._quote_keys: set[str] = set()
        self._truncated = {"facts": False, "numbers": False, "quotes": False}
        self._entity_text_parts: list[str] = []

    # -- 基础写入 ----------------------------------------------------------
    def warn(self, message: str) -> None:
        if message and message not in self.card["warnings"]:
            self.card["warnings"].append(message)

    def set(self, **fields) -> None:
        for key, value in fields.items():
            if value is not None:
                self.card[key] = value

    def add_link(self, url: str | None, *, aihot: bool = False, related: bool = False) -> None:
        if not url:
            return
        if aihot:
            self.card["links"]["aihot"] = url
            return
        target = self.card["links"]["related" if related else "originals"]
        if url not in target:
            target.append(url)

    # -- fact --------------------------------------------------------------
    def fact(
        self,
        text: str,
        source: str,
        tier: str,
        reason: str,
        *,
        url: str | None = None,
        evidence: list[str] | None = None,
        published_at: str | None = None,
        kind: str = "statement",
    ) -> bool:
        text = normalize_durations(normalize_space(text))
        if len(text) < 8:
            return False
        key = re.sub(r"[\s，。；：、,.!?！？:;\"'“”『』「」()（）]", "", text)[:70]
        if not key or key in self._fact_keys:
            return False
        if len(self.card["facts"]) >= self.max_facts:
            self._truncated["facts"] = True
            return False
        self._fact_keys.add(key)
        fact = {
            "id": "",
            "text": text,
            "source": source or "未标注",
            "source_url": url,
            "published_at": published_at,
            "tier": tier,
            "tier_reason": reason,
            "evidence": [u for u in (evidence or []) if u],
            "kind": kind,
        }
        self.card["facts"].append(fact)
        self._entity_text_parts.append(text)
        return True

    # -- number ------------------------------------------------------------
    def numbers_from(self, text: str, source: str, url: str | None, tier: str) -> int:
        added = 0
        for item in extract_numbers(text):
            context = item["context"]
            dedupe = re.sub(r"\s+", "", context)[:60]
            key = f"{item['value']}|{item['unit']}|{dedupe}"
            existing = self._num_map.get(key)
            if existing:
                existing["occurrences"] += 1
                continue
            if len(self._num_map) >= self.max_numbers:
                self._truncated["numbers"] = True
                continue
            entry = {
                "id": "",
                "value": item["value"],
                "value_num": item["value_num"],
                "raw": item["raw"],
                "unit": item["unit"],
                "context": context,
                "source": source,
                "source_url": url,
                "tier": tier,
                "occurrences": 1,
            }
            self._num_map[key] = entry
            added += 1
        return added

    # -- quote -------------------------------------------------------------
    def quotes_from(self, text: str, source: str, url: str | None, tier: str) -> None:
        for quote in extract_quotes(text, source, url, tier):
            key = re.sub(r"\W+", "", quote["text"])[:50]
            if not key or key in self._quote_keys:
                continue
            if len(self.card["quotes"]) >= self.max_quotes:
                self._truncated["quotes"] = True
                continue
            self._quote_keys.add(key)
            self.card["quotes"].append(
                {
                    "id": "",
                    "text": quote["text"],
                    "speaker": quote["speaker"],
                    "source": quote["source"],
                    "source_url": quote["source_url"],
                    "tier": quote["tier"],
                }
            )

    # -- timeline ----------------------------------------------------------
    def timeline(self, when: str | None, event: str, source: str = "", url: str | None = None,
                 tier: str = "") -> None:
        if not when or not event:
            return
        event = normalize_space(event)
        if len(event) < 4:
            return
        for item in self.card["timeline"]:
            if item["time"] == when and item["event"] == event:
                return
        self.card["timeline"].append(
            {"time": when, "event": event, "source": source, "url": url, "tier": tier}
        )

    # -- finalize ----------------------------------------------------------
    def finalize(self) -> dict:
        card = self.card
        if self._truncated["facts"]:
            card["warnings"].append(
                f"facts 超过上限 {self.max_facts} 条，已截断（可调 --max-facts）"
            )
        if self._truncated["numbers"]:
            card["warnings"].append(
                f"numbers 超过上限 {self.max_numbers} 条，已截断（可调 --max-numbers）"
            )
        if self._truncated["quotes"]:
            card["warnings"].append(f"quotes 超过上限 {self.max_quotes} 条，已截断")
        for idx, item in enumerate(card["facts"], 1):
            item["id"] = f"f{idx}"
        card["numbers"] = list(self._num_map.values())
        for idx, item in enumerate(card["numbers"], 1):
            item["id"] = f"n{idx}"
        for idx, item in enumerate(card["quotes"], 1):
            item["id"] = f"q{idx}"
        card["timeline"].sort(key=lambda x: x["time"], reverse=True)
        if len(card["timeline"]) > 60:
            card["timeline"] = card["timeline"][:60]
            card["warnings"].append("timeline 超过 60 条，已截断")
        text_for_entities = "\n".join(self._entity_text_parts) or card["body"] or card["title"]
        card["entities"] = extract_entities(text_for_entities)
        card["language"] = detect_language((card["body"] or "") + "\n" + " ".join(
            f["text"] for f in card["facts"]
        ))
        if not card["summary"]:
            if card["facts"]:
                card["summary"] = clip(card["facts"][0]["text"], 220)
        if not card["license"]:
            card["license"] = LICENSE_FILE
        if not card["source_meta"]:
            card["source_meta"] = {"source_type": card["origin"]}
        card["tier_counts"] = {
            tier: sum(1 for f in card["facts"] if f["tier"] == tier) for tier in TIER_ORDER
        }
        return card


# --------------------------------------------------------------------------- #
# AIHOT：复用 tools/aihot_fetch.py（失败时退回内置客户端）
# --------------------------------------------------------------------------- #
class _FallbackResponse:
    def __init__(self, url: str, text: str, content_type: str = ""):
        self.url = url
        self.text = text
        self.content_type = content_type
        self.status = 200
        self.from_cache = False

    def json(self):
        try:
            return json.loads(self.text)
        except ValueError as exc:
            raise PrepError(f"AIHOT 返回不是合法 JSON：{exc}") from exc


class _FallbackAihotClient:
    """tools/aihot_fetch.py 不可用时的极简替代（无缓存/限流，仅保证能跑）。"""

    def __init__(self, cache_dir: Path, timeout: float = 20.0, refresh: bool = False):
        self.cache_dir = cache_dir
        self.timeout = timeout

    def get(self, path: str, accept: str = "application/json"):
        url = path if path.startswith("http") else AIHOT_BASE + path
        text, final_url, ctype = http_get(url, timeout=self.timeout, accept=accept)
        return _FallbackResponse(final_url, text, ctype)


def load_aihot_client(args):
    cache_dir = Path(args.cache_dir).expanduser() if args.cache_dir else DEFAULT_CACHE_DIR
    tool = ROOT / "tools" / "aihot_fetch.py"
    if tool.exists():
        try:
            spec = importlib.util.spec_from_file_location("_aihot_fetch_for_prep", tool)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            client = module.AihotClient(
                cache_dir=cache_dir, timeout=args.timeout, refresh=args.refresh
            )
            return client, cache_dir, "tools/aihot_fetch.py"
        except Exception as exc:  # pragma: no cover - 兜底
            log(f"[警告] 复用 tools/aihot_fetch.py 失败（{exc}），改用内置 HTTP 客户端")
    return _FallbackAihotClient(cache_dir=cache_dir, timeout=args.timeout), cache_dir, "builtin"


def normalize_public_id(raw: str) -> str:
    pid = (raw or "").strip()
    if "/" in pid:
        pid = pid.rstrip("/").split("/")[-1]
    if not re.match(r"^[0-9A-Za-z][0-9A-Za-z-]{7,63}$", pid):
        raise PrepError(
            f"publicId 格式不对：{raw!r}。应为 stories/<uuid> 的最后一段，"
            "例如 589d286a-2a6d-48be-b14a-e61390534ec3"
        )
    return pid


def _find_cached_api(cache_dir: Path, suffix: str):
    http_dir = cache_dir / "http"
    if not http_dir.is_dir():
        return None
    for path in sorted(http_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        url = str(payload.get("url") or "").rstrip("/")
        body = payload.get("body")
        if url.endswith(suffix) and isinstance(body, str):
            try:
                return json.loads(body)
            except ValueError:
                continue
    return None


def find_local_story(cache_dir: Path, pid: str):
    cached = _find_cached_api(cache_dir, f"/api/v1/stories/{pid}")
    if cached:
        return cached, "cache"
    for path in sorted(DATA_RAW.glob(f"*/story/{pid}.json")):
        try:
            return json.loads(path.read_text(encoding="utf-8")), f"sample:{path}"
        except (OSError, ValueError):
            continue
    return None, None


def find_local_hot(cache_dir: Path):
    cached = _find_cached_api(cache_dir, "/api/v1/hot-topics")
    if cached:
        return cached, "cache"
    snapshots = sorted(DATA_RAW.glob("*/hot-topics.json"))
    for path in reversed(snapshots):
        try:
            return json.loads(path.read_text(encoding="utf-8")), f"sample:{path}"
        except (OSError, ValueError):
            continue
    return None, None


def fetch_story(pid: str, args) -> tuple[dict, str, list[str]]:
    client, cache_dir, backend = load_aihot_client(args)
    warnings: list[str] = []
    if not args.offline:
        try:
            resp = client.get(f"/api/v1/stories/{pid}")
            data = resp.json()
            story = data.get("story") or {}
            if not story.get("title"):
                raise ValueError("接口返回缺少 story.title")
            transport = "cache" if getattr(resp, "from_cache", False) else "network"
            return data, transport, warnings
        except Exception as exc:
            warnings.append(f"实时获取 AIHOT story 失败：{exc}")
            log(f"[警告] 实时获取失败（{exc}），尝试本地缓存/样本…")
    data, origin = find_local_story(cache_dir, pid)
    if not data:
        raise PrepError(
            "无法获取 AIHOT story "
            f"{pid}。已尝试：实时接口（{backend}）+ 本地缓存 {cache_dir} + data/raw 样本。"
            + (f" 失败原因：{warnings[-1]}" if warnings else "")
            + "。请检查网络/AIHOT 可用性，或改用 --url / --file 输入。"
        )
    warnings.append(f"使用本地离线数据：{origin}")
    return data, "local", warnings


def fetch_hot(args) -> tuple[dict, str, list[str]]:
    client, cache_dir, backend = load_aihot_client(args)
    warnings: list[str] = []
    if not args.offline:
        try:
            resp = client.get("/api/v1/hot-topics")
            data = resp.json()
            if not data.get("items"):
                raise ValueError("热点接口返回 items 为空")
            transport = "cache" if getattr(resp, "from_cache", False) else "network"
            return data, transport, warnings
        except Exception as exc:
            warnings.append(f"实时获取 AIHOT 热点失败：{exc}")
            log(f"[警告] 实时获取热点失败（{exc}），尝试本地快照…")
    data, origin = find_local_hot(cache_dir)
    if not data:
        raise PrepError(
            f"无法获取 AIHOT 热点榜（接口 {AIHOT_BASE}/api/v1/hot-topics 与本地快照都不可用）。"
            "请检查网络，或改用 --url / --file。"
        )
    warnings.append(f"使用本地离线热点快照：{origin}")
    return data, "local", warnings


# --------------------------------------------------------------------------- #
# 四种输入的素材卡构造
# --------------------------------------------------------------------------- #
def build_from_aihot_story(args) -> dict:
    pid = normalize_public_id(args.aihot_story)
    data, transport, warnings = fetch_story(pid, args)
    story = data.get("story") or {}
    title = normalize_space(story.get("title") or "")
    if not title:
        raise PrepError(f"AIHOT story {pid} 没有标题，无法构图。")
    digest = (story.get("digest") or "").strip()
    latest = normalize_space(story.get("latest") or "")
    reports = story.get("reports") or []
    # 主角厂商只看标题（避免把综述里提到的 OpenRouter/Ollama 等平台当成「厂商官方」）；
    # 标题里没有已知厂商时，才退一步看综述首段。
    primary_vendors = detect_vendors(title) or detect_vendors(
        split_paragraphs(digest)[0] if digest else ""
    )
    links = story.get("links") or {}
    story_url = links.get("aihot") or f"{AIHOT_STORY_PAGE}{pid}"

    builder = CardBuilder("aihot", max_facts=args.max_facts, max_numbers=args.max_numbers)
    builder.set(
        title=title,
        source_name=f"AIHOT（{story.get('sourceCount') or len(reports)} 个信源 / "
        f"{story.get('reportCount') or len(reports)} 条报道）",
        source_url=story_url,
        published_at=normalize_datetime(story.get("firstReportAt")),
        summary=clip(split_paragraphs(digest)[0] if digest else latest, 260),
        body=normalize_block(digest + ("\n\n" + latest if latest else "")),
    )
    builder.card["source_meta"] = {
        "source_type": "aihot",
        "aihot_story_id": story.get("publicId") or pid,
        "status": story.get("status"),
        "source_count": story.get("sourceCount"),
        "report_count": story.get("reportCount"),
        "first_report_at": normalize_datetime(story.get("firstReportAt")),
        "latest_at": normalize_datetime(story.get("latestAt")),
        "digest_updated_at": normalize_datetime(story.get("digestUpdatedAt")),
        "transport": transport,
    }
    builder.card["license"] = dict(AIHOT_LICENSE)
    builder.add_link(story_url, aihot=True)
    builder.add_link(story_url)
    for warning in warnings:
        builder.warn(warning)

    # 1) AI 综述：每句一条 fact（AIBOT 综述本身就是转述，默认 third-party）
    if digest:
        for paragraph in split_paragraphs(digest):
            for sentence in split_sentences(paragraph):
                tier, reason = digest_sentence_tier(sentence, primary_vendors)
                evidence = _matching_report_urls(sentence, reports)
                builder.fact(
                    sentence,
                    "AIHOT AI 综述",
                    tier,
                    reason,
                    url=story_url,
                    evidence=evidence,
                    published_at=normalize_datetime(story.get("digestUpdatedAt")),
                    kind="digest",
                )
                builder.numbers_from(sentence, "AIHOT AI 综述", story_url, tier)
                builder.quotes_from(sentence, "AIHOT AI 综述", story_url, tier)
    # 2) 最新进展
    if latest:
        tier, reason = digest_sentence_tier(latest, primary_vendors)
        builder.fact(
            latest, "AIHOT 最新进展", tier, reason, url=story_url,
            published_at=normalize_datetime(story.get("latestAt")), kind="latest",
        )
        builder.numbers_from(latest, "AIHOT 最新进展", story_url, tier)

    # 3) 每条 report：标题 + 摘要句，带来源、tier、原文链接
    for report in reports:
        if not isinstance(report, dict):
            continue
        rep_title = normalize_space(report.get("title") or "")
        rep_summary = (report.get("summary") or "").strip()
        src = report.get("source") or {}
        src_name = normalize_space(src.get("name") or "")
        orig = (report.get("links") or {}).get("original") or ""
        published = normalize_datetime(report.get("publishedAt"))
        tier, reason = classify_report(report, primary_vendors)
        if rep_title:
            builder.fact(
                rep_title, src_name or "未标注信源", tier, reason,
                url=orig or None, published_at=published, kind="report",
            )
            builder.numbers_from(rep_title, src_name or "未标注信源", orig or None, tier)
            builder.quotes_from(rep_title, src_name or "未标注信源", orig or None, tier)
        for sentence in split_sentences(rep_summary)[:4]:
            builder.fact(
                sentence, src_name or "未标注信源", tier, reason,
                url=orig or None, published_at=published, kind="report",
            )
            builder.numbers_from(sentence, src_name or "未标注信源", orig or None, tier)
            builder.quotes_from(sentence, src_name or "未标注信源", orig or None, tier)
        if published:
            builder.timeline(published, rep_title or clip(rep_summary, 80), src_name, orig or None, tier)
        builder.add_link(orig)

    # 4) storyline / related 当导航链接，不当事实
    for key in ("storyline", "related"):
        for ref in story.get(key) or []:
            if isinstance(ref, dict):
                ref_url = (ref.get("links") or {}).get("aihot")
                if ref_url:
                    builder.add_link(ref_url, related=True)
    if not builder.card["facts"]:
        raise PrepError(f"AIHOT story {pid} 里没抽到任何事实（digest/reports 都是空的？）")
    card = builder.finalize()
    if len(card["facts"]) < 5:
        card["warnings"].append(
            "抽到的事实较少，可能是该 story 报道/综述较短；写稿前建议补官方原文。"
        )
    return card


def _matching_report_urls(sentence: str, reports: list) -> list[str]:
    """找与综述句子关键词重合度高的 report 原文链接，作为 fact.evidence。"""
    tokens = _keywords(sentence)
    if not tokens:
        return []
    scored: list[tuple[int, str]] = []
    for report in reports:
        if not isinstance(report, dict):
            continue
        url = (report.get("links") or {}).get("original")
        if not url:
            continue
        rep_text = f"{report.get('title') or ''} {report.get('summary') or ''}"
        overlap = len(tokens & _keywords(rep_text))
        if overlap >= 3:
            scored.append((overlap, url))
    scored.sort(reverse=True)
    return [url for _score, url in scored[:3]]


def _keywords(text: str) -> set[str]:
    tokens = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9.+-]{2,}", text)}
    cjk = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
    tokens.update(cjk)
    return tokens


def build_from_aihot_hot(args) -> dict:
    data, transport, warnings = fetch_hot(args)
    items = [it for it in (data.get("items") or []) if isinstance(it, dict)][: args.limit]
    if not items:
        raise PrepError("AIHOT 热点榜为空（items 为空），请稍后重试。")
    latest_times = [normalize_datetime(it.get("latestAt")) for it in items]
    latest_times = [t for t in latest_times if t]
    hot_date = (
        max(latest_times)[:10] if latest_times else datetime.now(SH_TZ).date().isoformat()
    )
    builder = CardBuilder("aihot", max_facts=max(args.max_facts, len(items) * 2),
                          max_numbers=args.max_numbers)
    builder.set(
        title=f"AIHOT 热点榜 Top {len(items)} · {hot_date}",
        source_name="AIHOT 热点榜",
        source_url=AIHOT_BASE + "/",
        published_at=max(latest_times) if latest_times else None,
        summary="；".join(f"#{it.get('rank')} {it.get('title')}" for it in items)[:300],
        body="\n".join(f"#{it.get('rank')} {it.get('title')}" for it in items),
    )
    builder.card["license"] = dict(AIHOT_LICENSE)
    builder.card["source_meta"] = {
        "source_type": "aihot-hot",
        "transport": transport,
        "count": data.get("count"),
        "items": [],
    }
    builder.add_link(AIHOT_BASE + "/")
    for warning in warnings:
        builder.warn(warning)

    for item in items:
        src_name = normalize_space((item.get("source") or {}).get("name") or "")
        orig = (item.get("links") or {}).get("original")
        story_url = (item.get("links") or {}).get("story")
        published = normalize_datetime(item.get("latestAt"))
        tier, reason = classify_report(
            {"source": item.get("source") or {}, "links": item.get("links") or {}},
            detect_vendors(str(item.get("title") or "")),
        )
        title = normalize_space(item.get("title") or "")
        if title:
            builder.fact(title, src_name or "未标注", tier, reason, url=orig or None,
                         published_at=published, kind="hot")
            builder.numbers_from(title, src_name or "未标注", orig or None, tier)
            builder.quotes_from(title, src_name or "未标注", orig or None, tier)
        if published:
            builder.timeline(published, title, src_name, orig or None, tier)
        builder.add_link(orig)
        builder.add_link(story_url, related=True)
        builder.card["source_meta"]["items"].append(
            {
                "rank": item.get("rank"),
                "title": title,
                "source_name": src_name,
                "source_url": orig,
                "story_url": story_url,
                "signal_count": item.get("signalCount"),
                "source_count": item.get("sourceCount"),
                "participant_count": item.get("participantCount"),
                "latest_at": published,
                "story_id": (story_url or "").rstrip("/").split("/")[-1] if story_url else None,
            }
        )
    return builder.finalize()


def build_from_url(args) -> dict:
    url = args.url.strip()
    text, final_url, content_type = http_get(url, timeout=args.timeout)
    lowered = content_type.lower()
    is_html = "html" in lowered or bool(
        re.search(r"<(?:html|body|article|p)\b", text[:4000], re.I)
    )

    if is_html:
        page = parse_html_page(text, final_url)
    else:
        # 纯文本 / JSON 接口
        plain = normalize_block(text)
        if len(plain) < 100:
            raise PrepError(
                f"URL 返回的内容太短/不像正文（{len(plain)} 字，Content-Type: {content_type}）："
                f"{final_url}。请确认链接是文章页，或改用 --file 粘贴正文。"
            )
        page = {
            "title": "",
            "title_raw": "",
            "site_name": "",
            "description": "",
            "published_at_raw": "",
            "published_at": _find_date_in_text(plain[:2000]),
            "paragraphs": split_paragraphs(plain),
            "blocks": [],
        }
        page["blocks"] = [{"kind": "body", "text": p} for p in page["paragraphs"]]

    tier, reason, suggested_name = classify_page(final_url)
    title = args.title or page["title"] or clip(page["paragraphs"][0], 80)
    source_name = args.source_name or page["site_name"] or suggested_name
    host = hostname(final_url)

    builder = CardBuilder("url", max_facts=args.max_facts, max_numbers=args.max_numbers)
    builder.set(
        title=title,
        source_name=source_name,
        source_url=final_url,
        published_at=args.published_at or page["published_at"],
        summary=page["description"] or clip(page["paragraphs"][0], 260),
        body=normalize_block("\n\n".join(page["paragraphs"])),
    )
    builder.card["license"] = license_for_url(final_url)
    builder.card["source_meta"] = {
        "source_type": "url",
        "domain": host,
        "final_url": final_url,
        "content_type": content_type,
        "paragraph_count": len(page["paragraphs"]),
        "chars": sum(len(p) for p in page["paragraphs"]),
        "title_raw": page.get("title_raw") or "",
        "published_at_raw": page.get("published_at_raw") or "",
    }
    builder.add_link(final_url)

    blocks = page.get("blocks") or [{"kind": "body", "text": p} for p in page["paragraphs"]]
    for block in blocks:
        if block.get("kind") == "heading":
            continue  # 标题块不进 facts/numbers，只留在 body 里
        for sentence in split_sentences(block["text"]):
            if _looks_like_label_link(sentence):
                continue
            sent_tier, sent_reason = tier, reason
            if UNCERTAIN_RE.search(sentence):
                sent_tier, sent_reason = "unverified", "正文含「据称/未确认」等不确定表述"
            elif OFFICIAL_ATTRIB_RE.search(sentence):
                sent_tier, sent_reason = "official", "正文明确引述官方口径"
            builder.fact(
                sentence, source_name, sent_tier, sent_reason,
                url=final_url, published_at=builder.card["published_at"], kind="body",
            )
            builder.numbers_from(sentence, source_name, final_url, sent_tier)
            builder.quotes_from(sentence, source_name, final_url, sent_tier)

    for when, event in _date_events(builder.card["body"], builder.card["published_at"]):
        builder.timeline(when, event, source_name, final_url, tier)
    if builder.card["published_at"]:
        builder.timeline(builder.card["published_at"], "页面发布时间", source_name, final_url, tier)

    if not builder.card["facts"]:
        raise PrepError(
            f"页面正文抽到了 {len(page['paragraphs'])} 段，但没有可用的句子事实：{final_url}"
        )
    card = builder.finalize()
    card["warnings"].append(
        f"页面对外部事实按「{tier}」定级（{reason}）；发布前请优先核对厂商官方原文。"
    )
    return card


# --------------------------------------------------------------------------- #
# 本地文本 / stdin
# --------------------------------------------------------------------------- #
def read_text_input(path_arg: str) -> tuple[str, str]:
    """返回 (text, 展示用来源)。path_arg 为 '-' 时读 stdin。"""
    if path_arg == "-":
        data = sys.stdin.buffer.read()
        label = "stdin（用户粘贴）"
    else:
        path = Path(path_arg).expanduser()
        if not path.exists():
            raise PrepError(
                f"文件不存在：{path}（解析后绝对路径 {path.resolve()}）。"
                "如果是从别处复制的文本，可以改用：pbpaste | prep_input.py --file -"
            )
        if path.is_dir():
            raise PrepError(f"--file 需要文件，不是目录：{path}")
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise PrepError(f"读取文件失败：{path}（{exc}）") from exc
        label = "用户粘贴文本" if not path.is_file() else str(path)
    if not data.strip():
        raise PrepError("输入文本为空（0 字节）。请检查文件/管道是否有内容。")
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding), label
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace"), label


def build_from_text(args) -> dict:
    raw_text, label = read_text_input(args.file)
    if args.title:
        title = args.title
    else:
        title = infer_text_title(raw_text, looks_markdown(raw_text))
    markdown = looks_markdown(raw_text)
    cleaned = strip_markdown(raw_text) if markdown else normalize_block(raw_text)
    paragraphs = split_paragraphs(cleaned)
    if not paragraphs:
        raise PrepError("输入文本清洗后为空；请确认粘贴的是正文而不是纯符号。")

    base_tier = args.tier or "unverified"
    if base_tier == "unverified":
        base_reason = "用户提供的文本，来源/版权/时效均未知（保守定级）"
    else:
        base_reason = f"用户在 --file 输入时显式指定 tier={base_tier}"

    builder = CardBuilder("file", max_facts=args.max_facts, max_numbers=args.max_numbers)
    published_at = args.published_at or _find_date_in_text(cleaned[:3000])
    builder.set(
        title=title or "（无标题文本）",
        source_name=args.source_name or ("用户粘贴文本" if label.startswith("stdin") else label),
        source_url=None,
        published_at=published_at,
        summary=clip(paragraphs[0], 260),
        body=normalize_block(cleaned),
    )
    builder.card["license"] = dict(LICENSE_FILE)
    builder.card["source_meta"] = {
        "source_type": "file",
        "input": label,
        "format": "markdown" if markdown else "plain",
        "chars": len(cleaned),
        "paragraph_count": len(paragraphs),
    }
    for paragraph in paragraphs:
        for sentence in split_sentences(paragraph):
            sent_tier, sent_reason = base_tier, base_reason
            if UNCERTAIN_RE.search(sentence):
                sent_tier, sent_reason = "unverified", "文本含「据称/未确认」等不确定表述"
            elif OFFICIAL_ATTRIB_RE.search(sentence) and base_tier in ("official", "first-party", "third-party"):
                sent_tier, sent_reason = "official", "文本明确引述官方口径"
            builder.fact(
                sentence, builder.card["source_name"], sent_tier, sent_reason,
                published_at=published_at, kind="text",
            )
            builder.numbers_from(sentence, builder.card["source_name"], None, sent_tier)
            builder.quotes_from(sentence, builder.card["source_name"], None, sent_tier)
    for when, event in _date_events(cleaned, published_at):
        builder.timeline(when, event, builder.card["source_name"], None, base_tier)
    if not builder.card["facts"]:
        raise PrepError("输入文本清洗后没有抽到句子级事实，请检查内容。")
    card = builder.finalize()
    if base_tier == "unverified":
        card["warnings"].append(
            "来源为粘贴文本：所有事实默认 unverified，发布前必须找到原始出处（优先厂商官方）并核对数字。"
        )
    return card


# --------------------------------------------------------------------------- #
# 正文里的日期 → 时间线
# --------------------------------------------------------------------------- #
def _find_date_in_text(text: str) -> str | None:
    patterns = [
        r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})日?",
        r"(\d{1,2})\s*月\s*(\d{1,2})\s*日",
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if not m:
            continue
        if len(m.groups()) == 3:
            return normalize_datetime(m.group(0))
        month, day = int(m.group(1)), int(m.group(2))
        year = datetime.now(SH_TZ).year
        try:
            return datetime(year, month, day).date().isoformat()
        except ValueError:
            continue
    return None


def _date_events(text: str, published_at: str | None) -> list[tuple[str, str]]:
    """正文中出现「10 月 23 日开放权重」这类带日期的事件句。"""
    if not text:
        return []
    year = None
    if published_at and re.match(r"^\d{4}", published_at):
        year = int(published_at[:4])
    year = year or datetime.now(SH_TZ).year
    events: list[tuple[str, str]] = []
    seen: set[str] = set()
    for sentence in split_sentences(text):
        if len(sentence) < 8:
            continue
        dates = re.findall(r"(?<!\d)(\d{1,2})\s*月\s*(\d{1,2})\s*日|(?<!\d)(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", sentence)
        for match in dates:
            m1, d1, y2, m2, d2 = match
            if y2:
                iso = f"{int(y2):04d}-{int(m2):02d}-{int(d2):02d}"
            else:
                month, day = int(m1), int(d1)
                try:
                    iso = datetime(year, month, day).date().isoformat()
                except ValueError:
                    continue
            if iso in seen:
                continue
            seen.add(iso)
            event = clip(sentence, 120)
            events.append((iso, event))
    return events[:10]


# --------------------------------------------------------------------------- #
# 输出：Markdown / JSON / 落盘 / check
# --------------------------------------------------------------------------- #
def _md_link(text: str, url: str | None) -> str:
    if not url:
        return text
    return f"[{text}]({url})" if text else url


def _inline(text: str) -> str:
    return (text or "").replace("`", "ˋ").replace("\n", " ")


def render_markdown(card: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {card.get('title') or '（无标题）'}")
    lines.append("")
    lines.append(f"**来源**：{card.get('source_name') or '—'}")
    if card.get("source_url"):
        lines.append(f"**链接**：{card['source_url']}")
    lines.append(
        f"**来源类型**：`{card.get('origin')}`　·　"
        f"**发布**：{card.get('published_at') or '未识别'}　·　"
        f"**抓取**：{card.get('fetched_at')}"
    )
    tier_counts = card.get("tier_counts") or {}
    tier_line = " / ".join(f"{k} {v}" for k, v in tier_counts.items())
    lines.append(f"**事实分层**：{tier_line}")
    license_info = card.get("license") or {}
    if license_info.get("note"):
        lines.append(f"**商用提示**：{license_info['note']}")
    meta = card.get("source_meta") or {}
    if meta.get("aihot_story_id"):
        lines.append(
            f"**AIHOT**：story `{meta['aihot_story_id']}` · "
            f"{meta.get('source_count')} 信源 / {meta.get('report_count')} 报道 · "
            f"transport={meta.get('transport')}"
        )
    lines.append("")
    lines.append("## 摘要")
    lines.append("")
    lines.append(card.get("summary") or "（无摘要）")
    lines.append("")

    lines.append("## 关键事实（按可信度分层）")
    lines.append("")
    facts = card.get("facts") or []
    for fact in facts:
        tier = fact.get("tier") or "unverified"
        text = _inline(fact.get("text") or "")
        src = _inline(fact.get("source") or "")
        url = fact.get("source_url")
        tail = f"　——〔{TIER_LABEL.get(tier, tier)}｜{src}"
        if url:
            tail += f"｜{url}"
        tail += "〕"
        lines.append(f"- `[{tier}]` {text}{tail}")
    if not facts:
        lines.append("- （没抽到事实）")
    lines.append("")

    lines.append("## 数字（事实核验原料）")
    lines.append("")
    numbers = card.get("numbers") or []
    for num in numbers:
        raw = _inline(num.get("raw") or num.get("value") or "")
        context = _inline(num.get("context") or "")
        source = _inline(num.get("source") or "")
        tier = num.get("tier") or ""
        lines.append(f"- `{raw}`（单位 {num.get('unit') or '—'}）— {context}〔{source}｜{tier}〕")
    if not numbers:
        lines.append("- （没抽到数字）")
    lines.append("")

    lines.append("## 引语")
    lines.append("")
    quotes = card.get("quotes") or []
    for quote in quotes:
        speaker = _inline(quote.get("speaker") or "未标注")
        lines.append(
            f"- “{_inline(quote.get('text') or '')}” — {speaker}"
            f"〔{_inline(quote.get('source') or '')}｜{quote.get('tier')}〕"
        )
    if not quotes:
        lines.append("- （没抽到引语；中文新闻常没有直接引语，可回原文补）")
    lines.append("")

    lines.append("## 实体")
    lines.append("")
    entities = card.get("entities") or []
    if entities:
        lines.append("、".join(
            f"{e['name']}（{e['type']}×{e['mentions']}）" for e in entities
        ))
    else:
        lines.append("（没识别到已知实体）")
    lines.append("")

    lines.append("## 时间线")
    lines.append("")
    timeline = card.get("timeline") or []
    for item in timeline:
        src = _inline(item.get("source") or "")
        url = item.get("url")
        event = _inline(item.get("event") or "")
        line = f"- {item.get('time')} · {event}"
        if src:
            line += f"〔{src}〕"
        if url:
            line += f" {url}"
        lines.append(line)
    if not timeline:
        lines.append("- （没抽到时间线；可手动补「日期 → 事件」）")
    lines.append("")

    links = card.get("links") or {}
    lines.append("## 来源链接")
    lines.append("")
    if links.get("aihot"):
        lines.append(f"- AIHOT 阅读页：{links['aihot']}")
    for url in links.get("originals") or []:
        lines.append(f"- 原文：{url}")
    for url in links.get("related") or []:
        lines.append(f"- 相关：{url}")
    if not any((links.get("aihot"), links.get("originals"), links.get("related"))):
        lines.append("- （无外部链接）")
    lines.append("")

    if card.get("warnings"):
        lines.append("## 警告 / 待人工确认")
        lines.append("")
        for warning in card["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def check_summary(card: dict) -> str:
    facts = card.get("facts") or []
    numbers = card.get("numbers") or []
    quotes = card.get("quotes") or []
    entities = card.get("entities") or []
    timeline = card.get("timeline") or []
    tier_counts = card.get("tier_counts") or {}
    tier_line = " / ".join(f"{k} {tier_counts.get(k, 0)}" for k in TIER_ORDER)
    meta = card.get("source_meta") or {}
    lines = [
        f"[check] title    : {card.get('title') or '（无标题）'}",
        f"[check] origin   : {card.get('origin')}  ·  schema {card.get('schema_version')}",
        f"[check] source   : {card.get('source_name') or '—'}"
        + (f"  →  {card['source_url']}" if card.get("source_url") else ""),
        f"[check] published: {card.get('published_at') or '未识别'}",
        f"[check] facts    : {len(facts)}  ({tier_line})",
        f"[check] numbers  : {len(numbers)}",
        f"[check] quotes   : {len(quotes)}",
        f"[check] entities : {len(entities)}  ·  timeline {len(timeline)}",
    ]
    if meta.get("aihot_story_id"):
        lines.append(
            f"[check] aihot    : story {meta['aihot_story_id']} · "
            f"{meta.get('source_count')} 信源 / {meta.get('report_count')} 报道 · "
            f"transport={meta.get('transport')}"
        )
    if meta.get("input"):
        lines.append(f"[check] input    : {meta['input']}（{meta.get('format')}，{meta.get('chars')} 字）")
    if meta.get("domain"):
        lines.append(f"[check] domain   : {meta['domain']} · {meta.get('paragraph_count')} 段 / {meta.get('chars')} 字")
    if card.get("license", {}).get("note"):
        lines.append(f"[check] license  : {card['license']['note']}")
    for warning in card.get("warnings") or []:
        lines.append(f"[check] warning  : {warning}")
    return "\n".join(lines)


def write_outputs(card: dict, args) -> None:
    json_text = json.dumps(card, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(card)
    wrote: list[str] = []
    if args.out:
        path = Path(args.out).expanduser()
        if path.suffix.lower() in (".md", ".markdown"):
            payload = md_text
        else:
            payload = json_text
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")
            wrote.append(str(path))
        except OSError as exc:
            raise PrepError(f"写入 --out 文件失败：{path}（{exc}）") from exc
    if args.out_dir:
        directory = Path(args.out_dir).expanduser()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "card.json").write_text(json_text, encoding="utf-8")
            (directory / "card.md").write_text(md_text, encoding="utf-8")
            wrote.extend([str(directory / "card.json"), str(directory / "card.md")])
        except OSError as exc:
            raise PrepError(f"写入 --out-dir 失败：{directory}（{exc}）") from exc
    for item in wrote:
        log(f"[已写入] {item}")


def run(args) -> int:
    if args.url:
        card = build_from_url(args)
    elif args.aihot_story:
        card = build_from_aihot_story(args)
    elif args.aihot_hot:
        card = build_from_aihot_hot(args)
    elif args.file:
        card = build_from_text(args)
    else:
        raise PrepError("没有输入源：请用 --aihot-story / --aihot-hot / --url / --file（或管道传入文本）。")

    write_outputs(card, args)

    if args.check:
        print(check_summary(card))
        return 0
    if args.json:
        sys.stdout.write(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(render_markdown(card))
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prep_input.py",
        description="AI 资讯输入层：把 AIHOT story / 任意新闻 URL / 粘贴文本归一成统一素材卡（JSON + Markdown）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python3 prep_input.py --aihot-story 589d286a-2a6d-48be-b14a-e61390534ec3 --check\n"
            "  python3 prep_input.py --aihot-hot --out material.json\n"
            "  python3 prep_input.py --url https://www.minimax.io/blog/minimax-m31f --out material.json\n"
            "  pbpaste | python3 prep_input.py --file - --check\n"
            "  python3 prep_input.py --file news.md --tier third-party --out material.json\n"
            "\n不联网也能跑：--file / stdin 走纯本地。事实优先来自厂商官方发布，聚合站只当导航。\n"
        ),
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--aihot-story", metavar="PUBLIC_ID",
                        help="AIHOT 事件 id（stories/<uuid> 的最后一段）")
    source.add_argument("--aihot-hot", action="store_true", help="AIHOT 当前热点榜（Top N）")
    source.add_argument("--url", metavar="URL", help="任意新闻页 URL（官方博客/媒体/HN 等）")
    source.add_argument("--file", metavar="PATH", help="纯文本/Markdown 文件；- 表示 stdin")

    parser.add_argument("--check", action="store_true", help="只打印 title 与 facts/numbers/quotes 等计数")
    parser.add_argument("--json", action="store_true", help="打印 JSON 素材卡（默认打印 Markdown）")
    parser.add_argument("--out", metavar="PATH", help="落盘到文件（.json → JSON；.md → Markdown）")
    parser.add_argument("--out-dir", metavar="DIR", help="落盘 DIR/card.json 与 DIR/card.md")
    parser.add_argument("--title", metavar="TEXT", help="覆盖标题（粘贴文本没有标题时很有用）")
    parser.add_argument("--source-name", metavar="NAME", help="覆盖来源名（如「IT之家」「某厂商官方博客」）")
    parser.add_argument("--published-at", metavar="TIME", help="覆盖发布时间（ISO 或中文日期）")
    parser.add_argument("--tier", choices=TIER_ORDER,
                        help="--file 输入的事实基础 tier（默认 unverified；你确知来源时才升档）")
    parser.add_argument("--limit", type=int, default=10, metavar="N",
                        help="--aihot-hot 取前 N 条（默认 10）")
    parser.add_argument("--timeout", type=float, default=20.0, metavar="SEC",
                        help="HTTP 超时秒数（默认 20）")
    parser.add_argument("--refresh", action="store_true", help="忽略 AIHOT 本地缓存新鲜度，强制刷新")
    parser.add_argument("--offline", action="store_true", help="不联网，只用本地缓存/样本（AIHOT 输入）")
    parser.add_argument("--cache-dir", metavar="DIR", help="AIHOT 缓存目录（默认 data/.cache）")
    parser.add_argument("--max-facts", type=int, default=80, metavar="N", help="facts 上限（默认 80）")
    parser.add_argument("--max-numbers", type=int, default=200, metavar="N", help="numbers 上限（默认 200）")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit 必须 ≥ 1")
    if args.max_facts < 1 or args.max_numbers < 1:
        parser.error("--max-facts / --max-numbers 必须 ≥ 1")
    if not any((args.aihot_story, args.aihot_hot, args.url, args.file)):
        if not sys.stdin.isatty():
            args.file = "-"
        else:
            parser.error(
                "没有输入源：请用 --aihot-story / --aihot-hot / --url / --file，"
                "或通过管道传入文本（pbpaste | prep_input.py --file -）。"
            )
    try:
        return run(args)
    except PrepError as exc:
        log(f"[错误] {exc}")
        return 1
    except KeyboardInterrupt:
        log("[中断] 用户取消")
        return 130
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
