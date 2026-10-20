#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aihot_fetch.py —— AIHOT（https://aihot.news）REST API v1 采集器。

把 AIHOT 的匿名只读 JSON / Markdown 接口封装成几个子命令，供「AI 资讯 → 内容二创」
流水线取数使用。只用 Python 标准库，无第三方依赖。

子命令
------
  hot            GET /api/v1/hot-topics（热点 Top 10，附摘要/最新进展）
  daily          GET /api/v1/dailies/latest 或 /api/v1/dailies/{date}
  items          GET /api/v1/items（分类 / 时间窗 / 分页 / 搜索）
  story <id>     GET /api/v1/stories/{publicId}（报道时间线 + AI 综述）
  agent-hot      GET /api/v1/agent/hot（Markdown 版当前热点）
  agent-latest   GET /api/v1/agent/latest（Markdown 版最新精选）

通用行为
--------
* 请求带 Accept-Encoding: gzip（等价 curl --compressed）与 Accept: application/json（agent 命令为 text/markdown）。
* User-Agent 末尾附 aihot-actor/<uuid>（匿名去重统计，不是鉴权；优先复用 skills/aihot/.aihot-actor-id）。
* ETag / If-None-Match 条件请求 + 本地缓存（data/.cache/）；304 直接复用缓存。
* 本地滑动窗口限流：60 秒内最多 55 次请求（服务端同 IP 约 60 次/分钟即返回 429）。
* 429 / 503 遵守 Retry-After；网络错误或 5xx 短暂退避后重试一次。

许可提醒
--------
AIHOT 服务与数据输出适用其公开使用规则：个人非商业、公益非商业和组织内部使用免费；
面向外部的商业产品、收费服务、客户交付、代理接口、数据转售、公开镜像、批量公开再分发，
或对外训练/微调/评测/检索增强生成，须事先取得 AIHOT 书面授权（wzglyay@virxact.com）。
见 https://aihot.news/terms 。脚本里保存的数据仅供获准用途使用。
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import textwrap
import time
import uuid
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, request
from urllib.parse import urljoin

try:  # Python 3.9+；macOS/Linux 自带 tzdata 时可用
    from zoneinfo import ZoneInfo

    SH_TZ = ZoneInfo("Asia/Shanghai")
except Exception:  # pragma: no cover - 兜底
    SH_TZ = timezone(timedelta(hours=8))

BASE_URL = os.environ.get("AIHOT_BASE_URL", "https://aihot.news").rstrip("/")
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_DIR = Path(os.environ.get("AIHOT_CACHE_DIR") or (ROOT / "data" / ".cache"))
SKILL_ACTOR_FILE = ROOT / "skills" / "aihot" / ".aihot-actor-id"
UA_BASE = "aihot-fetch/1.0 (+https://aihot.news/api/v1/agent)"
ACTOR_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REDIRECT_CODES = (301, 302, 303, 307, 308)
RATE_LIMIT = 55  # 每分钟最多 55 次（服务端阈值约 60 次/分钟）
RATE_WINDOW = 60.0


# --------------------------------------------------------------------------- #
# 小工具
# --------------------------------------------------------------------------- #
def log(msg: str) -> None:
    """提示信息走 stderr，保证 stdout 只有数据。"""
    print(msg, file=sys.stderr, flush=True)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def clip(text: str | None, limit: int) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def wrap(text: str | None, indent: str = "   ", width: int = 100) -> str:
    if not text:
        return ""
    return textwrap.fill(
        " ".join(str(text).split()),
        width=width,
        initial_indent=indent,
        subsequent_indent=indent,
        break_long_words=True,
        break_on_hyphens=False,
    )


def to_sh(iso: str | None) -> str:
    """把接口里的 UTC ISO 时间转成北京时间字符串。"""
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(SH_TZ).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(iso)


def now_sh() -> str:
    return datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S")


def rule(title: str, char: str = "─", width: int = 100) -> None:
    print(title)
    print(char * min(width, max(20, len(title) + 8)))


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]


def _parse_max_age(cache_control: str | None) -> int:
    if not cache_control:
        return 0
    m = re.search(r"max-age\s*=\s*(\d+)", cache_control)
    return int(m.group(1)) if m else 0


def _retry_after_seconds(value: str | None) -> int:
    if not value:
        return 30
    value = value.strip()
    if value.isdigit():
        return max(1, min(120, int(value)))
    try:  # HTTP-date 形式
        dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        return max(1, min(120, int(dt.timestamp() - time.time()) + 1))
    except Exception:
        return 30


def resolve_actor_id(cache_dir: Path, override: str | None) -> str:
    """解析 aihot-actor 假名 UUID：--actor > 环境变量 > 本地缓存 > 已装 Skill 的 ID。"""
    candidates: list[str | None] = [override, os.environ.get("AIHOT_ACTOR_ID")]
    cached = cache_dir / "actor-id"
    for p in (cached, SKILL_ACTOR_FILE):
        try:
            candidates.append(p.read_text(encoding="utf-8").strip())
        except OSError:
            candidates.append(None)
    for cand in candidates:
        if cand and ACTOR_RE.match(cand):
            if not cached.exists():
                atomic_write(cached, (cand.strip() + "\n").encode("utf-8"))
                try:
                    os.chmod(cached, 0o600)
                except OSError:
                    pass
            return cand.strip().lower()
    new_id = str(uuid.uuid4())
    atomic_write(cached, (new_id + "\n").encode("utf-8"))
    try:
        os.chmod(cached, 0o600)
    except OSError:
        pass
    return new_id


# --------------------------------------------------------------------------- #
# 限流 + HTTP 客户端（缓存 / ETag / 重试）
# --------------------------------------------------------------------------- #
class RateLimiter:
    """跨进程的滑动窗口限流：60 秒内最多 RATE_LIMIT 次请求。"""

    def __init__(self, cache_dir: Path, limit: int = RATE_LIMIT, window: float = RATE_WINDOW):
        self.path = cache_dir / "ratelimit.json"
        self.limit = limit
        self.window = window

    def _load(self) -> list[float]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [float(x) for x in raw if isinstance(x, (int, float))]
        except (OSError, ValueError):
            return []

    def acquire(self) -> None:
        now = time.time()
        stamps = [t for t in self._load() if now - t < self.window]
        if len(stamps) >= self.limit:
            wait = stamps[0] + self.window - now + 0.1
            if wait > 0:
                log(f"[限流] 本地 60 秒窗口已用 {len(stamps)} 次，等待 {wait:.1f}s（服务端约 60 次/分钟）")
                time.sleep(wait)
                now = time.time()
                stamps = [t for t in stamps if now - t < self.window]
        stamps.append(now)
        try:
            atomic_write(self.path, json.dumps(stamps).encode("utf-8"))
        except OSError:
            pass


class ApiError(RuntimeError):
    pass


class Response:
    __slots__ = ("url", "text", "content_type", "status", "from_cache")

    def __init__(self, url: str, text: str, content_type: str, status: int, from_cache: bool):
        self.url = url
        self.text = text
        self.content_type = content_type
        self.status = status
        self.from_cache = from_cache

    def json(self):
        return json.loads(self.text)


class AihotClient:
    def __init__(
        self,
        cache_dir: Path,
        timeout: float = 20.0,
        actor: str | None = None,
        refresh: bool = False,
        no_cache: bool = False,
    ):
        self.cache_dir = cache_dir
        self.http_cache = cache_dir / "http"
        self.timeout = timeout
        self.refresh = refresh
        self.no_cache = no_cache
        self.actor = resolve_actor_id(cache_dir, actor)
        self.ua = f"{UA_BASE} aihot-actor/{self.actor}"
        self.limiter = RateLimiter(cache_dir)
        self.opener = request.build_opener()

    # -- 本地缓存 ---------------------------------------------------------- #
    def _cache_path(self, url: str) -> Path:
        return self.http_cache / f"{_cache_key(url)}.json"

    def _read_cache(self, url: str) -> dict | None:
        if self.no_cache:
            return None
        try:
            data = json.loads(self._cache_path(url).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if data.get("url") != url or not isinstance(data.get("body"), str):
            return None
        return data

    def _store_cache(self, url: str, text: str, headers, status: int = 200) -> None:
        if self.no_cache:
            return
        payload = {
            "url": url,
            "status": status,
            "etag": headers.get("ETag"),
            "content_type": headers.get("Content-Type", ""),
            "cache_control": headers.get("Cache-Control", ""),
            "max_age": _parse_max_age(headers.get("Cache-Control")),
            "fetched_at": time.time(),
            "body": text,
        }
        try:
            atomic_write(self._cache_path(url), json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        except OSError:
            pass

    def _touch_cache(self, cache: dict) -> None:
        cache["fetched_at"] = time.time()
        try:
            atomic_write(
                self._cache_path(cache["url"]), json.dumps(cache, ensure_ascii=False).encode("utf-8")
            )
        except OSError:
            pass

    # -- 单次请求 ---------------------------------------------------------- #
    @staticmethod
    def _decode(raw: bytes, headers) -> str:
        enc = (headers.get("Content-Encoding") or "").lower()
        if "gzip" in enc:
            raw = gzip.decompress(raw)
        elif "deflate" in enc:
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        charset = "utf-8"
        ctype = headers.get("Content-Type", "") or ""
        m = re.search(r"charset=([\w-]+)", ctype)
        if m:
            charset = m.group(1)
        return raw.decode(charset, "replace")

    def _problem_message(self, e: error.HTTPError) -> str:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        detail = body
        try:
            obj = json.loads(body)
            detail = obj.get("detail") or obj.get("title") or body
        except ValueError:
            pass
        return f"HTTP {e.code}: {clip(detail, 300) or e.reason}"

    def get(self, path_or_url: str, accept: str = "application/json") -> Response:
        url = path_or_url if path_or_url.startswith("http") else BASE_URL + path_or_url
        cache = self._read_cache(url)
        if cache and not self.refresh:
            age = time.time() - float(cache.get("fetched_at") or 0)
            if age < float(cache.get("max_age") or 0):
                return Response(url, cache["body"], cache.get("content_type", ""), 200, True)

        last_error: str | None = None
        request_url = url
        for hop in range(6):
            for attempt in range(4):
                self.limiter.acquire()
                headers = {
                    "Accept": accept,
                    "Accept-Encoding": "gzip",
                    "User-Agent": self.ua,
                }
                if cache and cache.get("etag"):
                    headers["If-None-Match"] = cache["etag"]
                req = request.Request(request_url, headers=headers, method="GET")
                try:
                    with self.opener.open(req, timeout=self.timeout) as resp:
                        text = self._decode(resp.read(), resp.headers)
                        self._store_cache(url, text, resp.headers, resp.status)
                        return Response(url, text, resp.headers.get("Content-Type", ""), resp.status, False)
                except error.HTTPError as e:
                    if e.code == 304 and cache:
                        self._touch_cache(cache)
                        return Response(url, cache["body"], cache.get("content_type", ""), 304, True)
                    if e.code in REDIRECT_CODES:
                        location = e.headers.get("Location")
                        e.close()
                        if not location:
                            raise ApiError(f"HTTP {e.code} 重定向缺少 Location: {url}")
                        request_url = urljoin(request_url, location)
                        break  # 跳出 attempt，进入下一跳
                    if e.code in (429, 503) or e.code >= 500:
                        wait = _retry_after_seconds(e.headers.get("Retry-After")) if e.code in (429, 503) else 5
                        last_error = self._problem_message(e)
                        e.close()
                        if attempt < 3:
                            log(f"[重试] {last_error}；按 Retry-After 等待 {wait}s 后重试（{attempt + 1}/3）")
                            time.sleep(wait)
                            continue
                        raise ApiError(f"AIHOT 暂时不可用（已重试）：{last_error}")
                    last_error = self._problem_message(e)
                    e.close()
                    raise ApiError(last_error)
                except (error.URLError, TimeoutError, OSError) as e:
                    last_error = f"网络错误：{e}"
                    if attempt < 1:
                        log(f"[重试] {last_error}；3s 后重试一次")
                        time.sleep(3)
                        continue
                    raise ApiError(last_error)
            else:
                continue
            continue  # 重定向后继续外层循环
        raise ApiError(f"重定向次数过多：{url}（最后一次错误：{last_error or '未知'}）")


# --------------------------------------------------------------------------- #
# 输出辅助
# --------------------------------------------------------------------------- #
def emit_payload(resp: Response, args) -> None:
    """--json / --save：原样输出/落盘接口返回。"""
    if getattr(args, "save", None):
        path = Path(args.save).expanduser()
        atomic_write(path, resp.text.encode("utf-8"))
        log(f"[已保存] {path}  ({len(resp.text.encode('utf-8'))} bytes, 缓存={resp.from_cache})")
    if getattr(args, "json", False):
        sys.stdout.write(resp.text)
        if not resp.text.endswith("\n"):
            sys.stdout.write("\n")


def note_notice(data: dict) -> None:
    notice = data.get("notice")
    if isinstance(notice, dict) and notice.get("message"):
        log(f"[AIHOT 公告] {notice['message']}")


def source_line(resp: Response) -> str:
    return "（本地缓存命中）" if resp.from_cache else "（网络实时）"


# --------------------------------------------------------------------------- #
# 子命令实现
# --------------------------------------------------------------------------- #
def _story_public_id(links: dict) -> str | None:
    url = (links or {}).get("story")
    if not url:
        return None
    return url.rstrip("/").split("/")[-1] or None


def _hot_enrich(client: AihotClient, items: list[dict]) -> dict[str, dict]:
    """为热点补摘要：热点接口本身没有摘要/好评字段，用 story 的 AI 综述补。"""
    enriched: dict[str, dict] = {}
    for item in items:
        pid = _story_public_id(item.get("links") or {})
        if not pid:
            continue
        try:
            resp = client.get(f"/api/v1/stories/{pid}", accept="application/json")
            data = resp.json()
            note_notice(data)
            story = data.get("story") or {}
            digest = (story.get("digest") or "").strip()
            summary = clip(digest.split("\n\n")[0], 120) if digest else ""
            enriched[item["id"]] = {
                "publicId": pid,
                "summary": summary,
                "latest": clip(story.get("latest"), 120),
                "reportCount": story.get("reportCount"),
            }
        except ApiError as e:
            log(f"[提示] 热点 #{item.get('rank')} 的 story 暂不可用：{e}")
    return enriched


def cmd_hot(client: AihotClient, args) -> None:
    resp = client.get("/api/v1/hot-topics", accept="application/json")
    data = resp.json()
    note_notice(data)
    items = (data.get("items") or [])[: args.limit]

    if args.json:
        emit_payload(resp, args)
        return
    if args.save:
        emit_payload(resp, args)

    enriched = {} if args.no_summary else _hot_enrich(client, items)
    rule(f"AIHOT 当前热点 Top {len(items)} · 抓取 {now_sh()} 北京时间 · 来源 /api/v1/hot-topics {source_line(resp)}")
    for it in items:
        extra = enriched.get(it["id"], {})
        print()
        print(f"#{it.get('rank')}  {it.get('title')}")
        heat = f"热度 信号{it.get('signalCount', 0)} · 信源{it.get('sourceCount', 0)}"
        if it.get("participantCount") is not None:
            heat += f" · 参与方{it['participantCount']}"
        heat += f" · 最新 {to_sh(it.get('latestAt'))}"
        print(f"   {heat}")
        if extra.get("summary"):
            print(wrap(f"摘要 {extra['summary']}"))
        elif extra.get("latest"):
            print(wrap(f"摘要 {extra['latest']}"))
        elif args.no_summary:
            print("   摘要 （--no-summary 已跳过；加 --json 可看完整字段）")
        else:
            print("   摘要 （该热点暂无 story 综述）")
        print(f"   id {it.get('id')}    story {extra.get('publicId') or '—'}")
        if it.get("sourceNames"):
            print(wrap("信源 " + "、".join(it["sourceNames"]), indent="   "))


def cmd_daily(client: AihotClient, args) -> None:
    if args.date:
        if not DATE_RE.match(args.date):
            raise SystemExit("--date 需要 YYYY-MM-DD 格式，例如 2026-10-20")
        path = f"/api/v1/dailies/{args.date}"
    else:
        path = "/api/v1/dailies/latest"
    resp = client.get(path, accept="application/json")
    data = resp.json()
    note_notice(data)
    if args.json:
        emit_payload(resp, args)
        return
    if args.save:
        emit_payload(resp, args)

    report = data.get("report") or {}
    rule(f"AIHOT 日报 {report.get('date', '?')} · 抓取 {now_sh()} 北京时间 · {path} {source_line(resp)}")
    print(f"   生成时间 {to_sh(report.get('generatedAt'))} · 窗口 {to_sh(report.get('windowStart'))} → {to_sh(report.get('windowEnd'))}")
    lead = report.get("lead") or {}
    if lead.get("title"):
        print()
        print(f"【头条】{lead['title']}")
        print(wrap(lead.get("leadParagraph")))
    for sec in report.get("sections") or []:
        print()
        print(f"【{sec.get('label')}】{len(sec.get('items') or [])} 条")
        for n, item in enumerate(sec.get("items") or [], 1):
            print(f"  {n}. {item.get('title')}")
            print(wrap(item.get("summary"), indent="     "))
            src = (item.get("source") or {}).get("name") or "—"
            print(f"     来源 {src}")
            if (item.get("links") or {}).get("original"):
                print(f"     原文 {item['links']['original']}")
    flashes = report.get("flashes") or []
    if flashes:
        print()
        print(f"【快讯】{len(flashes)} 条")
        for item in flashes:
            src = (item.get("source") or {}).get("name") or "—"
            print(f"  · {to_sh(item.get('publishedAt'))}  {item.get('title')}  —  {src}")


def cmd_items(client: AihotClient, args) -> None:
    from urllib.parse import urlencode

    params: dict[str, str] = {"limit": str(args.limit), "mode": args.mode, "window": args.window, "by": args.by}
    if args.category:
        params["category"] = args.category
    if args.q:
        params["q"] = args.q
    if args.cursor:
        params["cursor"] = args.cursor
    path = "/api/v1/items?" + urlencode(params)
    resp = client.get(path, accept="application/json")
    data = resp.json()
    note_notice(data)
    if args.json:
        emit_payload(resp, args)
        return
    if args.save:
        emit_payload(resp, args)

    items = data.get("items") or []
    page = data.get("page") or {}
    q = data.get("query") or {}
    rule(
        f"AIHOT 条目 · mode={q.get('mode')} window={q.get('window')} category={q.get('category') or '全部'} "
        f"· 本页 {len(items)} 条 · 抓取 {now_sh()} {source_line(resp)}"
    )
    for n, it in enumerate(items, 1):
        flags = []
        if it.get("selected"):
            flags.append("精选")
        if it.get("score") is not None:
            flags.append(f"score={it['score']}")
        flag_s = (" · " + " · ".join(flags)) if flags else ""
        print()
        print(f"{n}. {it.get('title')}")
        print(
            f"   [{it.get('category') or '未分类'}]{flag_s} · 发布 {to_sh(it.get('publishedAt'))}"
            f" · 来源 {(it.get('source') or {}).get('name', '—')}"
        )
        if it.get("summary"):
            print(wrap(f"摘要 {it['summary']}"))
        if it.get("reason"):
            print(wrap(f"推荐理由 {it['reason']}"))
        print(f"   id {it.get('id')}  ·  {(it.get('links') or {}).get('aihot', '')}")
    more = "有下一页（--cursor 复用 page.nextCursor）" if page.get("hasMore") else "已到末页"
    print()
    print(f"本页 {page.get('count', len(items))} 条 · {more} · nextCursor={page.get('nextCursor') or '—'}")


def _normalize_public_id(raw: str) -> str:
    raw = raw.strip()
    if "/" in raw:
        raw = raw.rstrip("/").split("/")[-1]
    return raw


def cmd_story(client: AihotClient, args) -> None:
    pid = _normalize_public_id(args.public_id)
    resp = client.get(f"/api/v1/stories/{pid}", accept="application/json")
    data = resp.json()
    note_notice(data)
    if args.json:
        emit_payload(resp, args)
        return
    if args.save:
        emit_payload(resp, args)

    story = data.get("story") or {}
    rule(f"AIHOT 故事 {story.get('publicId', pid)} · 抓取 {now_sh()} 北京时间 {source_line(resp)}")
    print(f"   状态 {story.get('status')} · 信源 {story.get('sourceCount')} · 报道 {story.get('reportCount')}")
    print(f"   时间 {to_sh(story.get('firstReportAt'))} → {to_sh(story.get('latestAt'))}")
    print()
    print(f"【标题】{story.get('title')}")
    if story.get("latest"):
        print(wrap(f"【最新进展】{story['latest']}"))
    digest = (story.get("digest") or "").strip()
    if digest:
        print()
        print(f"【AI 综述】更新于 {to_sh(story.get('digestUpdatedAt'))}")
        for para in digest.split("\n\n"):
            print(wrap(para))
    reports = story.get("reports") or []
    if reports:
        print()
        print(f"【报道时间线】{len(reports)} 条（新 → 旧）")
        for n, rep in enumerate(reports, 1):
            src = (rep.get("source") or {}).get("name") or "—"
            print(f"  {n}. {to_sh(rep.get('publishedAt'))} · {src}")
            print(f"     {rep.get('title')}")
            if rep.get("summary"):
                print(wrap(rep["summary"], indent="       "))
            links = rep.get("links") or {}
            if links.get("original"):
                print(f"       原文 {links['original']}")
    for label, key in (("同一脉络", "storyline"), ("相关故事", "related")):
        refs = story.get(key) or []
        if refs:
            print()
            print(f"【{label}】{len(refs)} 条")
            for ref in refs:
                rid = ref.get("publicId") or ref.get("id")
                print(f"  · {ref.get('title')}  (publicId {rid})")
    print()
    print(f"阅读页 {(story.get('links') or {}).get('aihot', '—')}")


def cmd_agent_hot(client: AihotClient, args) -> None:
    resp = client.get(f"/api/v1/agent/hot?limit={args.limit}", accept="text/markdown; charset=utf-8")
    emit_payload(resp, args)
    if not args.json:
        sys.stdout.write(resp.text if resp.text.endswith("\n") else resp.text + "\n")


def cmd_agent_latest(client: AihotClient, args) -> None:
    from urllib.parse import urlencode

    params = {"window": args.window, "mode": args.mode, "limit": str(args.limit)}
    if args.category:
        params["category"] = args.category
    resp = client.get("/api/v1/agent/latest?" + urlencode(params), accept="text/markdown; charset=utf-8")
    emit_payload(resp, args)
    if not args.json:
        sys.stdout.write(resp.text if resp.text.endswith("\n") else resp.text + "\n")


# --------------------------------------------------------------------------- #
# 命令行
# --------------------------------------------------------------------------- #
def add_common(p: argparse.ArgumentParser, suppress_defaults: bool = False) -> None:
    """把通用选项同时挂到主命令和子命令上；子命令用 SUPPRESS 默认值避免覆盖前面的值。"""
    def dflt(value):
        return argparse.SUPPRESS if suppress_defaults else value

    p.add_argument("--json", action="store_true", default=dflt(False),
                   help="打印接口原始返回（JSON 命令为原始 JSON，agent 命令为原始 Markdown）")
    p.add_argument("--save", metavar="PATH", default=dflt(None),
                   help="把接口原始返回原样写入文件（自动创建父目录）")
    p.add_argument("--refresh", action="store_true", default=dflt(False),
                   help="忽略本地缓存的新鲜度，重新请求（仍带 If-None-Match 条件请求）")
    p.add_argument("--no-cache", action="store_true", default=dflt(False),
                   help="不读也不写本地缓存，强制完整网络请求")
    p.add_argument("--cache-dir", metavar="DIR", default=dflt(None),
                   help="缓存目录（默认 data/.cache，也可用 AIHOT_CACHE_DIR 环境变量）")
    p.add_argument("--timeout", type=float, default=dflt(20.0), help="单次请求超时秒数（默认 20）")
    p.add_argument("--actor", metavar="UUID", default=dflt(None),
                   help="aihot-actor 假名 UUID（默认复用 skills/aihot/.aihot-actor-id 或本地生成）")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aihot_fetch.py",
        description="AIHOT REST API v1 采集器：hot / daily / items / story / agent-hot / agent-latest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python3 tools/aihot_fetch.py hot\n"
            "  python3 tools/aihot_fetch.py --save data/raw/2026-10-20/hot-topics.json hot\n"
            "  python3 tools/aihot_fetch.py daily --date 2026-10-20\n"
            "  python3 tools/aihot_fetch.py items --limit 50 --category ai-models --mode all\n"
            "  python3 tools/aihot_fetch.py story 589d286a-2a6d-48be-b14a-e61390534ec3\n"
            "  python3 tools/aihot_fetch.py agent-latest --window 24h --limit 10\n"
            "\n许可：个人非商业/公益/组织内部免费；对外商业、客户交付、数据转售、公开镜像等"
            "须先取得 AIHOT 书面授权（wzglyay@virxact.com，https://aihot.news/terms）。"
        ),
    )
    add_common(parser)
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    p_hot = sub.add_parser("hot", help="当前多源热点 Top 10（附摘要/最新进展）")
    add_common(p_hot, suppress_defaults=True)
    p_hot.add_argument("--limit", type=int, default=10, choices=range(1, 11), metavar="1-10")
    p_hot.add_argument("--no-summary", action="store_true", help="跳过 story 请求，不补摘要（只打 1 次接口）")
    p_hot.set_defaults(func=cmd_hot)

    p_daily = sub.add_parser("daily", help="最新或指定日期的 AIHOT 日报")
    add_common(p_daily, suppress_defaults=True)
    p_daily.add_argument("--date", metavar="YYYY-MM-DD", help="上海时区日历日期；缺省取最新一期")
    p_daily.set_defaults(func=cmd_daily)

    p_items = sub.add_parser("items", help="最近 7 天的公开/精选条目（分类、时间窗、搜索、分页）")
    add_common(p_items, suppress_defaults=True)
    p_items.add_argument("--limit", type=int, default=20, help="本页条数 1-100（服务端默认 50）")
    p_items.add_argument("--category", metavar="CAT",
                         help="ai-models / ai-products / industry / paper / tip / opinion（新值需容忍）")
    p_items.add_argument("--mode", choices=("selected", "all"), default="selected", help="selected=编辑精选；all=全部公开动态")
    p_items.add_argument("--window", choices=("24h", "7d"), default="7d", help="时间窗（仅支持 24h/7d）")
    p_items.add_argument("--by", choices=("timeline", "published"), default="timeline", help="时间窗依据的轴")
    p_items.add_argument("--q", metavar="KEYWORD", help="关键词搜索（2-200 字符，最近 7 天）")
    p_items.add_argument("--cursor", metavar="CURSOR", help="上一页 page.nextCursor（只能配合同一 query 使用）")
    p_items.set_defaults(func=cmd_items)

    p_story = sub.add_parser("story", help="事件全貌：报道时间线 + AI 综述（publicId 或 story URL）")
    add_common(p_story, suppress_defaults=True)
    p_story.add_argument("public_id", metavar="publicId", help="stories/{publicId} 的 id，或热点 links.story 的链接")
    p_story.set_defaults(func=cmd_story)

    p_ah = sub.add_parser("agent-hot", help="Markdown 版当前热点（给 Agent/LLM 直接读）")
    add_common(p_ah, suppress_defaults=True)
    p_ah.add_argument("--limit", type=int, default=10, choices=range(1, 11), metavar="1-10")
    p_ah.set_defaults(func=cmd_agent_hot)

    p_al = sub.add_parser("agent-latest", help="Markdown 版最新精选/动态（给 Agent/LLM 直接读）")
    add_common(p_al, suppress_defaults=True)
    p_al.add_argument("--limit", type=int, default=10, choices=range(1, 31), metavar="1-30")
    p_al.add_argument("--window", choices=("24h", "7d"), default="24h")
    p_al.add_argument("--mode", choices=("selected", "all"), default="selected")
    p_al.add_argument("--category", metavar="CAT",
                      help="ai-models / ai-products / industry / paper / tip / opinion")
    p_al.set_defaults(func=cmd_agent_latest)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cache_dir = Path(args.cache_dir).expanduser() if args.cache_dir else DEFAULT_CACHE_DIR
    client = AihotClient(
        cache_dir=cache_dir,
        timeout=args.timeout,
        actor=args.actor,
        refresh=args.refresh,
        no_cache=args.no_cache,
    )
    try:
        args.func(client, args)
    except ApiError as e:
        log(f"[错误] {e}")
        return 1
    except KeyboardInterrupt:
        log("[中断] 用户取消")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
