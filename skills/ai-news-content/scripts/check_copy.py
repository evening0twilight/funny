#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_copy.py —— 发布前机器校验（AI 新闻内容工坊的"最后一公里"）

为什么需要它：
    小红书/抖音/合规的约束都是「硬约束」，但写稿模型会漏。
    这个脚本把能机器判的部分全判掉，剩下的才交给人看。

用法：
    python3 check_copy.py out/xxx/01-小红书图文.md
    python3 check_copy.py out/xxx/01-小红书图文.md --material material.json
    python3 check_copy.py out/xxx/02-抖音口播分镜.md --mode douyin
    python3 check_copy.py out/xxx/ --all            # 目录下所有 .md

退出码：0 = 全过（WARN 不算失败）；1 = 有 FAIL。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------- 常量
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U0001F000-\U0001F0FF\u2600-\u27BF\u2B00-\u2BFF]"
)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

AI_SMELL = [
    "作为 AI", "作为AI", "总之", "综上所述", "值得注意的是", "在当今时代",
    "赋能", "闭环", "深度赋能", "让我们", "不仅仅是", "毋庸置疑", "众所周知",
    "在这个信息爆炸", "值得一提", "首先，其次，最后",
]
# 广告法高风险绝对化用语（做号被投诉的重灾区）
# 硬违规：带了就是承诺/极限宣传，直接 FAIL
ABSOLUTE_HARD = ["全网最低", "100%", "零风险", "绝对安全", "永久有效", "史上最", "绝无仅有", "国家级", "世界级"]
# 软风险：新闻里「排名第一」「最强模型」常是引用事实，需要人工确认有没有出处 → WARN
ABSOLUTE_SOFT = ["最强", "最好", "最快", "第一", "唯一", "顶级", "极致", "永久"]
# 站外导流 / 诱导互动
DIVERT = [
    "扣 1", "扣1", "领入口", "私信我", "私信领取", "加微", "微信", "二维码",
    "主页链接", "评论区领取", "评论区扣", "关注后领取", "扫码", "站外",
]
# 承诺式 / 编造体感
FAKE_EXP = ["我用了", "我实测", "我亲测", "用了三个月", "亲测有效", "我试过很久"]


# --------------------------------------------------------------------- 工具
def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def section(text: str, name: str) -> str:
    """抓 【xxx】 或 ## 【xxx】 到下一个同级标题之间的内容。"""
    pat = re.compile(rf"^#{{0,3}}\s*【{re.escape(name)}】\s*$", re.M)
    m = pat.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    # 边界只认「## 及以上」标题或下一个【】段。
    # 早期用 ^#{1,3}\s，结果正文里塞一行 "# xxx" 就把整段截空，
    # 后面的检查全部 pass——违规反而报告更干净，这是最坏的失败模式。
    nxt = re.search(r"^##+\s*\S|\n【", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def visible_chars(s: str) -> int:
    return len(re.sub(r"\s", "", s))


def cjk_count(s: str) -> int:
    return len(CJK_RE.findall(s))


def strip_md(s: str) -> str:
    """去掉引号/代码块标记，留下正文。"""
    s = re.sub(r"^>\s?", "", s, flags=re.M)
    s = re.sub(r"^```.*?$", "", s, flags=re.M)
    return s


class Result:
    def __init__(self):
        self.rows: list[tuple[str, str, str]] = []

    def add(self, item: str, ok: bool | None, detail: str = "") -> None:
        status = "PASS" if ok is True else ("FAIL" if ok is False else "WARN")
        self.rows.append((status, item, detail))

    @property
    def failed(self) -> int:
        return sum(1 for r in self.rows if r[0] == "FAIL")

    def render(self, title: str) -> None:
        print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
        for status, item, detail in self.rows:
            mark = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ "}[status]
            print(f"{mark} {item:<28} {detail}")


# --------------------------------------------------------------------- 检查项

def publish_scope(text: str) -> str:
    """只保留"要发出去"的内容：去掉自检/核对/风险章节，以及否定式的表格行。

    不做这层剥离，自检表里的「无扣 1 / 无导流」会被自己的检查器判成违规——
    这是典型的"检查器误报"，实测踩过。
    """
    lines = text.splitlines()
    out: list[str] = []
    skip, level = False, 0
    for ln in lines:
        m = re.match(r"^(#{1,6})\s*(.*)", ln)
        if m:
            title = m.group(2)
            if re.search(r"自检|核对|发布前|风险|失败模式|checklist", title, re.I):
                skip, level = True, len(m.group(1))
                continue
            if skip and len(m.group(1)) <= level:
                skip = False
        if skip:
            continue
        # 表格里描述"我们没有做某事"的行，不算违规
        if re.match(r"^\s*(?:[-*>|]|\d+[.、])?\s*(?:不放|不做|不用|不要|禁止|已删|不写|不含|无[ 「]|未|❌|✅)", ln):
            continue
        if ln.lstrip().startswith("|") and re.search(r"无[ 「]|禁止|已删|不写|不含|✅|❌", ln):
            continue
        out.append(ln)
    return "\n".join(out)


def check_xhs(text: str, res: Result) -> None:
    head = section(text, "标题")
    body = strip_md(section(text, "正文"))
    tags_raw = section(text, "标签")

    # --- 标题 ---
    cands = re.findall(r"^\s*(?:\d+[.、]|[-*])\s*(.+?)\s*$", head, re.M)
    # 去掉「（16 字，悬念冲突）」这类人工标注，否则会把字数算进标题
    cands = [re.sub(r"[（(]\s*\d+\s*字[^）)]*[）)]", "", c).strip() for c in cands]
    cands = [c for c in cands if c and not c.startswith("主标题") and len(c) > 2]
    if not cands:
        res.add("标题 ≤20 字", None, "没找到标题候选")
    else:
        bad = [(c, len(c)) for c in cands if len(c) > 20]
        res.add("标题 ≤20 字", not bad,
                f"{len(cands)} 个候选，长度 {[len(c) for c in cands]}"
                + (f"；超长 {bad}" if bad else ""))

    # --- 正文长度 ---
    if not body.strip():
        res.add("正文 300–800 字", None, "没找到【正文】段落")
    else:
        n_cjk, n_vis = cjk_count(body), visible_chars(body)
        ok = 300 <= n_cjk <= 800
        res.add("正文 300–800 字", ok, f"汉字 {n_cjk} / 可见字符 {n_vis}")

    # --- 排版 ---
    res.add("无 Markdown 加粗 **", "**" not in body,
            f"出现 {body.count('**')} 次" if "**" in body else "")
    emoji_n = len(EMOJI_RE.findall(body))
    res.add("emoji ≤8", emoji_n <= 8, f"{emoji_n} 个")
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    over = [p for p in paras if len(EMOJI_RE.findall(p)) > 1]
    res.add("每段 emoji ≤1", not over, f"{len(over)} 段超标" if over else "")

    # --- 标签 ---
    tags = re.findall(r"#[^\s#，,。；;]+", tags_raw)
    if not tags:
        tags = re.findall(r"#[^\s#，,。；;]+", text[-300:])
    res.add("标签 5–8 个", 5 <= len(tags) <= 8, f"{len(tags)} 个")

    # 标题和封面文案才是最容易被抓的地方，必须一起扫（下面这 5 项覆盖标题+正文）
    check_common(head + "\n" + body, res)

    # 标题备选数量
    res.add("标题备选 3 个", len(cands) >= 3, f"{len(cands)} 个")

    # CTA 只能有一个
    cta = [w for w in ("收藏", "关注", "评论区", "点赞", "转发", "私信") if w in body]
    res.add("CTA 单一", len(cta) <= 2, "、".join(cta) if cta else "没找到互动引导")


def check_douyin(text: str, res: Result) -> None:
    """抖音：口播字数 × 语速 = 时长，且每句 ≤15 字。"""
    scope = publish_scope(text)

    # --- 抓口播全文：取最长的 ``` 代码块 ---
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", scope, re.S)
    spoken = ""
    if blocks:
        spoken = max(blocks, key=lambda b: len(CJK_RE.findall(b)))
    if not spoken.strip():
        m = re.search(r"口播全文[^\n]*\n+(.*?)(?=\n##|\n\*\*|$)", scope, re.S)
        spoken = m.group(1) if m else ""
    spoken = strip_md(spoken).strip()
    # 【S1 / 0–5s】这类是舞台标记，不是要念的字
    spoken_clean = re.sub(r"【[^】]*】", "", spoken).strip()

    if not spoken_clean:
        res.add("口播全文", None, "没找到口播段落")
    else:
        n_cjk, n_vis = cjk_count(spoken_clean), visible_chars(spoken_clean)
        res.add("口播字数", True, f"汉字 {n_cjk} / 含数字字母 {n_vis}")

        sents = [x for x in re.split(r"[。！？!?\n]+", spoken_clean) if x.strip()]
        longest = max((cjk_count(x) for x in sents), default=0)
        longs = [(x.strip(), cjk_count(x)) for x in sents if cjk_count(x) > 15]
        res.add("每句 ≤15 字", not longs,
                f"{len(sents)} 句，最长 {longest} 字" + (f"；超长 {longs[:3]}" if longs else ""))

        # 声明的字数与时长（取「口播正文：N 字」与箭头后的秒数）
        mc = re.search(r"(?:口播正文|口播全文|全文)[：:]\s*(\d+)\s*字", scope)
        ms = re.search(r"→\s*(\d+(?:\.\d+)?)\s*秒", scope) or re.search(
            r"(\d+(?:\.\d+)?)\s*秒\s*(?:←|＝|=)", scope)
        if mc and ms:
            declared_n, declared_s = int(mc.group(1)), float(ms.group(1))
            rate = declared_n / (declared_s / 60) if declared_s else 0
            ok = 235 <= rate <= 285
            res.add("语速 240–280 字/分", ok,
                    f"声明 {declared_n} 字 / {declared_s} 秒 = {rate:.0f} 字/分")
            drift = abs(n_vis - declared_n) / max(declared_n, 1)
            res.add("声明字数 vs 实际", drift <= 0.2,
                    f"声明 {declared_n}，实际含标点 {n_vis}（偏差 {drift:.0%}）")
        else:
            res.add("语速 240–280 字/分", None, "没找到「N 字 / X 秒」的声明")

    rows = len(re.findall(r"^\|\s*\d", scope, re.M))
    res.add("分镜表", rows >= 4, f"{rows} 行" if rows else "没找到分镜表行")

    hook = re.search(r"黄金\s*3\s*秒.*?\n+(?:>\s*)?(.+)", scope)
    res.add("黄金 3 秒钩子", hook is not None,
            (hook.group(1)[:30] if hook else "没找到钩子段"))

    check_common(publish_scope(scope), res)


def check_common(scope: str, res: Result) -> None:
    """所有平台共用的合规/文风检查。作用域应是"要发出去的文字"。"""
    # 解说/播报/字幕语境里的「让我们…」是正常修辞，不算 AI 腔（实测误伤过一条赛事解说梗）
    hits: list[str] = []
    for w in AI_SMELL:
        for m in re.finditer(re.escape(w), scope):
            line = scope[scope.rfind("\n", 0, m.start()) + 1: scope.find("\n", m.end())]
            if re.search(r"解说|播报|镜头|字幕|台词|主持", line):
                continue
            hits.append(w)
            break
    res.add("AI 腔黑名单", not hits, "、".join(hits) if hits else "")

    hard = [w for w in ABSOLUTE_HARD if w in scope]
    res.add("绝对化用语(硬)", not hard, "、".join(hard) if hard else "")

    soft = [w for w in ABSOLUTE_SOFT if w in scope]
    res.add("绝对化用语(软)", None if soft else True,
            f"出现 {('、'.join(soft))}，确认有出处/归属再发" if soft else "")

    div_hits = [w for w in DIVERT if w in scope]
    res.add("站外导流", not div_hits, "、".join(div_hits) if div_hits else "")

    fake = [w for w in FAKE_EXP if w in scope]
    res.add("编造体感", not fake, "、".join(fake) if fake else "")


def check_ai_label(text: str, res: Result) -> None:
    """AI 生成标识（有图/视频产物时必须出现）。"""
    has_visual = bool(re.search(r"生图|视频提示词|首帧|分镜|画面", text))
    labeled = bool(re.search(r"AI 生成|AI生成|人工智能生成", text))
    if has_visual:
        res.add("AI 生成标识", labeled, "未发现声明" if not labeled else "")


# 技术参数噪声：提示词里这些数字不是"事实"，不该判失败
# 只抹"自指性"数字：必须带「全文/口播/约/共/时长」这类限定词才抹。
# 早期版本直接抹掉所有「N 秒」，结果正文里「响应 88 秒」这种假数字被抓漏了。
_SELF_METRIC = [
    re.compile(r"(?:全文|口播|时长|预计|约|共|大约|总计|片长|字数)\s*\d+(?:\.\d+)?\s*(?:字|秒|分钟)"),
    re.compile(r"\d+(?:\.\d+)?\s*字/分"),          # 语速
    re.compile(r"\d+(?:\.\d+)?\s*秒\s*[）)]"),     # 括号里的时长备注
]
_TECH_TOKEN = [
    re.compile(r"#[0-9A-Fa-f]{3,8}\b"),        # 色值 #0B1220
    re.compile(r"\b\d+\s*[Kk]\b"),             # 色温 5600K
    re.compile(r"\b\d+\s*(?:mm|px|pt|fps|Hz|bit)\b", re.I),
    re.compile(r"\b\d+\s*[:：]\s*\d+\b"),      # 9:16
    re.compile(r"\b\d+\.\d+\s*(?:Sunburst|Flare|Pro|Lite|Turbo|Preview|Max|Flash|H3|Coder|Image)\b", re.I),
    re.compile(r"\b(?:GPT|Seedance|Seedream|MiniMax|Vidu|Claude|Gemini|GPT-)\s*\d+\.\d+", re.I),
]
# 只忽略个位数。早期版本把 100 / 16 / 2.5 也放进来，
# 结果「售价 100 元」这种假数字被放过——版本号靠 _TECH_TOKEN 处理，不靠这个表。
_IGNORE_NUMS = {str(n) for n in range(0, 11)}


def material_text(material: dict) -> str:
    """只取素材卡里"承载事实"的字段。

    不能直接 json.dumps 整个卡：source_url / id / entity id 里全是数字碎片，
    会让任何数字都"看起来有出处"（实测：「88 分」被 URL 里的 88 蒙混过关）。
    """
    parts: list[str] = []
    for key in ("title", "summary", "body"):
        v = material.get(key)
        if isinstance(v, str):
            parts.append(v)
    for f in material.get("facts") or []:
        if isinstance(f, dict) and f.get("text"):
            parts.append(str(f["text"]))
    for n in material.get("numbers") or []:
        if isinstance(n, dict):
            parts.append(str(n.get("raw") or ""))
            parts.append(str(n.get("value") or ""))
            parts.append(str(n.get("context") or ""))
    for q in material.get("quotes") or []:
        if isinstance(q, dict) and q.get("text"):
            parts.append(str(q["text"]))
    for t in material.get("timeline") or []:
        if isinstance(t, dict):
            parts.append(str(t.get("event") or t.get("text") or ""))
    return "\n".join(parts)


def check_numbers(publish_text: str, material: dict | None, res: Result) -> None:
    """正文/口播里的数字是否都能在素材卡里找到出处。

    只作用于「发布文案」——提示词、参数表、自检表里的数字不算事实。
    """
    if not material:
        res.add("数字可溯源", None, "未提供 --material，跳过")
        return
    if not publish_text.strip():
        res.add("数字可溯源", None, "这份文件不是发布文案，跳过")
        return

    scope = publish_text
    # 只抹掉"自指性数字"（全文 180 字 / 约 40 秒），不要整行删除——
    # 早期版本按行删，结果整段正文因为出现一个"字"字被丢掉，数字核验直接失效。
    for pat in _SELF_METRIC:
        scope = pat.sub(" ", scope)
    for pat in _TECH_TOKEN:
        scope = pat.sub(" ", scope)

    blob = material_text(material)
    # 关键：用 token 集合比对，不能用子串。
    # 早期版本用 `n not in blob`，「88 分」会被素材卡里的 1588 命中，假阴性。
    mat_tokens = set(re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", blob))
    nums = set(re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", scope))
    missing = sorted(n for n in nums if n not in mat_tokens and n not in _IGNORE_NUMS)
    res.add("数字可溯源", not missing,
            f"{len(missing)} 个未在素材卡出现：{missing[:8]}" if missing else "全部命中")


def heading_section(text: str, keywords: list[str]) -> str:
    """按 Markdown 标题抓一段（用于「## 2. 配文」这类非【】结构）。"""
    pat = re.compile(r"^#{1,4}\s*[^\n]*(?:" + "|".join(keywords) + r")[^\n]*$", re.M)
    m = pat.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^#{1,4}\s", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def publish_text_of(text: str, mode: str) -> str:
    """抠出「要发出去的那段字」，数字核验只认它。"""
    if mode == "xhs":
        body = strip_md(section(text, "正文"))
        return body or strip_md(heading_section(text, ["配文", "正文"]))
    if mode == "douyin":
        blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
        spoken = max(blocks, key=lambda b: len(CJK_RE.findall(b))) if blocks else ""
        return re.sub(r"【[^】]*】", "", strip_md(spoken))
    # generic：只出图 + 配文 的成品（flash / image 模式）也要查
    body = strip_md(heading_section(text, ["配文"]))
    # 去掉夹在配文里的制作说明（模型/比例/路线/Canvas 这些不是要发出去的字）
    meta = re.compile(r"模型|比例|路线|Canvas|画质|分辨率|裁到|留白|安全区|提示词")
    return "\n".join(ln for ln in body.splitlines() if not meta.search(ln))


# --------------------------------------------------------------------- 主流程
def detect_mode(text: str, forced: str | None, path: Path | None = None) -> str:
    """判断这份文件是什么。

    教训：早期版本只看「出现小红书三个字」就判 xhs、看「口播+分镜」就判 douyin，
    结果 00-摘要、02-视频提示词 这些非发布文件被按错误模式检查，报一堆假 FAIL。
    现在：文件名优先（摘要/提示词/模板 → generic），再看结构化标记。
    """
    if forced and forced != "auto":
        return forced
    name = path.name if path else ""
    if re.search(r"摘要|素材卡|提示词|自检|template|模板|README", name, re.I):
        return "generic"
    # 小红书：必须有可发布的正文+标签结构
    if "【正文】" in text and ("【标签】" in text or "【标题】" in text):
        return "xhs"
    # 抖音：分镜表 + 钩子段同时存在
    if "黄金 3 秒" in text and ("分镜" in text):
        return "douyin"
    return "generic"


def run_one(path: Path, mode: str, material: dict | None, strict: bool) -> bool:
    text = read(path)
    res = Result()
    mode = detect_mode(text, mode, path)

    if mode == "xhs":
        check_xhs(text, res)
    elif mode == "douyin":
        check_douyin(text, res)
    else:
        res.add("模式识别", None, "generic：只做通用检查")
        check_common(text, res)

    check_ai_label(text, res)
    check_numbers(publish_text_of(text, mode), material, res)

    res.render(f"{path.name}  ·  mode={mode}")
    return res.failed == 0 if strict else res.failed == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="发布前机器校验")
    ap.add_argument("path", help="待校验的 .md 文件或目录")
    ap.add_argument("--mode", default="auto", choices=("auto", "xhs", "douyin", "generic"))
    ap.add_argument("--material", help="素材卡 JSON（用于数字溯源）")
    ap.add_argument("--all", action="store_true", help="目录模式下校验所有 .md")
    args = ap.parse_args()

    material = None
    if args.material:
        material = json.loads(Path(args.material).read_text(encoding="utf-8"))

    p = Path(args.path)
    files = sorted(p.glob("*.md")) if p.is_dir() else [p]
    if not files:
        print(f"[!] 没找到 .md 文件：{p}", file=sys.stderr)
        return 1

    ok = all(run_one(f, args.mode, material, True) for f in files)
    print(f"\n{'=' * 70}")
    print("结论：" + ("全部通过，可以进入人工复核" if ok else "存在 FAIL，先改再发"))
    print("注意：机器过了不等于能发——事实分层、语气、有没有编造，仍要人看。")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
