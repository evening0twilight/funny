# tools/ 取数层：AIHOT REST API v1 采集器

给「AI 新闻 → 短视频/图文二创」流水线提供**干净的结构化输入**。不爬网页，只调 AIHOT 官方匿名只读接口
（[OpenAPI v2.0.0](https://aihot.news/openapi-v1.json)、[Agent 使用说明](https://aihot.news/api/v1/agent)）。

```
tools/
├── aihot_fetch.py        # 采集器（Python 3 标准库，无第三方依赖）
└── README.md             # 本文件：用法 / 字段 / 限流 / 许可
skills/aihot/             # 官方 AIHOT Agent Skill v2.0.0（install.sh --dir 安装）
data/raw/2026-10-20/      # 2026-10-20 抓取的接口原始返回（真实数据，非 mock）
data/.cache/              # 本地 HTTP 缓存 + actor-id + 限流窗口（可安全删除）
```

---

## 0. 官方 Skill（已安装并验证）

用官方 `install.sh --dir` 装到项目内，不写 `$HOME`：

```bash
bash <(curl -fsSL https://aihot.news/aihot-skill/install.sh) \
  --dir /Users/a1-6/projects/person/funny/skills/aihot
```

安装结果（`v2.0.0`，安装器逐个校验 SHA-256 后整体替换）：

| 文件 | 说明 |
|---|---|
| `skills/aihot/SKILL.md` | Skill 正文。它只调 `/api/v1/agent/*`（Markdown 版接口）+ `/api/v1/agent` 使用说明，不调 JSON 接口 |
| `skills/aihot/LICENSE` | MIT（只覆盖 Skill 指令文件，**不覆盖** AIHOT 服务/数据） |
| `skills/aihot/agents/openai.yaml` | 展示名 / 默认 prompt |
| `skills/aihot/.aihot-actor-id` | 安装器生成的随机 UUID（0600，匿名去重统计用，不是 Key/账号） |
| `skills/aihot/.gitignore` | 安装器生成，忽略上面那个 actor 文件 |

> 坑：安装脚本会在 `$HOME` 下建安装锁 `~/.aihot-skill-install.lock`。本仓库沙箱只允许写 workspace，
> 因此安装时把 `HOME` 指向了 workspace 内的临时目录（`HOME=.../tmp/home bash install.sh --dir ...`），
> 目标目录仍是 `skills/aihot`。普通环境直接跑上面的命令即可。

---

## 1. 快速开始

```bash
cd /Users/a1-6/projects/person/funny

# 当前热点 Top 10：名次 + 标题 + 热度(信号/信源/参与方) + 摘要 + 最新进展 + id
python3 tools/aihot_fetch.py hot

# 事件全貌（报道时间线 + AI 综述）：publicId 或热点里的 story 链接都行
python3 tools/aihot_fetch.py story 589d286a-2a6d-48be-b14a-e61390534ec3

# 最新日报 / 指定日期日报
python3 tools/aihot_fetch.py daily
python3 tools/aihot_fetch.py daily --date 2026-10-20

# 条目列表：全部公开动态、按分类、分页
python3 tools/aihot_fetch.py items --mode all --limit 50
python3 tools/aihot_fetch.py items --category ai-models --window 24h
python3 tools/aihot_fetch.py items --limit 50 --mode all --cursor '<page.nextCursor>'

# Agent 用 Markdown（给 LLM 直接读，自带「回答提示」）
python3 tools/aihot_fetch.py agent-hot --limit 10
python3 tools/aihot_fetch.py agent-latest --window 7d --limit 20

# 原样落盘 + 原样打印（--json / --save 可放子命令前后）
python3 tools/aihot_fetch.py --save data/raw/2026-10-20/hot-topics.json hot
python3 tools/aihot_fetch.py hot --save data/raw/2026-10-20/hot-topics.json
python3 tools/aihot_fetch.py --json items --limit 3
```

退出码：`0` 成功；`1` 接口/网络错误（stderr 有原因）；`2` 参数错误。数据只走 **stdout**，
提示、限流、保存日志走 **stderr**。

> 速度：`hot` 在缓存过期时要为 10 条热点逐个补 story 摘要，约 10–30s（顺带把 story 详情写进缓存，
> 随后 `story` 命令秒回）；加 `--no-summary` 或 `--json` 就只请求 1 次 hot-topics 接口。

---

## 2. 子命令与接口对照

| 子命令 | 接口 | 关键参数 | 终端输出要点 |
|---|---|---|---|
| `hot` | `GET /api/v1/hot-topics` | `--limit 1-10`、`--no-summary` | 名次、标题、热度三指标、摘要、最新进展、id、story publicId、信源列表 |
| `daily` | `GET /api/v1/dailies/latest` 或 `/api/v1/dailies/{date}` | `--date YYYY-MM-DD` | 头条、分栏（模型/产品/行业/技巧观点）、快讯、链接 |
| `items` | `GET /api/v1/items` | `--limit 1-100`、`--category`、`--mode selected\|all`、`--window 24h\|7d`、`--by timeline\|published`、`--q`、`--cursor` | 标题、分类、score、精选标记、摘要、推荐理由、id、阅读页 |
| `story <publicId>` | `GET /api/v1/stories/{publicId}` | 位置参数可传 id 或 story URL | 状态、信源/报道数、时间跨度、最新进展、AI 综述、报道时间线、相关故事 |
| `agent-hot` | `GET /api/v1/agent/hot` | `--limit 1-10` | 原样 Markdown（含「回答提示」） |
| `agent-latest` | `GET /api/v1/agent/latest` | `--limit 1-30`、`--window`、`--mode`、`--category` | 原样 Markdown |

所有子命令都支持通用选项：

| 选项 | 作用 |
|---|---|
| `--json` | 打印接口原始返回（JSON 命令=原始 JSON；agent 命令=原始 Markdown），不打印人读格式 |
| `--save PATH` | 把接口原始返回**原样**写入文件（自动建父目录），同时仍可打印人读格式 |
| `--refresh` | 忽略本地 TTL，重新请求（仍带 `If-None-Match`，304 时复用缓存） |
| `--no-cache` | 不读不写缓存，强制完整请求 |
| `--cache-dir DIR` | 缓存目录（默认 `data/.cache`，也可用 `AIHOT_CACHE_DIR`） |
| `--timeout SEC` | 单次请求超时，默认 20s |
| `--actor UUID` | 覆盖 `aihot-actor/<uuid>`（默认复用 `skills/aihot/.aihot-actor-id`） |

---

## 3. 字段说明与「做内容」用途

### 3.1 `hot-topics.json`（`/api/v1/hot-topics`）

`schemaVersion=1`、`count`、`items[]`。每个热点：

| 字段 | 含义 | 对二创的用途 |
|---|---|---|
| `rank` | 1–10 名次 | 排片/标题党参考，别自己重排 |
| `id` | 条目 id（`/items/{id}`） | 关联条目 |
| `title` | 事件标题 | 视频标题素材 |
| `links.aihot` / `links.original` | AIHOT 阅读页 / 原始出处 | 署名、回溯原文 |
| `links.story` | 事件页 **HTML** URL（旧域名 `aihot.virxact.com`）**不能当 API 请求**；取最后一段 publicId 再调 `/stories/{publicId}` | 拿时间线/AI 综述 |
| `sourceCount` / `signalCount` / `participantCount` | 信源数 / 信号数 / 参与方数 | **热度依据**（接口没有单一“热度分”） |
| `sourceNames[]` | 信源名称 | 佐证“多源在讨论” |
| `latestAt` | 最新进展时间（UTC ISO） | 新鲜度判断 |

> `hot` 命令的“摘要/最新进展”来自对每个热点 `story` 的 `digest`/`latest` 二次请求（已缓存）；
> `--no-summary` 或 `--json` 时只打 1 次 hot-topics 接口。

### 3.2 `items.json`（`/api/v1/items`）

顶层：`schemaVersion`、`query`（实际生效的 mode/category/window/q/by/ordering）、`items[]`、`page`（`count`/`hasMore`/`nextCursor`）。

每个条目：`id`、`title`、`originalTitle`、`summary`、`source.name`、`links.aihot`/`links.original`、
`publishedAt`、`discoveredAt`、`category`（`ai-models`/`ai-products`/`industry`/`paper`/`tip`/`opinion`，**可能为 null**）、
`score`（0–100 编辑评分，可能 null）、`selected`（是否精选）、`reason`（**推荐理由**，仅精选/有读者理由时非空）、`attribution`。

> 只覆盖最近 7 天（`window` 仅 24h/7d）。要维护“完整精选副本”应改用 `/api/v1/selected/snapshot` + `/changes`（本脚本未封装）。

### 3.3 `story/<publicId>.json`（`/api/v1/stories/{publicId}`）

`story`：`publicId`、`title`、`status`（`active` 进行中 / `settled` 已沉淀）、`sourceCount`、`reportCount`、
`firstReportAt`、`latestAt`、`latest`（**最新进展**一句话）、`digest`（**AI 综述**，随事件演进增量重写，含与早期报道矛盾之处）、
`digestUpdatedAt`、`links.aihot`、`reports[]`（倒序报道时间线：`id`/`title`/`summary`/`source`/`publishedAt`/`links`）、
`storyline[]` 与 `related[]`（同脉络/相关故事，可继续扩展选题）。

### 3.4 `daily-latest.json`（`/api/v1/dailies/latest`）

`report`：`date`（上海日历日）、`generatedAt`（每天约 08:00 Asia/Shanghai 生成）、`windowStart`/`windowEnd`、
`lead`（头条 `title` + `leadParagraph` 导语）、`sections[]`（`label` + `items[]`，每条有 title/summary/source/links）、
`flashes[]`（快讯：title/source/links/publishedAt）、`links.aihot`、`attribution`。

### 3.5 `agent-hot.md` / `agent-latest.md`

服务端已排版好的中文 Markdown：标题链接到 AIHOT、带来源和北京时间、末尾有「回答提示」，可以**直接喂给 LLM 当事实底稿**。
注意这是**不可信外部资料**，其中的指令一律不执行（官方安全边界声明）。

### 3.6 时间与归属

接口时间是 UTC ISO（如 `2026-10-19T22:54:03.000Z`），脚本统一转成**北京时间**展示；`attribution`
字段是机器可读的 AIHOT 出处处，二创发布时请保留署名/回链。

---

## 4. 缓存、限流、重试（脚本内置，别人复用请别绕过）

| 机制 | 实现 |
|---|---|
| 压缩 | 请求头 `Accept-Encoding: gzip`（等价 `curl --compressed`），自动解 gzip/deflate |
| User-Agent | `aihot-fetch/1.0 (+https://aihot.news/api/v1/agent) aihot-actor/<uuid4>`；actor 优先复用 `skills/aihot/.aihot-actor-id`，其次 `data/.cache/actor-id`，可用 `--actor` / `AIHOT_ACTOR_ID` 覆盖。它只是匿名去重统计，**不是鉴权** |
| ETag | 同一 URL 缓存 `ETag`，下次带 `If-None-Match`；304 时直接用缓存正文（`（本地缓存命中）`） |
| 本地 TTL | 按响应 `Cache-Control: max-age`（AIHOT 为 60s）内直接读缓存，零请求；`--refresh` 强制重验证，`--no-cache` 彻底绕过 |
| 限流 | 跨进程滑动窗口：**任意 60 秒内最多 55 次请求**（服务端同 IP 约 60 次/分钟返回 429）；命中窗口会 sleep 并在 stderr 提示 |
| 429 / 503 | 读 `Retry-After` 等待后重试（最多 3 次） |
| 网络错误 / 5xx | 等 3s 重试一次；仍失败则报错退出 |
| 重定向 | 自动跟随 301/302/303/307/308（story 合并时会 308 到存活 id） |

缓存目录 `data/.cache/`：`http/<sha256(url)>.json`（正文+ETag+时间）、`actor-id`、`ratelimit.json`。可随时删除，只会让下次变慢。

> 代理：脚本用 `urllib`，会自动读取 `HTTP(S)_PROXY` 环境变量；本机环境走 `http://127.0.0.1:7897` 正常。

---

## 5. 已落盘数据：`data/raw/2026-10-20/`

抓取时间 **2026-10-20 11:34–11:35（北京时间）**，全部为接口真实返回，未经改写：

| 文件 | 大小 | 数据量 | 对应接口/参数 |
|---|---|---|---|
| `hot-topics.json` | 5.7 KB | 10 条热点 | `/api/v1/hot-topics` |
| `daily-latest.json` | 11.5 KB | 日报 1 期：4 栏 12 条 + 8 条快讯 | `/api/v1/dailies/latest`（date=2026-10-20） |
| `items.json` | 88.3 KB | 100 条（99 条有摘要，6 条精选带推荐理由） | `/api/v1/items?mode=all&window=7d&limit=100` |
| `story/589d286a-….json` | 13.6 KB | 报道 20 条 + 723 字 AI 综述 | 热点 #1 MiniMax M3.1 Flash |
| `story/f8045374-….json` | 18.1 KB | 报道 25 条 + 748 字 AI 综述 | 热点 #2 DeepSeek V4.1-Flash-1017 |
| `story/66a54812-….json` | 3.8 KB | 报道 4 条 + 295 字 AI 综述 | 热点 #3 Anthropic 公益基金 |
| `agent-hot.md` | 3.7 KB | Markdown 版 Top 10 | `/api/v1/agent/hot` |
| `agent-latest.md` | 8.2 KB | Markdown 版精选 10 条 | `/api/v1/agent/latest?limit=10` |

抽查命令：

```bash
python3 - <<'PY'
import json,glob,os
b='data/raw/2026-10-20'
h=json.load(open(f'{b}/hot-topics.json')); print('hot', h['count'], len(h['items']))
d=json.load(open(f'{b}/daily-latest.json'))['report']; print('daily', d['date'], len(d['sections']), sum(len(s['items']) for s in d['sections']), len(d['flashes']))
i=json.load(open(f'{b}/items.json')); print('items', len(i['items']), i['query']['mode'], i['page']['hasMore'])
for p in glob.glob(f'{b}/story/*.json'):
    s=json.load(open(p))['story']; print('story', s['publicId'], s['reportCount'], len(s['digest'] or ''))
PY
```

---

## 6. 已知坑 / 字段缺失（实测）

1. **`hot-topics` 没有“热度分/摘要/推荐理由”**：只有 `signalCount`（信号数）、`sourceCount`（信源数）、`participantCount`（参与方）。
   脚本的“摘要”是额外请求该热点 story 的 `digest` 补出来的；“热度”按三个计数展示，不是官方单一分值。
2. **`links.story` 是旧域名 HTML 页**（`https://aihot.virxact.com/story/<publicId>`），**不能当 JSON 接口请求**；
   必须取最后一段 publicId 再调 `/api/v1/stories/{publicId}`。脚本已处理（也支持直接传 URL）。
3. **`items` 只有最近 7 天**，且 `window` 只有 `24h/7d`，不能当历史库；`q` 搜索也只覆盖 7 天。历史用 `{date}` 日报/周报/月报接口。
4. **可为空的字段**：`items[].category`（本次 100 条中 4 条为 null）、`items[].summary`（1 条 null）、
   `items[].score`（可能 null）、`items[].reason`（仅精选有，本次 6 条）。`publishedAt` 可能为 null（回填/无可靠发布日期时）。
5. **`story` 会合并**：`reportCount` 在事件发酵中持续涨，合并后的 story 返回 308 到存活 id；脚本自动跟随重定向。
6. **`dailies/latest` 每天约 08:00（Asia/Shanghai）才更新**；要历史某天用 `--date`，且不能瞎猜日期（官方建议先 `dailies?limit=1` 拿日期）。
7. **上限**：`items.limit ≤ 100`，`agent/hot limit ≤ 10`，`agent/latest limit ≤ 30`，`hot-topics` 固定 Top 10；翻页只能靠 `cursor`（与 query 绑定）。
8. **429 与自动重试**：脚本会按 `Retry-After` 等待；若看到 `[限流]` stderr 提示是本地保护，属正常现象。
9. **安装脚本行为**：必须显式 `--target` 或 `--dir`（无参数只打印帮助）；会在 `$HOME` 建安装锁并生成
   `.aihot-actor-id`/`.gitignore`；沙箱环境需把 `HOME` 指到可写目录（见第 0 节）。
10. **`notice` 字段**：接口偶尔返回 `notice`（skill 更新/域名迁移等面向用户的公告），脚本会打印到 stderr `[AIHOT 公告]`，按提示转告用户一次即可。

---

## 7. 许可与使用规则（重要，别踩线）

> AIHOT 的公开使用规则（https://aihot.news/terms ）：
> **个人非商业、公益非商业和组织内部使用免费。**
> 任何面向外部的商业产品、收费服务、客户交付、代理接口、数据转售、公开镜像、白标、批量公开再分发，
> 或面向外部的训练/微调/评测/检索增强生成/答案产品，**都须事先取得 AIHOT 书面授权**；
> 仅标注「数据来源：AIHOT」不等于已获授权。授权联系 **wzglyay@virxact.com**。
>
> 匿名、无需 API Key 只说明技术访问方式，不代表所有用途均获许可。
> `LICENSE` 里的 MIT 只覆盖 Skill 指令与随附文件，**不覆盖 AIHOT 服务、数据输出或第三方原文**；
> 第三方原文及全文版权仍归原作者，重要数字/原话请回原文核对。
> 二创发布时保留 `attribution` 署名与回链（AIHOT 阅读页），并遵守目标平台的转载规则。

本仓库当前定位为**个人/内部研究与非商业内容试验**；若要对外商用，请先按上面流程取得授权。

---

## 8. 对「做内容」最有用的字段（实测推荐）

| 优先级 | 字段 | 为什么好用 |
|---|---|---|
| ★★★ | `story.digest`（AI 综述） | 多源交叉后的事实底稿，含矛盾点说明，几百字可直接改写成分镜脚本 |
| ★★★ | `story.latest`（最新进展） | 一句话“现在到哪一步了”，适合做视频开头钩子 |
| ★★★ | `items[].reason`（推荐理由） | 编辑视角的“为什么值得讲”，直接决定选题价值，**只有精选条目才有** |
| ★★☆ | `daily.lead` + `sections` + `flashes` | 一天叙事的现成骨架：头条→分栏→快讯 |
| ★★☆ | `hot-topics.signalCount/sourceCount/participantCount` | 热度证据（多源同时讨论），比单一分数好讲 |
| ★★☆ | `story.reports[]`（时间线） | 事件“起承转合”顺序 + 每条原文链接，便于求证与引用 |
| ★☆☆ | `agent-*.md` 的「回答提示」 | 官方给 LLM 的讲解规范，可直接作为写作提示词模板 |
| ★☆☆ | `story.storyline/related` | 做系列选题、上下集 |

---

## 9. `topic_score.py` —— 选题打分（做视频前先跑它）

`aihot_fetch.py` 只负责「拿到数据」，`topic_score.py` 负责回答「今天这 10 条，我该做哪 2 条」。

```bash
python3 tools/topic_score.py                      # 均衡权重
python3 tools/topic_score.py --profile news       # 资讯号：情绪/冲突优先
python3 tools/topic_score.py --profile tool       # 工具号：实用/收藏优先
python3 tools/topic_score.py --profile opinion    # 观点号：冲突 + 可视化
python3 tools/topic_score.py --top 3 --json       # 前 3 条，机器可读
```

### 打的是什么分

| 维度 | 权重（news 号型） | 判断依据 |
|---|---|---|
| 热度 | 30% | `signalCount` 与 `participantCount` 归一化 |
| 冲突/情绪 | 40% | 封杀/禁令/失控/被捕/诉讼… 关键词命中（决定完播率） |
| 实用价值 | 10% | 发布/上线/开源/免费/降价… （决定收藏率） |
| 受众相关 | 10% | DeepSeek/MiniMax/Qwen/开源… （AI 资讯号主力人群） |
| 可视化 | 10% | 数字密度：亿/万/倍/token/%（能不能做成卡片和数据镜） |

### 几个使用要点

- **它会自动用 `data/raw/<date>/story/*.json` 里的 AI 综述补全摘要**。`hot-topics` 本身不带摘要，不补的话「可视化」维度会全是 0。想让它更准，就先 `aihot_fetch.py hot` 把 10 条都抓一遍 story。
- 分数是**筛子不是决策**：前 2 条值得做，第 3 条之后除非你有独特视角，否则别碰。
- 同一批新闻，`--profile tool` 和 `--profile news` 排出来的第一名经常不是同一条——这不是 bug，是号型不同。
- 关键词表在文件顶部，做垂直号（比如只讲 AI 编程、只讲国产模型）时直接改 `CN_RELEVANT` 和 `CONFLICT` 词表。
