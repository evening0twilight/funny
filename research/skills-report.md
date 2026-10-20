# 社区 Skills 选型与实测报告：AI 新闻 → 小红书/抖音内容 + AI 视频提示词

- 调研人：skills-scout（Team Lead 的 Skills 选型任务，task-2）
- 调研时间：2026-10-20 11:30–12:10（Asia/Singapore），star/许可/commit 均为该时点查证
- 测试素材：AIHOT 2026-10-20 热点 **No.01「MiniMax 发布 M3.1 Flash，权重 10 月 23 日开放」**
  - 原始输入：`research/tests/input-news-01.md`（来自 `https://aihot.news/api/v1/agent/stories/589d286a-2a6d-48be-b14a-e61390534ec3`，含 AI 综述 + 18 条报道时间线 + 一手来源标记）
- 安装位置：`skills/<name>/`，每个旁附 `provenance.md`；实测产出：`research/tests/<skill>/`

---

## 0. 结论速览（先看这段）

**能直接用、且我有信心直接发小红书的，只有一个组合，不是单个 skill：**

| 用途 | 推荐 | 组合方式 |
|---|---|---|
| **A. 中文文案扩写**（小红书图文 / 抖音口播稿） | `cn-skills`（LLL-178，star 仅 1⭐，但规则最硬）× 或 `xhs-image-text-generator`（sanqi，28⭐，交付管线最完整） | 先用主 skill 产出，再用 `shuorenhua`（2184⭐）过一遍去 AI 味 |
| **A. 配图/卡片（可选）** | `guizang-social-card`（7596⭐，AGPL-3.0） | 只在需要做小红书卡片图时启用 |
| **B. AI 视频提示词** | `lanshu-video-kit`（424⭐，中文原生，即梦/可灵/Seedance）为主；`shortfilm-prompt`（476⭐，电影感叙事）为「概念片/品牌片」备选 | B 只产出画面提示词，**不产出内容结构**，必须先用 A 定好讲什么 |

**一句话总结：「小红书文案」和「视频提示词」这两个赛道，社区里真正能打的不是 star 最高的，而是「把约束写死、能自检、有脚本/评测」的那几个小仓库。**

- 最高 star 的 `guizang-social-card`（7.6k）根本不是文案 skill，是配图排版 skill。
- 出现频率最高的 `vivy-yi/xiaohongshu-skills`（493⭐、139 个 SKILL.md）是**提示词散文集**，实测产出全是「绝绝子/感动哭了」的美妆号语气，0 处可用。
- `redfox-community`（447⭐、132 个 SKILL.md）里 **130 个 SKILL.md 都要求你注册并充值它自家的 API**，无 LICENSE，是伪装成 skill 的商业引流。
- 官方 `anthropics/skills`（18.2 万⭐）**没有任何一个**小红书/抖音/视频提示词技能。

---

## 1. 候选全景表

> star / last push / license 全部为 2026-10-20 11:35 ± 5 分钟通过 GitHub API（`/repos/{owner}/{repo}`）查证。
> 「判定」列是最终结论：✅ 推荐 · 🟡 有条件可用 · ❌ 淘汰。

### 1.1 中文内容扩写（A 类）

| # | Skill / 仓库 | Star | License | Last push | 形态 | 判定 |
|---|---|---|---|---|---|---|
| 1 | [sanqi-cd/Sanqi-Skills](https://github.com/sanqi-cd/Sanqi-Skills) › `xhs-image-text-generator` | **28** | MIT | 2026-10-01 | 203 行 SKILL.md + 4 个脚本 + carousel schema + evals | ✅ 推荐（管线最完整；star 少的硬伤已注明） |
| 2 | [LLL-178/cn-skills](https://github.com/LLL-178/cn-skills) › `xiaohongshu-post` + `douyin-script` | **1** | MIT | 2026-09-06 | 114 / 76 行 SKILL.md，量化规则 + 自检清单，无脚本 | ✅ 推荐（规则最像行家；社区验证为零，仅作「文案主笔」） |
| 3 | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | **2184** | MIT | 2026-10-19 | 75 行 SKILL.md + 123 case benchmark + 20 场景样本 + 多版本评测记录 | ✅ 推荐（唯一有公开 benchmark 的中文写作 skill，作「去 AI 味」终检） |
| 4 | [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) | **7596** | **AGPL-3.0** | 2026-07-01 | 336 行 SKILL.md + 16 篇 references + seed HTML 模板 + 校验脚本 | 🟡 有条件推荐（配图层；AGPL + 需浏览器/截图） |
| 5 | [wenziai/wenzi-xiaohongshu-workflow](https://github.com/wenziai/wenzi-xiaohongshu-workflow) | 175 | **无 LICENSE** | 2026-10-12 | 6 个 skill（账号定位→选题→改稿→排期），有真实运营截图 | ❌ 淘汰（**无 license，默认保留所有权利，不可合规复用**） |
| 6 | [OrangeViolin/content-pipeline](https://github.com/OrangeViolin/content-pipeline) | 218 | MIT | 2026-04-12 | 672 行 SKILL.md，素材→出稿→排版→封面→CDP 自动发布 | 🟡 未实测潜力股（强绑个人品牌 01fish + Chrome CDP，未测不推荐） |
| 7 | [JiamanJemma/social-creator-toolkit](https://github.com/JiamanJemma/social-creator-toolkit) | 35 | MIT | 2026-03-04 | 642 行 SKILL.md，全平台标题/文案/封面提示词/发布时间 | 🟡 全景表列名（star 低、无评测，未进实测） |
| 8 | [vivy-yi/xiaohongshu-skills](https://github.com/vivy-yi/xiaohongshu-skills) | **493** | **无 LICENSE** | 2026-01-23 | **139 个** SKILL.md，每个 150–800 行「百科长文」 | ❌ **淘汰，见 §4.1 实测** |
| 9 | [redfox-data/redfox-community](https://github.com/redfox-data/redfox-community) | 447 | **无 LICENSE** | 2026-10-19 | 132 个 SKILL.md，其中 **130 个要求 redfox.hk 付费 API Key** | ❌ 淘汰（商业引流外包成 skill） |

### 1.2 AI 视频提示词（B 类）

| # | Skill / 仓库 | Star | License | Last push | 形态 | 判定 |
|---|---|---|---|---|---|---|
| 10 | [cclank/lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) | **424** | MIT | 2026-10-07 | 7 个 SKILL.md（含路由）+ 21 篇中文 methodology（另有 README）+ 594 条提示词库 | ✅ 推荐（中文原生 + 模型工程化，最贴国内模型） |
| 11 | [jnMetaCode/ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) | **476** | MIT（`prompts/` 除外，见 NOTICE） | **2026-10-19** | 411 行 SKILL.md + 29 个题材模板 + 6 个完整示例 + evals + CI | ✅ 推荐（约束最硬的电影感提示词；题材偏概念片） |
| 12 | [Wayhhow/ai-video-shot-prompt-skill](https://github.com/Wayhhow/ai-video-shot-prompt-skill) | 16 | MIT 文件 / GitHub 识别 NOASSERTION | 2026-09-06 | 157 行 SKILL.md + 10 references + `validate_prompt.py` + 6 个测试 | ❌ 淘汰（工程不错但 16⭐无社区验证 + license 声明不一致） |
| 13 | [shuhaolin63-hash/GuoFanDirector_Skills](https://github.com/shuhaolin63-hash/GuoFanDirector_Skills) | 7 | MIT | 2026-07-20 | 短剧分镜提示词（克隆 112MB，内容未完整取到） | ❌ 淘汰（7⭐，无法验证内容，体积异常） |
| 14 | [Hao0321/ai-media-generator](https://github.com/Hao0321/ai-media-generator) | 未查证 | 未查证 | — | 14+ 平台图像/视频/音乐提示词 | ❌ 未入选（仅在搜索结果出现，无法验证 star/维护） |
| 15 | [liangdabiao/skill-ten-prompt-generator](https://skillsmp.com/ko/creators/liangdabiao/skill-ten-prompt-generator/claude-skills-video-prompt-generator) | 未查证 | 未查证 | — | 注册站上的 video-prompt-generator | ❌ 未入选（注册站条目，仓库元数据无法核） |

### 1.3 框架与官方仓库（作参照，不作推荐）

| # | 仓库 | Star | License | 结论 |
|---|---|---|---|---|
| 16 | [anthropics/skills](https://github.com/anthropics/skills) | 182,275 | 无顶层 LICENSE（分 skill 声明） | **没有** 小红书/抖音/视频提示词技能。19 个技能里最接近的 `internal-comms`（企业沟通）、`doc-coauthoring`（文档合写）都不解决中文平台内容。判 **不适用** |
| 17 | [obra/superpowers](https://github.com/obra/superpowers) | 302,187 | MIT | 工程方法论框架（brainstorming / plan / TDD / review）。对「写文案」无直接技能，但它的 skill 结构（frontmatter + 渐进式 references）可作为自己封装 skill 的范本。判 **不适用但值得学结构** |
| 18 | mattpocock/skills | 297,646 | MIT | 同类工程 skills，不适用 |

---

## 2. TOP 推荐与淘汰理由

### 2.1 A 类主笔（二选一，都用真实产出验证过）

**① `cn-skills › xiaohongshu-post` + `douyin-script`（1⭐，MIT）—— 文案规则最硬**

选定理由（不是 star）：
- 小红书部分给出**可核对的数量约束**：标题 ≤20 字且 5 类公式、正文 300–800 字（>800 完读率断崖）、开头三行定生死、emoji 每段最多 1 个整篇 ≤8、**明令禁止输出 Markdown 加粗**（因为小红书不渲染 `**`）、标签 5–8 个「大流量泛标签 + 精准垂类 + 自定义」搭配。
- 抖音部分给出**换算口径**：语速 240–280 字/分钟折算时长、每句 ≤15 字、每 5–10 秒埋一个刺激点、输出分镜表（画面/口播/字幕/时长）。
- 有自检清单，且清单里的每一条都能用脚本验（实测见 §3.2）。
- 唯一同时覆盖「小红书图文」和「抖音口播」的候选。

淘汰不了的原因也是它：**star=1，没有任何社区验证，也没有 benchmark**。所以我在报告里把它定位为「规则可用、但请当作自己团队的内部 SOP 使用，别当成行业共识」。

**② `xhs-image-text-generator`（28⭐，MIT）—— 交付管线最完整**

选定理由：
- 5 个 Step 从「素材归一 → 发布方案 → 分页 → 图片页 → 交付包」，每一步都有**可执行动作**：`normalize_input.py`（URL/HTML/MD 抽正文）、`render_carousel_html.py`（carousel.json → 1080×1350 排版 HTML，锁定文字与页数）、`validate_delivery.py`（**校验不过不许说完成**）。
- 交付物定义到文件名：`manifest.md` / `caption.txt` / `hashtags.txt` / `comments.txt` / `image-prompts.md` / `carousel.json` / `quality-check.md`。
- 有 evals（`evals/evals.json` + `trigger-evals.json`），有「高风险主题开工门槛」（投资/医疗/法律类没素材就先问、不许编）。

**硬伤说清楚**：28⭐、单作者、依赖生图模型；我实测时它的校验器**真的抓到了我漏填的占位符**（`FAIL: unresolved placeholder found`），这是「有自检」的实战证据，不是宣传。

**③ 终检：`shuorenhua`（2184⭐，MIT）**

它不是文案 skill，而是最后一道工序：删套话、去翻译腔、降夸饰，同时**保住数字、限定词、责任主体、否定/情态**。选它的核心理由是**它是本次唯一带公开评测的中文写作 skill**：`evals/` 有 benchmark 123 cases、20 个场景样本、盲测文件和 v1.4→v2.6 的历次结果记录，README 还明确拒绝「判断 AI 含量/规避检测」这种伪需求。

### 2.2 A 类配图（可选）

**`guizang-social-card`（7596⭐，AGPL-3.0）**：中文社区 star 最高的小红书图文 skill，但**它不是文案 skill**。实测（§3.4）证明它能产出结构合法、class 全部命中模板、硬规则全过的 3:4 卡片 HTML；同时它的能力圈写得非常诚实（明说「美食摆盘/日常 OOTD/梦核/Y2K/纯摄影 showcase 不在能力圈，要当场拒绝」）。三个门槛必须提前知道：**AGPL-3.0**、需要真实截图作证据层、需要本地浏览器渲染。

**淘汰**：`wenziai`（无 license）、`content-pipeline`（未测，强绑 01fish 品牌 + CDP 自动发布，不适合直接给用户）、`social-creator-toolkit`（35⭐，未测）。

### 2.3 B 类视频提示词（按题材分工，不是二选一）

**① `lanshu-video-kit`（424⭐，MIT）—— 中文原生、国内模型为主**

- 7 个 skill 有明确路由与「何时不用本 skill」：`model-selector` / `seedance-prompter` / `seedance-storyboard` / `happyhorse-prompter` / `kling-prompter` / `seedance-debugger` / `prompt-translator`。
- 21 篇中文 methodology 是知识底座：约束词清单、运镜词典、情绪外化表、分镜时序、六大模型公式速查、避坑 12 问。
- 有工程约束：每镜只 1 种运镜、不写死秒数（「模型对精确时间支持不稳定」）、主体稳定标签、`@图片N` 素材角色、必加三条约束（水印/Logo/字幕）、防「双胞胎」词。
- 有 CI 每周盯 24/32 个模型官方端点版本变化，说明在维护而不是一次性 dump。

**② `shortfilm-prompt`（476⭐，MIT）—— 电影感/概念片最强约束**

- 7 条 hard rules + 30 秒交稿 checklist，**不通过不交**：禁空泛形容词（cinematic/epic/4K 都要换成具体相机+镜头型号）、必须写 breathing 句、必须写 sound 行、至少 2 个瑕疵描述、结尾不许堆特效、禁 IP 名 + 每模型建议。
- 8 个模型的差异化建议（Seedance/可灵/Veo/海螺/Wan/Runway/Pika/Sora）精确到「负面词有没有专属字段」「单次时长」「IP 过滤严格程度」，这一条就甩开大多数合集。
- 29 个题材模板 + 6 个完整成品示例 + LLM-judge evals + CI。

**它们的真实短板（实测发现）**：
- 两个都**不产出内容结构**。你给它们一条新闻，它们给你画面提示词；但「15 秒里讲哪三个信息点、口播说什么」它们不管。
- `shortfilm-prompt` 的 29 个模板**全是电影感题材**（变形/催泪/广告/恐怖/微短剧/武侠…），**没有「资讯/新闻/B-roll」题材**。用它做新闻片，会得到一条成本很高、但跟新闻无关的电影感短片。
- 所以 B 的正确用法：**A 定内容 → B 只做画面**。

---

## 3. 实测对比（同一新闻、同一任务）

### 3.1 测试设计

| 项 | 内容 |
|---|---|
| 输入 | 同一条新闻（`research/tests/input-news-01.md`），MiniMax M3.1 Flash 发布 |
| A 任务 | 产出「可直接发的小红书图文笔记 + 抖音口播稿」 |
| B 任务 | 产出「可直接粘进视频模型的中文提示词（15–20 秒）」 |
| 执行方式 | 把每个 skill 的 `SKILL.md` 当指令严格执行（Step 1→N），保留全部产出与自检记录 |
| 评分 | 4 维各 1–5：**指令可执行度** / **产出可用度** / **中文适配** / **无需返工**（5=不用改） |

### 3.2 评分总表

| Skill | Star | 指令可执行度 | 产出可用度 | 中文适配 | 无需返工 | 均分 | 实测文件夹 |
|---|---|---|---|---|---|---|---|
| `cn-skills`（小红书+抖音） | 1 | **5** | **4** | **5** | 4.5 | **4.6** | `research/tests/cn-skills/` |
| `xhs-image-text-generator` | 28 | 5 | 4 | 5 | 4 | **4.5** | `research/tests/xhs-image-text-generator/` |
| `shuorenhua`（终检） | 2184 | 5 | 4.5 | 5 | **5** | **4.9** | `research/tests/shuorenhua/` |
| `lanshu-video-kit` | 424 | 5 | **4.5** | 5 | 4.5 | **4.75** | `research/tests/lanshu-video-kit/` |
| `shortfilm-prompt` | 476 | 5 | 3.5 | 3 | 3 | **3.6** | `research/tests/shortfilm-prompt/` |
| `guizang-social-card` | 7596 | 5 | 3 | 5 | 3 | **4.0** | `research/tests/guizang-social-card/` |
| `vivy-yi/xiaohongshu-skills` | 493 | **1** | **1** | 3 | **1** | **1.5** | `research/tests/vivy-yi-xiaohongshu-skills/` |

**注意**：这张表不是「谁比谁强」的单一排名——A 类（前 3 行 + guizang）和 B 类（lanshu / shortfilm）做的不是同一件事；`shuorenhua` 是插件不是主笔。

### 3.3 同一新闻，产出的真实差异

**A 类（小红书 / 抖音）**

| | `cn-skills` | `xhs-image-text-generator` |
|---|---|---|
| 交付物 | 标题 3 个 + 封面文案 + 正文（466 字）+ 标签 8 个；另出抖音口播（178 字≈40 秒）+ 6 行分镜表 | 8 页 carousel.json + cards.html + caption（507 字）+ 标签 16 个 + 5 条 FAQ 评论 + 6 维评分 |
| 可执行度差异 | 只给规则，产出靠模型自觉 | 有脚本与校验：**我漏填 manifest 占位符时被 `validate_delivery.py` 直接判 FAIL**，修完才 PASS |
| 事实严谨性 | 无「不编造」约束（但它没编） | 每页带 `source_note`，并要求在成品里明示「许可证未公布 / 1M 上下文是第三方转述」 |
| 真实缺陷 | 无长度/结构校验；标签无大小搭配说明 | 需要生图模型；标题生成 10 个偏多；正文没有「去 AI 味」环节 |

**结论：两者互补 > 二选一。** 要「能直接发且敢发」，用 `xhs-image-text-generator` 定结构，用 `cn-skills` 的规则校一遍文案，再用 `shuorenhua` 过一遍语气。要「只发文案不配图」，`cn-skills` 就够。

**B 类（视频提示词）**

| | `lanshu-video-kit` | `shortfilm-prompt` |
|---|---|---|
| 选型 | 先跑 `model-selector`：中文 + 竖屏 + 15s + 国内 → **即梦 3.0 主选 / Seedance 2.0 备选** | 跳过选型，默认电影感 |
| 产出 | 3 镜头竖屏分镜（每镜 4 维：运镜/动作表情/位置/音频）+ 全量约束词 + 每模型替换建议 | 20 秒 4 镜头 5-stage 完整 prompt（含 Sony Venice + Canon K-35 / 35mm f/2.0 等具体参数）+ 负面词预置包 + 每模型时长与负面词字段建议 |
| 直接可用性 | **可直接粘进即梦 3.0** | **可直接粘进 Veo/Sora/Kling**，但题材是电影感叙事，不是新闻片 |
| 真实缺陷 | 不写口播文案，不知内容讲什么 | 模板库无资讯题材；英文 canonical（中文是译本） |

**结论：做「AI 新闻短视频」这类内容，用 `lanshu` 更贴（中文原生、国内模型、有选型路由）；做「品牌片/概念片/情绪片」，用 `shortfilm-prompt` 更专业。**

### 3.4 guizang 的实测（配图层）

- 按 SKILL.md 的 4.5 步**不许手写 HTML，复制 `assets/template-swiss-card.html`**，只替换 `<!-- POSTERS_HERE -->`。
- 产出 3 张 1080×1440 Swiss card（封面 S01 / 数据 S03 / 陷阱 S05），脚本校验：使用 25 个 class **全部存在于模板 CSS**；硬规则（单一 accent、无圆角/阴影/渐变、large-the-larger 字重、中文标题 ≤28 字）全过。
- **但沙箱内无法运行浏览器**（Chrome headless 被拦截、`qlmanage` 报 `sandbox initialization failed`），所以无法输出最终 PNG。**纯视觉 skill 拿不到最终图，就只验证了一半**——这点必须诚实计入评分（可用度 3 分）。

### 3.5 真实产出的证据（各取一段）

- 小红书正文（`cn-skills` 产出，466 字、emoji 3 个、无 Markdown 加粗、标签 8 个）：
  > 先说结论：MiniMax 新发的 M3.1 Flash，成本只有上代 1/3，速度快 3 倍，还限时免费。🫠
  > 跑长任务的人应该都懂，模型越聪明越贵，账单是实打实的。这次它把价格拉到了输入 1 元/百万 token，输出 4 元/百万 token。
- 抖音口播（`cn-skills` 产出，178 字≈40 秒，黄金 3 秒 + 6 行分镜表）：
  > 一个连名字都不敢露的模型，在海外免费榜霸榜 10 天，今天终于公布真身了。
- 视频提示词（`lanshu` 产出，即梦 3.0 可直接用）：
  > 镜头 1：固定机位中景，一个年轻程序员坐在深夜的工位前……他先是盯着屏幕停顿，随后手指在键盘上敲了两下又停住，眉头轻微皱起……
- 视频提示词（`shortfilm-prompt` 产出，5-stage + 7 rules 自检全过）：
  > Shot on Sony Venice + Canon K-35 series, 35mm, f/2.0…… Handheld shot. Throughout, maintain an extremely subtle, breath-like camera float to enhance presence.
- 去 AI 味前后（`shuorenhua`）：466 字 → 448 字，删掉「先说结论：」「更戏剧的是」「今天官方才摊牌」等 8 处渲染性表达，**14 个数字/版本/条件全部原位保留**。

---

## 4. 「不建议用」清单（指名道姓 + 证据）

### 4.1 `vivy-yi/xiaohongshu-skills`（493⭐，139 个 SKILL.md）—— 最典型的「多 ≠ 好」

- **无 LICENSE 文件**：法律上不可复用，这一条就足以淘汰。
- **139 个 skill 全是 SEO 长文模板**：`copywriting-skills/SKILL.md` 的「Implementation」全部内容是「Hook 用『你还在…吗?』/ 加 emoji 💖✨🔥 / be enthusiastic: OMG、绝绝子、真香 / 说『真的感动哭了』」。这不是流程，是**用文案解释文案**。
- 它的 `Before/After` 是「❌ 这个产品很好用 → ✅ OMG姐妹们！」，属于示例对照，**没有输入输出契约、没有平台格式规则（不知道小红书不渲染 Markdown、不知道标题 ≤20 字）、没有交付物定义**。
- 实测产出必带编造体验（「我最近用了」「花了冤枉钱」），SKILL 里没有任何「不得编造」约束。
- 语气错配：美妆号语气直接套 AI 工具内容，等于自杀。
- 评分：可执行 1 / 可用 1 / 中文 3 / 返工 1。

### 4.2 `redfox-data/redfox-community`（447⭐，132 个 SKILL.md）—— 伪装成 skill 的商业引流

- **无 LICENSE**（仓库根目录没有 LICENSE 文件）。
- 132 个 SKILL.md 里 **130 个**引用它自家 `redfox.hk` 的 API Key（`skills/video-prompt-expert/SKILL.md` 第 60–68 行：「使用本技能前，请确保已配置 API Key → 访问红狐Hub 注册 → 个人中心获取 `ak_xxx`」）。
- 所谓「视频提示词专家」本质是「在自己平台上跑一次生成」，离开它的付费 API 就没有价值。
- 这不是 skill，是**给自家产品导流的 README 集合**。

### 4.3 `wenziai/wenzi-xiaohongshu-workflow`（175⭐）—— 内容不错，但无 license

- 6 个 skill 的真号运营方法论确实扎实（有 50 万阅读的真实截图、有「先诊断再改写」的硬规则）。
- 但**仓库没有 LICENSE**，默认「保留所有权利」。用户要拿去运营自己的账号、还可能商用——**合规风险 > 内容收益**，直接淘汰，不冒这个险。

### 4.4 `Wayhhow/ai-video-shot-prompt-skill`（16⭐）—— 工程好，但社区验证不足

- 有 `validate_prompt.py` 结构自检 + 6 个测试文件 + 10 篇 references，工程质量其实高于很多 400⭐ 仓库。
- 但 16⭐、last push 2026-09-06、GitHub 识别的 license 是 `NOASSERTION`（文件里写 MIT 但声明不一致）。按「社区认可」的硬指标不达标，且许可存疑，**不建议直接投产**；可以当「怎么写好提示词 skill」的参考。

### 4.5 `shuhaolin63-hash/GuoFanDirector_Skills`（7⭐）

- 7⭐、无 issue 讨论、克隆下来 112MB（异常大），内容未能完整取到。无法验证「有没有真 SKILL.md 工作流」，按宁缺毋滥淘汰。

### 4.6 `anthropics/skills`（18.2 万⭐）—— 官方，但不管这件事

- 19 个技能：`docx/pdf/pptx/xlsx`（文档）、`frontend-design`、`mcp-builder`、`skill-creator`、`brand-guidelines`、`internal-comms`、`doc-coauthoring`、`webapp-testing` 等。
- **没有一个覆盖小红书/抖音/短视频脚本/视频提示词**。最接近的 `internal-comms` 是企业内部沟通写作，`doc-coauthoring` 是文档合写。
- 这是一个有价值的负面结论：**别把「官方仓库」当「什么都有」**。写中文平台内容，官方仓库帮不上。

---

## 5. 提示词方法论：用官方指南当尺子

用户要的「视频提示词」是 B 类，而 B 类水最深（大量「提示词合集」冒充 skill）。我用两份官方指南做尺子，结论是：**能通过这把尺子的社区 skill 只有 `lanshu` 和 `shortfilm-prompt`**。

### 5.1 官方尺子说了什么

**[Google Veo 提示词指南](https://ai.google.dev/gemini-api/docs/veo?lang=zh-cn#prompt_guide)**
- Veo 3.1 单次 8 秒，720p/1080p/4K，**原生音频**；竖屏 9:16 可选；可续写、可首尾帧、可用最多 3 张参考图。
- 提示词要覆盖：主体 + 动作 + 风格 + 相机 + 构图 + 氛围 + 音频；负面词走**独立字段**，不要在字段里写 `no...` 命令句。

**[OpenAI Sora 2 提示词指南](https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide.md)**
- 「像给一个从没看过你分镜的摄影师下 brief」；分辨率/时长/角色引用只能走 API 参数，**不能写在 prompt 里**。
- 关键原则：**每个镜头只要一个清晰的相机运动 + 一个清晰的主体动作**；动作要用「节拍/步数」描述（「走三步到窗边，停住，最后一秒拉窗帘」优于「走过房间」）。
- 用 weak/strong 对照：`"beautiful street at night"` → `"wet asphalt, zebra crosswalk, neon signs reflecting in puddles"`；`"cinematic look"` → `"anamorphic 2.0x lens, shallow DOF, volumetric light"`。
- 对白放 `<dialogue>` 块；**Sora 没有负面词字段**，否定要折进正向描述。
- 详细模板：Format & Look / Lenses & Filtration / Grade & Palette / Lighting & Atmosphere / Location & Framing / Wardrobe / Sound / Optimized Shot List（带时间码与 Purpose）。

### 5.2 用这把尺子筛社区 skill 的 5 个问题

1. 它有没有说清**每个模型不能做什么**（时长上限、负面词字段、IP 过滤、能否出音频）？→ `shortfilm-prompt` 逐模型写了，`lanshu` 有 model-selector 矩阵，**vivy / redfox 没有**。
2. 它有没有**禁止空泛形容词**、要求具体相机/镜头/光位？→ 只有 `shortfilm-prompt` 把它写成 hard rule。
3. 它有没有说「**一个镜头一个运镜**」？→ `lanshu`（分镜时序）、`shortfilm-prompt`（Rule）都有；这与 Sora 官方一致。
4. 它给的是**模板 + 约束**，还是**一堆成品 prompt 让你抄**？→ 抄 prompt 的（redfox 594 条、lanshu 594 条也是抄，但 lanshu 额外给了 methodology 与生成流程；redfox 只给你抄 + 付费生成）。
5. 它的 license 和 commit 能不能查？→ 查不了的一律不进 TOP。

**结论（对 Lead 的回应）**：B 类不是「整体不行」，而是**两极分化**：顶部 2 个（lanshu / shortfilm）质量过硬、能通过官方尺子；腰部和底部全是「提示词合集 + 引流」。**不需要我们从头封装**——除非用户要的是「AI 新闻解说」这种特定题材（这两个仓库都不覆盖），那时才值得基于官方指南自建一个 `news-explainer-prompt` skill。

---

## 6. 给用户的安装与使用建议

### 6.1 已装好的东西

```
skills/
├── cn-skills/                    # LLL-178：xiaohongshu-post + douyin-script（1⭐, MIT）
├── xhs-image-text-generator/     # sanqi：小红书图文交付管线（28⭐, MIT）
├── shuorenhua/                   # MrGeDiao：去 AI 味终检（2184⭐, MIT）
├── guizang-social-card/          # op7418：卡片/封面配图（7596⭐, AGPL-3.0）
├── shortfilm-prompt/             # jnMetaCode：电影感视频提示词（476⭐, MIT）
├── lanshu-video-kit/             # cclank：中文视频提示词全家桶（424⭐, MIT）
└── aihot/                        # 另一位同事的，我没动
```

每个目录旁都有 `provenance.md`（URL / star + 查证时间 / license / commit hash / 选它的理由 / 已知局限）。
**安装方式全部是 `git clone --depth 1` + 拷贝，没有任何写 `$HOME` 的安装器**，可随时删除。

### 6.2 推荐工作流（一条 AI 新闻 → 全平台内容）

```
AIHOT 事件 markdown（已有 data 脚本）
   │
   ├─ A1 小红书图文：
   │    xhs-image-text-generator（定 8 页结构 + 交付包 + 自检）
   │      → cn-skills/xiaohongshu-post 的规则校标题/正文/标签
   │      → shuorenhua 去 AI 味（minimal 模式，别让它改事实）
   │      → guizang-social-card 出卡片（需要图时）
   │
   ├─ A2 抖音口播：
   │    cn-skills/douyin-script（黄金 3 秒 + 240-280 字/分钟 + 分镜表）
   │      → shuorenhua 过一遍
   │
   └─ B 视频提示词：
        lanshu-video-kit（model-selector 选模型 → seedance-storyboard 出分镜提示词）
          └─ 想要电影感时换 shortfilm-prompt（它约束更硬，但题材是概念片）
```

### 6.3 给用户的三条使用纪律

1. **A 和 B 不要混着用**：视频提示词 skill 不会帮你决定「这条新闻讲什么」。先让 A 定内容结构，再让 B 写画面。
2. **凡是没有 license 的（vivy、redfox、wenziai）一律别装进生产流程**——尤其 wenziai 内容其实不错，但无 license 就意味着你不可复用、不可分发。
3. **任何 AI 文案发布前必须人工过一遍事实**：这次的新闻里就有两处坑（许可证未公布、1M 上下文是第三方转述），好 skill 会把它们写进「避坑页」，烂 skill 会把它们写成确定事实。

### 6.4 如果之后要自建 skill

`anthropics/skills` 的 `skill-creator` + `obra/superpowers` 的结构（frontmatter + 渐进式 references + 硬规则 + self-check）是范本；本次实测发现「好用」的四个必备件：
1. **输出契约**（文件名、字段、长度、格式）；
2. **硬约束**（≤20 字、≤8 个 emoji、每镜 1 运镜、禁 `**`）；
3. **自检**（脚本或 checklist，不通过不交）；
4. **模型路由**（哪个模型有什么限制）。

---

## 7. 附录

### 7.1 交付物索引

| 路径 | 内容 |
|---|---|
| `research/tests/input-news-01.md` | 统一测试输入（AIHOT 热点 No.01 事件全文） |
| `research/tests/xhs-image-text-generator/` | 发布方案 + 8 页 carousel + cards.html + 交付包（validator PASS）+ 实测记录 |
| `research/tests/cn-skills/` | 小红书笔记 + 抖音口播 + 分镜表 + 自检记录 |
| `research/tests/shuorenhua/` | 去 AI 味前后对照 + 改动清单 + 保真核对 |
| `research/tests/guizang-social-card/` | 3 张 Swiss 卡片 HTML + class 合规校验 + 实测记录 |
| `research/tests/lanshu-video-kit/` | 选型 + 3 镜分镜提示词 + 自检 + 模型适配建议 |
| `research/tests/shortfilm-prompt/` | 5-stage 完整 prompt + 7 rules 自检 + 模型适配 |
| `research/tests/vivy-yi-xiaohongshu-skills/` | 反面样本：实测产出 + 逐条问题证据 |
| `research/data/` | AIHOT API 原始响应（hot-topics / agent-hot / story 详情） |

### 7.2 环境限制（诚实声明）

- 沙箱**无法运行浏览器**：Chrome headless 被系统拦截（`Trace/BPT trap: 5`），`qlmanage` 报 `sandbox initialization failed`。因此 guizang / sanqi 的**最终 PNG 生成未能验证**，只交付 HTML + 结构校验。
- 沙箱内**没有生图模型**：`image-prompts.md` 里的提示词未经真实出图验证。
- 没有安装 Pillow（pip 写入 `$HOME` 会被沙箱拒绝），所以 `validate_delivery.py` 走的是 `--allow-html` 分支（skill 明文允许）。
- GitHub Search API 未认证配额 10 次/分钟，部分候选（Hao0321、liangdabiao）未能查证元数据，已标「未查证」而非「推荐」。

### 7.3 评分口径

- **指令可执行度**：SKILL.md 是否给出可照做的步骤、产物定义、约束；能不能被另一个模型机械执行。
- **产出可用度**：产出能否直接发/直接用；需要多少人工判断。
- **中文适配**：是否为中文平台设计（字数、标点、不渲染 Markdown、emoji、语气、模型中文能力）。
- **无需返工**：按产出质量扣分，越少人改越高。5 分 = 直接发，1 分 = 全部重写。
