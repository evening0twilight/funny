# 输入层：素材卡 schema 与多源新闻适配

> **一句话原则：事实优先来自厂商官方发布；聚合站只当导航。**
> AIHOT 是默认主力源，但不是唯一源。任何一条 AI 新闻——AIHOT 事件、厂商博客、TechCrunch、HN 帖子、甚至你从群里复制的一段话——都应该先被 `scripts/prep_input.py` 归一成同一张**素材卡**，后面的写作环节不再关心来源。

---

## 1. 怎么用（30 秒）

```bash
# 1) AIHOT 事件（信息最全：AI 综述 + 20 条报道 + firstParty 标记）
python3 skills/ai-news-content/scripts/prep_input.py \
  --aihot-story 589d286a-2a6d-48be-b14a-e61390534ec3 --out material.json

# 2) AIHOT 热点榜（实时；失败自动回退 data/raw 最新快照）
python3 skills/ai-news-content/scripts/prep_input.py --aihot-hot --limit 10 --out material.json

# 3) 任意新闻页（官方博客 / 媒体 / HN 讨论页）
python3 skills/ai-news-content/scripts/prep_input.py \
  --url https://www.minimax.io/blog/minimax-m31f --out material.json

# 4) 用户直接粘贴的一段文字 / Markdown（完全离线）
pbpaste | python3 skills/ai-news-content/scripts/prep_input.py --file - --out material.json
python3 skills/ai-news-content/scripts/prep_input.py --file news.md --tier third-party --out material.json

# 人工确认抽到了什么（只打印 title + facts/numbers/quotes 计数）
python3 skills/ai-news-content/scripts/prep_input.py --aihot-story <id> --check
```

输出方式：

| 参数 | 行为 |
|---|---|
| 默认 | stdout 打印可读 **Markdown** 素材卡 |
| `--json` | stdout 打印 **JSON** 素材卡（字段与本文一致） |
| `--out PATH` | 落盘到文件：`.json` → JSON，`.md` → Markdown |
| `--out-dir DIR` | 同时落盘 `DIR/card.json` 和 `DIR/card.md` |
| `--check` | 只打印计数，便于确认抽取质量 |

其它常用参数：`--title` / `--source-name` / `--published-at` 覆盖元数据；`--tier` 指定粘贴文本的基础可信度；`--timeout`（默认 20s）；`--refresh`（忽略 AIHOT 缓存）；`--offline`（只用本地缓存/样本）；`--max-facts` / `--max-numbers` 控制上限。

**依赖**：只用 Python 标准库。AIHOT 输入复用 `tools/aihot_fetch.py`（缓存 / 限流 / ETag / 重试）；该文件不存在时自动退回内置 HTTP 客户端。抓网页带 `User-Agent` 和超时，失败会报清楚原因（HTTP 状态 / 网络错误 / 正文太短），**不会静默返回空卡**。

实测（2026-10-20，数据会随 AIHOT 更新变化）：

| 输入 | facts | numbers | quotes |
|---|---|---|---|
| `--aihot-story 589d286a…`（MiniMax M3.1 Flash） | 69（official 3 / first-party 23 / third-party 30 / unverified 13） | 107 | 16 |
| `--url https://www.minimax.io/blog/minimax-m31f` | 27（全部 official） | 14 | 0（原文无直接引语） |
| `--url https://techcrunch.com/2026/10/18/anthropic-…` | 15（全部 third-party） | 5 | 8 |
| `--file <(echo "MiniMax 发布 M3.1 Flash，成本降低 67%")` | 1（unverified） | 1（67%） | 0 |

---

## 2. 素材卡 schema（`schema_version: ai-news-card/v1`）

### 2.1 顶层字段

| 字段 | 类型 | 含义 | 下游怎么用 |
|---|---|---|---|
| `schema_version` | string | 固定 `ai-news-card/v1` | 版本兼容判断 |
| `origin` | `aihot` \| `url` \| `file` | 来源类型 | **判断商用风险的第一依据**（见 `license`） |
| `title` | string | 归一后的标题 | 写稿标题的原料；`--url` 会剥掉站名后缀 |
| `source_name` | string | 来源展示名 | AIHOT 显示「AIHOT（N 信源 / M 报道）」；官方页显示厂商名；文件显示路径或「用户粘贴文本」 |
| `source_url` | string\|null | 原文/阅读页链接 | 引用时挂链接 |
| `published_at` | string\|null | 发布时间，ISO 8601（带 +08:00）或 `YYYY-MM-DD` | 「截至 X 月 X 日」必须用这个锚点 |
| `fetched_at` | string | 抓取时间（+08:00） | 判断时效 |
| `language` | `zh` \| `en` \| `mixed` \| `unknown` | 语种 | 决定是否需要翻译/改写 |
| `summary` | string | 2–3 句摘要（AIHOT 用 digest 首段；URL 用 meta description 或首段） | 快速理解事件 |
| `body` | string | 归一后的正文纯文本 | 需要上下文时回查原文 |
| `entities` | array | 已知实体 + 类型 + 提及次数 | 判断「谁做的」，避免把平台当厂商 |
| `facts` | array | 事实句，**逐条带 tier** | 写稿事实的唯一来源 |
| `numbers` | array | 所有数字单独抽出 | 事实核验原料 |
| `quotes` | array | 引语 + 说话人 | 需要原话时用 |
| `timeline` | array | 时间线（新→旧） | 交代「什么时候发生」 |
| `links` | object | `originals[]` 原文链接、`aihot` 阅读页、`related[]` 相关事件 | 溯源 |
| `source_meta` | object | 各来源的附加信息（story id / 域名 / 段数 / 字数 / 快照回退等） | 排障与复现 |
| `license` | object | 商用提示（`commercial_ok` + `note` + `url`） | **发布前必看** |
| `tier_counts` | object | 四档 tier 的条数统计 | `--check` 摘要 |

### 2.2 `facts[]`

| 字段 | 说明 |
|---|---|
| `id` | `f1`、`f2`…（卡内稳定） |
| `text` | 事实句（已去重、压缩空白） |
| `source` | 信源名：AIHOT 综述 / 某 X 账号 / 媒体名 / 用户粘贴文本 |
| `source_url` | 该事实对应的原文链接（AIHOT digest 句为 story 页；report 句为 `links.original`） |
| `published_at` | 该信源发布时间 |
| `tier` | **`official` / `first-party` / `third-party` / `unverified`** |
| `tier_reason` | 为什么定这一档（可审计，别删） |
| `evidence` | 与综述句关键词重合的报道原文链接（AIHOT story 才有，最多 3 条） |
| `kind` | `digest` / `latest` / `report` / `hot` / `body` / `text` |

### 2.3 tier 四档（写稿纪律的核心）

| tier | 定义 | 判定规则（`prep_input.py` 里可查） | 写的时候 |
|---|---|---|---|
| `official` | **厂商官方发布**：官方博客 / newsroom / API changelog / 官方新闻稿 | AIHOT `source.firstParty=true`；或厂商官方域名命中（minimax.io、openai.com、anthropic.com、blog.google、deepseek.com…）；或综述里明确写「官方称/官方公布」 | 可直接当事实写，最好带时间 |
| `first-party` | **同一方多渠道**：同一厂商自己的 X 账号、公众号、GitHub release 等 | 信源名里出现主角厂商（如「X：MiniMax (@MiniMax_AI)」「公众号：MiniMax」），但未标记 firstParty | 可以当事实写，注明渠道 |
| `third-party` | **媒体报道 / 评测机构 / 平台方转述** | TechCrunch、The Decoder、IT之家、MarkTechPost、Arena、Artificial Analysis、OpenRouter、Ollama…；或 URL 域名在媒体白名单；或 AIHOT 综述句未标注出处（默认保守第三档） | 必须带主体：「据 XX 报道」「XX 评测」 |
| `unverified` | **纯转述 / 无法确认**：个人账号、未知域名、含「据称/未确认/转述」、`--file` 粘贴文本 | Testing Catalog、Rohan Paul、个人 X 账号、未知 blog；正文含不确定表述；`--file` 默认档（可用 `--tier` 覆盖） | **不写**，或明确写「有说法称，未获官方确认」 |

判定顺序（从高到低）：

1. AIHOT 明确标了 `firstParty=true` → `official`
2. 原文域名属于**这条新闻主角厂商**的官方域名 → `official`（官方 blog/changelog）或 `first-party`（厂商自有社媒）
3. 信源名里含主角厂商（官方 X / 公众号）→ `first-party`
4. 已知媒体/评测/平台信源 → `third-party`
5. X / 公众号等社媒账号、未知域名 → `unverified`
6. `--file` / stdin → 全部 `unverified`（除非 `--tier` 显式指定）

> 关键设计决定：**tier 跟事实走，不跟整个 story 走。** 同一条新闻里，官方博客（official）、厂商 X 账号（first-party）、IT之家（third-party）、Testing Catalog（unverified）四档并存；下游写稿只挑 `official`/`first-party` 当结论，`third-party` 必须标来源，`unverified` 不写或标明未确认。`tier_reason` 保留判定依据，方便人工复核。

### 2.4 `numbers[]`（事实核验原料）

| 字段 | 说明 |
|---|---|
| `id` | `n1`… |
| `value` | 数值主体（`73.7`；比例保留 `1/3`；日期保留原文 `10 月 23 日`） |
| `value_num` | 可比较的 float（比例/日期为 `null`） |
| `raw` | 原文片段（`73.7%`、`$0.15`、`56.7T`、`200+ TPS`、`10 月 23 日`） |
| `unit` | `%`、`USD`、`CNY`/`元`、`T`/`B`/`M`、`TPS`、`tokens/s`、`天`、`倍`、`分`、`tokens`、`rank`、`date`、`ratio` |
| `context` | 数字所在**整句**（写稿时回看口径：是「成本」还是「价格」） |
| `source` / `source_url` / `tier` | 来源与可信度（继承所在事实句的 tier） |
| `occurrences` | 同值同句出现次数 |

抽取规则（正则，长匹配优先、去重叠）：比例 `1/3`、百分比 `73.7%`/`百分之七十`、金额 `$0.15`/`1 元`、数量级 `56.7T`/`200T`/`1M`/`200 trillion`、性能 `200+ TPS`/`200 tokens/s`、时长 `72 小时`/`3 天`、日期 `10 月 23 日`/`2026-10-19`、名次 `第 12`/`第 32`、普通数字兜底。**数字和句子一起给**，避免「73.7% 是什么的 73.7%」这种翻车。

### 2.5 `quotes[]` / `timeline[]` / `entities[]`

```json
{
  "quotes": [
    {"id": "q1", "text": "以 M3 三分之一的成本……", "speaker": "官方",
     "source": "AIHOT AI 综述", "source_url": "https://aihot.news/story/…", "tier": "official"}
  ],
  "timeline": [
    {"time": "2026-10-20T11:29:27+08:00", "event": "MiniMax M3.1-Flash 上线 WorkBuddy",
     "source": "X：Tencent WorkBuddy (@WorkBuddy_AI)", "url": "https://x.com/…", "tier": "third-party"}
  ],
  "entities": [
    {"name": "MiniMax", "type": "org", "mentions": 12},
    {"name": "M3.1 Flash", "type": "model", "mentions": 10}
  ]
}
```

- `quotes`：中文引号「」“”『』、英文引号，以及「X 称/表示/宣布…」的归属句；`speaker` 抽不到时为空字符串（不要编）。
- `entities.type`：`org` / `model` / `product` / `media` / `policy` / `platform`。
- `timeline`：AIHOT 来自 `reports[].publishedAt`；URL/文件来自正文日期句（「10 月 23 日开放权重」会按发布年份补全年份，属推断，写稿引用前对一下原文）。

### 2.6 `license`（origin → 能不能商用）

| origin | `commercial_ok` | 含义 |
|---|---|---|
| `aihot` | `requires_authorization` | AIHOT 数据受其条款约束：个人非商业/公益/组织内部免费；对外商业产品、客户交付、数据转售、公开镜像、批量再分发，以及训练/微调/评测/RAG 须**事先取得 AIHOT 书面授权**（https://aihot.news/terms）。商用请改用厂商官方源或先取得授权。 |
| `url` | `unknown` | 厂商官方页：事实可引用，全文/图片转载看该站版权政策；媒体页：只可短句引用并链接原文，整段转载需授权。 |
| `file` | `unknown` | 来源、版权、时效全未知，发布前必须找到原始出处。 |

`commercial_ok` 取值：`yes` / `no` / `requires_authorization` / `unknown`（当前实现不会擅自给 `yes`）。

---

## 3. 四种输入的映射表

| 素材卡字段 | `--aihot-story` | `--aihot-hot` | `--url` | `--file` / stdin |
|---|---|---|---|---|
| `title` | `story.title` | 「AIHOT 热点榜 Top N · 日期」 | `og:title` → `<h1>` → `<title>`（剥站名） | 第一个 `#` 标题 → 首个短行 → 首句；可用 `--title` 覆盖 |
| `source_name` | 「AIHOT（N 信源 / M 报道）」 | 「AIHOT 热点榜」 | `og:site_name` → 厂商名 → 媒体名 → 域名 | 文件路径 / 「用户粘贴文本」 |
| `source_url` | `story.links.aihot` | `https://aihot.news/` | 最终 URL（跟随重定向后） | `null` |
| `published_at` | `story.firstReportAt` | 各条 `latestAt` 最大值 | `article:published_time` → `datePublished` → `<time datetime>` | 正文里的日期；可用 `--published-at` 覆盖 |
| `summary` | digest 首段 | Top N 标题拼接 | meta description → 首段 | 首段 |
| `facts` | digest 逐句（默认 third-party，明确官方口径升 official）+ `latest` + 每条 report 的标题/摘要 | Top N 每条的标题 | 正文逐句（tier 按域名判定） | 逐句（默认 unverified） |
| `numbers` | digest / report 文本 | 热点标题 | 正文 | 正文 |
| `quotes` | digest + report 摘要里的归属句 | 标题（一般无） | 正文引语/归属句 | 正文引语/归属句 |
| `timeline` | `reports[].publishedAt` → 报道标题 | 各条 `latestAt` | 正文日期句 + 页面发布时间 | 正文日期句 |
| `links.originals` | 每条 report 的 `links.original` | 每条热点的 `links.original` | 页面 URL | `[]` |
| `license` | AIHOT 条款 | AIHOT 条款 | 域名判定 | 未知来源 |
| 离线可用 | 有本地缓存/`data/raw` 可回退 | 有本地快照可回退 | 否（需联网） | **是** |

AIHOT story 的字段对应关系（写代码或排障时看）：

| 素材卡 | AIHOT 字段 |
|---|---|
| `title` | `story.title` |
| `summary` / `body` | `story.digest` |
| `published_at` | `story.firstReportAt` |
| `facts`（综述） | `story.digest` 按句切分 |
| `facts`（最新） | `story.latest` |
| `facts`（报道） | `story.reports[].title` + `.summary` |
| `tier`（官方） | `story.reports[].source.firstParty == true` |
| `source_url`（事实） | `story.reports[].links.original` |
| `links` | `story.links.aihot` / `story.links.original` / `story.storyline[]` / `story.related[]` |
| `timeline` | `story.reports[].publishedAt` → `title` |

---

## 4. 非 AIHOT 的 AI 新闻源清单

> 原则：**官方源定事实，聚合源找线索，社区源看反应。** 下面这些都可以直接喂 `--url`（正文页），RSS/API 类可以先落到文件再 `--file`，或自己拉取后作为 `--url` 目标页交给脚本。

### 4.1 厂商官方（事实第一优先，tier=official）

| 名称 | 地址 | 更新频率 | 免费 | 适合做内容 | 备注 |
|---|---|---|---|---|---|
| Anthropic Newsroom | https://www.anthropic.com/news | 不定期（重大发布/政策） | 免费 | ★★★★★ 官方口径、模型卡、政策声明 | 页面可 `--url` 直接抓 |
| Google AI Blog（RSS） | https://blog.google/technology/ai/rss/ | 每周数次 | 免费 | ★★★★☆ Gemini/研究/产品 | RSS 拉取后存 md 再 `--file` |
| Google DeepMind Blog | https://deepmind.google/discover/blog/ | 每周 1–2 次 | 免费 | ★★★★☆ 研究/模型/评测 | 页面可 `--url` |
| Hugging Face Blog（RSS） | https://huggingface.co/blog/feed.xml | 每周数次 | 免费 | ★★★★☆ 开源模型/工具生态 | 偏开发者，适合技术号 |
| MiniMax Blog | https://www.minimax.io/blog | 不定期（模型发布） | 免费 | ★★★★★ 国内模型官方发布 | 本次实测目标页 |
| DeepSeek API 更新日志 | https://api-docs.deepseek.com/zh-cn/updates/ | 不定期（模型/API 变更） | 免费 | ★★★★★ 定价/版本变更一手信息 | AIHOT 热点的 `links.original` 常见来源 |
| OpenAI 新闻/更新 | https://openai.com/news/ | 每周数次 | 免费 | ★★★★★ ChatGPT/模型/政策 | 部分网络环境访问不稳定，备好镜像/转载交叉验证 |
| NVIDIA Blog | https://blogs.nvidia.com/ | 每周数次 | 免费 | ★★★☆☆ 算力/芯片/生态 | 适合产业向内容 |

### 4.2 聚合站 / RSS（找线索、做选题导航，tier=third-party）

| 名称 | 地址 | 更新频率 | 免费 | 适合做内容 | 备注 |
|---|---|---|---|---|---|
| TechCrunch AI（RSS） | https://techcrunch.com/category/artificial-intelligence/feed/ | 每天数条 | 免费 | ★★★★☆ 融资/产品/大公司 | 实测可抓；引用需标 TechCrunch |
| The Decoder（RSS） | https://the-decoder.com/feed/ | 每天 1–3 条 | 免费 | ★★★★★ AI 行业深度快讯 | 英文，AIHOT 常用信源 |
| MarkTechPost（RSS） | https://www.marktechpost.com/feed/ | 每天数条 | 免费 | ★★★☆☆ 模型发布/论文速递 | 偏技术，二手信息多 |
| MIT Technology Review AI（RSS） | https://www.technologyreview.com/topic/artificial-intelligence/feed/ | 每周数次 | 部分免费 | ★★★★☆ 深度/趋势 | 有付费墙，抓正文可能失败 |
| IT之家（RSS） | https://www.ithome.com/rss/ | 每天数十条 | 免费 | ★★★★☆ 国内快讯、中文表述 | 信息快但二手，事实回官方核 |
| 量子位（RSS） | https://www.qbitai.com/feed | 每天 1–3 条 | 免费 | ★★★★☆ 中文 AI 报道 | 适合中文改写参考 |
| 机器之心（RSS） | https://www.jiqizhixin.com/rss | 每天数条 | 免费 | ★★★☆☆ 论文/技术解读 | RSS 可能返回 HTML，注意解析 |
| 36氪（RSS） | https://36kr.com/feed | 每天数十条 | 免费 | ★★★☆☆ 融资/商业 | 与 AI 相关性需过滤 |
| Hacker News（Algolia API） | https://hn.algolia.com/api/v1/search_by_date?query=AI&tags=story | 实时 | 免费、无需 key | ★★★★☆ 技术圈热度/讨论角度 | JSON API，适合看「开发者怎么反应」 |
| Reddit r/MachineLearning（JSON） | https://www.reddit.com/r/MachineLearning/top.json?t=day | 每天 | 免费 | ★★★☆☆ 社区讨论/论文热度 | 常 403，需浏览器 UA/OAuth，谨慎依赖 |
| Hugging Face Daily Papers | https://huggingface.co/papers | 每个工作日 | 免费 | ★★★★☆ 论文选题/模型趋势 | 适合做「今天论文」类内容 |
| arXiv cs.AI（RSS） | https://rss.arxiv.org/rss/cs.AI | 每个工作日 | 免费 | ★★★☆☆ 一手论文（未同行评审） | 事实层级按「预印本/未评审」处理，别当官方结论 |

### 4.3 GitHub 上的 AI news 聚合项目（可 fork / 参考采集管线）

> 这些是**工具/参考实现**，不是事实源；质量参差，挑活跃的看思路即可。

| 名称 | 地址 | 更新频率 | 免费 | 适合做内容 | 备注 |
|---|---|---|---|---|---|
| `Jimmuji/ai-daily-digest` | https://github.com/Jimmuji/ai-daily-digest | 随作者更新 | 免费（开源） | ★★★☆☆ 自动日报思路（DeepSeek 驱动） | 适合参考「抓取 → 摘要 → 日报」流程 |
| `kevinho/clawfeed` | https://github.com/kevinho/clawfeed | 随作者更新 | 免费（开源） | ★★★☆☆ Twitter/RSS 汇总 + 看板 | 适合参考多源聚合与结构化摘要 |
| `0xSMW/rss-feeds` | https://github.com/0xSMW/rss-feeds | 随作者更新 | 免费（开源） | ★★★★☆ AI RSS 源清单 | 直接拿来扩充本文的源列表 |
| `karpathy/arxiv-sanity-lite` | https://github.com/karpathy/arxiv-sanity-lite | 随作者更新 | 免费（开源） | ★★★★☆ 论文筛选/订阅 | 自建 arXiv 关注列表的经典实现 |
| `Ezio0/AI_News` | https://github.com/Ezio0/AI_News | 随作者更新 | 免费（开源） | ★★★☆☆ RSS 版配置参考 | 可看 RSS 源配置方式 |
| `ZJM189/Daily_News` | https://github.com/ZJM189/Daily_News | 随作者更新 | 免费（开源） | ★★★☆☆ 每日定时抓 AI 资讯 | 轻量脚本，适合改造成定时任务 |

**事实来源优先级始终是：厂商官方发布 > 同一方多渠道 > 媒体报道/评测 > 个人转述。** 聚合站和 GitHub 项目只解决「今天有什么值得看」，不解决「这是不是真的」。

---

## 5. 推荐取数组合（兼顾速度与可信）

1. **AIHOT story**（默认）：一条事件的全貌 + 报道时间线，10 秒拿到 digest、20 条报道和 firstParty 标记。
2. **厂商官方原文**（补事实）：从 `facts[].evidence` 或 `links.originals` 里挑官方域名链接，`--url` 再跑一遍，拿到 `official` 事实和官方口径数字。
3. **1 个聚合/社区源**（补视角）：TechCrunch / The Decoder 看外媒角度，HN / Reddit 看开发者反应——这些只当素材和选题信号，不当结论。
4. **交叉检查**：`numbers[]` 里同一指标出现多个口径（如「成本 1/3」vs「定价一半」）时，分开归属，不要合并成一句。

## 6. 已知限制（别踩）

- **JS 渲染页**：只抽静态 HTML。抽不到正文会明确报错，此时用 `--file` 粘贴正文，或换原文/其他媒体链接。
- **反爬/403/429**：脚本带 UA、超时和一次重试；仍失败会给出 HTTP 状态与响应片段。不要暴力重试，换源或稍后再试。
- **付费墙/登录页**：正文会太短并报错；用摘要源 + 官方原文组合。
- **AIHOT 商用**：`origin=aihot` 的卡默认 `requires_authorization`，对外商业使用前必须取得授权或改用官方源（详见 `references/00-sourcing-and-rights.md`）。
- **时效**：`published_at` 是「发布」时间，不是「你抓取」时间；写「截至目前」时用 `fetched_at` 做锚点。
- **tier 不是自动真理**：规则是启发式的，`tier_reason` 和 `evidence` 是给人复核的；有疑问就点开 `source_url` 看一眼。

## 7. 加一个新来源（扩展点）

在 `scripts/prep_input.py` 里改三处即可：

1. `VENDOR_DOMAINS`：厂商官方域名 → vendor key（命中即 `official`）。
2. `MEDIA_DOMAINS`：媒体/平台域名 → 展示名（命中即 `third-party`）。
3. `ENTITY_LEXICON`：实体词表（org/model/media/policy），用于 `entities` 与「主角厂商」判断。

如果新源是 RSS/API，先抓到本地文本（或让 `--url` 指向文章页），再复用现有抽取逻辑，不要为单个源写特例。
