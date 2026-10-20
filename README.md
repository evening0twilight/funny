# AI 资讯 → 小红书 / 抖音：一条能持续跑的 content pipeline

> 目标：把 aihot.news 上的 AI 新闻，变成你能直接发的小红书图文、抖音口播稿、以及能喂给即梦/可灵/Veo/Sora 的视频提示词。
> 结论：**能跑通，但不是"装个 skill 就自动出稿"。** 真正有价值的是「数据层 + 选对的 skill + 事实核验」这条链，skill 只是中间那段。

---

## 0. 先说结论（30 秒版）

| 问题 | 答案 |
|---|---|
| aihot.news 能拿来做内容吗 | 能，它自带匿名只读 REST API + 官方 Agent Skill，**不用爬虫**。个人非商业运营免费 |
| 有没有能直接用的社区 skill | 有，但**不是 star 最高的那些**。最高星的几个要么不是文案 skill，要么是伪装成 skill 的引流 |
| skill 实际能力如何 | 小红书图文 80%、抖音口播 85% 可用（跑完要人工核事实）；**视频提示词不能指望 skill 自动出片**，它只给画面，内容结构得自己定 |
| AI 能直接出稿就发吗 | **不能。** 见 [§7 发布纪律](#7-发布纪律必须看)。我们实测的一条稿子被对抗审校挑出 8 个 P0，其中「AI 生成标识」和「导流话术」是会限流/违规的 |
| 最重要的认知 | **这是整活号，不是资讯号**。先让人停下来，再谈信息——所以 skill 里有一层「梗引擎」专门管注意力 |
| 最值得投入的地方 | 不是找更多 skill，是**选梗**和**事实核验**。格式活已经被脚本干掉了 |

---

## 1. 数据源：aihot.news 怎么用（已封装好）

站点自带三种接入方式，我们用 REST API v1（匿名、只读、无需 Key）：

```bash
python3 tools/aihot_fetch.py hot          # 当前热点 Top10（含摘要/最新进展/信源）
python3 tools/aihot_fetch.py daily        # 今日 AI 日报
python3 tools/aihot_fetch.py items --limit 50 --mode all --window 7d
python3 tools/aihot_fetch.py story 589d286a-2a6d-48be-b14a-e61390534ec3   # 事件全貌

python3 tools/topic_score.py --profile news   # 选题打分（见 §5）
```

**做内容最值钱的不是「今天有什么新闻」，是这三样：**

| 字段 | 在哪 | 为什么值钱 |
|---|---|---|
| `digest`（AI 综述） | `story/{uuid}` | 一条事件 700 字左右的完整来龙去脉，省掉你读 18 条报道 |
| `reports[]`（报道时间线 + `firstParty`） | 同上 | 能区分「官方首发」和「第三方转述」——**这是做内容不翻车的核心** |
| `latest`（最新进展） | 同上 | 事件还在发酵时，这就是你比同行快半步的信息差 |

> ⚠️ 许可：个人非商业、公益非商业、组织内部使用免费；**对外商业产品、客户交付、数据转售、公开镜像需事先书面授权**（wzglyay@virxact.com，[terms](https://aihot.news/terms)）。做个人号没事，接商单/做付费社群前先确认。

---

## 2. Skills 选型结论（社区认可度 + 实测）

完整报告见 [research/skills-report.md](research/skills-report.md)（7 个 skill 同一新闻实测 + 打分 + 淘汰理由）。

### 推荐组合（不是单个 skill，是一条链）

| 环节 | Skill | Star | 许可 | 实测分 | 说明 |
|---|---|---|---|---|---|
| 小红书图文 | [cn-skills](https://github.com/LLL-178/cn-skills) 的 `xiaohongshu-post` | 1 ⭐ | MIT | 4.6 | **规则最像行家**：标题≤20 字、正文 300–800 字、禁 `**`（小红书不渲染）、emoji 限量、标签 5–8 |
| 抖音口播 | 同仓库 `douyin-script` | 1 ⭐ | MIT | 4.6 | 唯一同时覆盖图文+口播的；语速 240–280 字/分钟折算时长、每句≤15 字 |
| 去 AI 味终检 | [shuorenhua](https://github.com/MrGeDiao/shuorenhua) | 2184 ⭐ | MIT | 4.9 | 唯一带公开评测（123 cases）的中文写作 skill，删套话但保住数字与限定词 |
| 交付管线（可选） | [xhs-image-text-generator](https://github.com/sanqi-cd/Sanqi-Skills) | 28 ⭐ | MIT | 4.5 | 带脚本+校验器，实跑时真的 `FAIL` 抓到我漏填的占位符 |
| 小红书卡片图（可选） | [guizang-social-card](https://github.com/op7418/guizang-social-card-skill) | 7596 ⭐ | AGPL-3.0 | 4.0 | 中文社区最星，但它是**配图** skill 不是文案 skill；AGPL 注意 |
| 视频提示词 | [lanshu-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) | 424 ⭐ | MIT | 4.75 | 中文原生，覆盖即梦/可灵/Seedance，有运镜词典+约束词清单+分镜时序 |
| 电影感/概念片 | [shortfilm-prompt](https://github.com/jnMetaCode/ai-shortfilm-prompts) | 476 ⭐ | MIT | 3.6 | 7 条 hard rules，但 29 个模板全是电影题材，**不覆盖资讯** |

**一句话：真正能打的是「把约束写死、能自检」的小仓库，不是 star 最高的。**

### 不建议用（指名道姓）

| Skill | Star | 问题 |
|---|---|---|
| `vivy-yi/xiaohongshu-skills` | 493 ⭐ | 139 个 SKILL.md，实测 1.5 分。产出全是「绝绝子/感动哭了」的美妆号语气，还编造使用体验，无 license |
| `redfox-data/redfox-community` | 447 ⭐ | 132 个 SKILL 里 **130 个要求你注册充值它自家 API**，无 license。伪装成 skill 的商业引流 |
| `anthropics/skills` | 18.2 万 ⭐ | 官方、质量高，但**一个中文平台内容技能都没有**（它做 docx/xlsx/pptx/前端） |

### 2.1 所以我们把三个 skill 合并重构成了一个：`ai-news-content`

装三个 skill 来回切太累，而且各有一个硬伤：cn-skills 不懂 AI 新闻、shuorenhua 只能改稿不能写稿、lanshu 按模型厂 API 写而你在 **arcloop.ai** 手动生成。

`skills/ai-news-content/` 是合并后的产物，一条命令跑完整链路：

```
输入（AIHOT / 任意 URL / 本地文件 / 粘贴）
  → prep_input.py 归一成素材卡（facts 带 official/first-party/third-party/unverified 四档）
  → 选题判断 → 写文案（小红书/抖音/快讯）
  → 视觉（生图 / 视频提示词，按 arcloop 真实模型写）
  → check_copy.py 机器自检（标题/字数/emoji/标签/AI 腔/绝对化/导流/AI 标识/数字溯源）
```

| 吸收了什么 | 来自 |
|---|---|
| 标题≤20 字、正文 300–800、emoji≤8、标签 5–8、语速 240–280、每句≤15 字 | cn-skills |
| 「保住事实与数字，只做减法」的去 AI 味逻辑 | shuorenhua |
| 图生视频只描述运动、每镜一运镜、显式端点 | lanshu-video-kit |

**修掉的**：只能吃固定来源、没有事实分层、没有合规环节、提示词按模型厂 API 写、没有自检。
详见 [skills/ai-news-content/README.md](skills/ai-news-content/README.md)。

---

## 3. 实测证据：两条真实内容，从数据到成品

### 3.1 资讯型：MiniMax M3.1 Flash 发布（热点 No.1）

```
out/2026-10-20/minimax-m31f/          # v2，已按对抗审校修完 8 条 P0
├── 00-选题卡.md        # 选题、受众、爆点、3 个标题（16/19/15 字）
├── 01-小红书图文.md    # 773 字符 / 379 汉字 / 0 个 `**` / 3 emoji / 7 标签
├── 02-抖音口播分镜.md  # 142 字 = 35.5 秒 @240 字/分，成片 40 秒（8×5s，零慢放）
├── 03-视频提示词.md    # 8 镜 × 5s，竖屏 9:16，四平台版本 + 负面词
├── 04-事实核验.md      # 25 条逐条核验、7 个风险、11 条红线 + 合规章
├── 05-溯源.md          # 哪个环节由哪个 skill 产出、改了什么、为什么改
└── 06-审校报告.md      # 对抗式审校：8 条 P0（这份最值得看）
```

这条链真实跑下来的样子：

1. `aihot_fetch.py story` 拿到 700 字 AI 综述 + 18 条报道时间线
2. cn-skills 出小红书稿 → 硬约束由 SKILL.md 写死，我用脚本复核：标题字数、正文长度、`**` 数量全部对得上
3. shuorenhua 过一遍去掉翻译腔和套话（05-溯源 里有终检前后 9 处对比）
4. lanshu 的 `kling-prompter` / `seedance-storyboard` 出 8 镜提示词
5. **对抗式审校**——这一步才决定能不能发

> 我们专门派了个「刻薄编辑」做独立审校，第一版结论是**不能直接发**，挑出 8 个 P0：人民币价格只在 AIHOT 综述里有、41 秒口播配 28 秒素材要 2.33x 慢放（还撞了自己写的 `no slow motion`）、AI 生成标识缺失、站外导流违规、S3 的「1/3」和「19%」自相矛盾……
> 第二版全部修完并复核通过。**这不是 skill 的失败，是流水线该有的环节**：能自动化的已经自动化，剩下的是判断。

### 3.2 预测型：Codex 额度重置，下一次窗口在哪

```
out/2026-10-20/codex-reset-predict/
├── 00-选题卡.md            # 为什么预测型内容值得做（完播/互动逻辑）
├── 01-小红书图文.md        # 标题 17 字，2 emoji，6 标签，全篇带条件词
├── 02-抖音口播分镜.md      # 25–35 秒
├── 03-视频提示词.md        # 5 镜，冷色电子钟/时间轴
└── 04-预测依据与免责.md    # 推算过程 + 免责句 + 「没重置怎么办」
```

这条是**另一种内容形态**，也是「Tibo 预告通知」的正确用法：与其做监控工具，不如把三次重置的确认时间（10/13 13:06、10/15 12:55、10/18 05:12）和间隔（47h49m、64h17m）做成一条**可对答案的预测**。

- 推算过程全部落在 `04`，每个推测句都带「按…推算」「如果」「大概率」
- 结尾留了可验证钩子（今晚回来对答案）——这是预测型内容涨粉的关键
- 我们复核过：稿子里引用的 Tibo 原话（「你想得美」「做点小卡片发给大家」）全部能在 `data/raw/2026-10-20/codex-resets.json` 里查到，没有编造

**这类内容的价值：** 重置是不可控的事件，但「什么时候会重置」是可控的选题。预测对了涨信任，预测错了也是互动——前提是**必须明说是预测**。

---

## 4. 目录结构

> **接手这个项目先读三份**：[CONVENTIONS.md](CONVENTIONS.md)（规则）→ [docs/daily-sop.md](docs/daily-sop.md)（每天怎么干）→ [docs/handoff.md](docs/handoff.md)（现状与待办）。
> **一天一个内容文件夹**：当天所有文案/梗卡/提示词都在 `out/YYYY-MM-DD/`。

```
funny/
├── CONVENTIONS.md             # ★ 项目规则（一天一文件夹、防串日、协作边界）
├── docs/
│   ├── daily-sop.md           # 每日流程
│   └── handoff.md             # 交接说明
├── tools/
│   ├── aihot_fetch.py        # 数据层：hot/daily/items/story/agent-hot/agent-latest
│   ├── topic_score.py        # 选题打分：10 条热点 → 该做哪 2 条
│   ├── new_day.py            # 新建一天的工作区（开工第一步）
│   ├── doctor.py             # 全项目体检（收工/提交前）
│   └── README.md             # 字段说明、限流、缓存
├── skills/
│   ├── ai-news-content/      # ★ 自研合并 skill：一条新闻 → 五种成品（先看这个）
│   ├── aihot/                # AIHOT 官方 Skill（问答式查新闻）
│   ├── cn-skills/            # 小红书 + 抖音文案主笔
│   ├── shuorenhua/           # 去 AI 味终检
│   ├── lanshu-video-kit/     # 视频提示词（即梦/可灵/Seedance）
│   ├── shortfilm-prompt/     # 电影感备选
│   ├── xhs-image-text-generator/
│   └── guizang-social-card/   # 以上 7 个是社区原版，留作对照与备选
├── data/raw/2026-10-20/      # 当天真实抓取数据（热点/日报/事件/重置记录）
├── research/
│   ├── skills-report.md      # 选型报告（7 个 skill 实测对比 + 淘汰理由）
│   └── tests/                # 每个 skill 的原始实测产出
├── out/                      # 成品包（可直接复制发布）
│   ├── 2026-10-20-minimax-m31f/        # 资讯型（v2 已过审校）
│   ├── 2026-10-20-codex-reset-predict/ # 预测型
│   └── v2-skill-tests/                 # 新 skill 的三篇实测
└── README.md                 # 你正在看的这份
```

---

## 5. 每天怎么干（30 分钟的 SOP）

```bash
# 0. 开工：建当天目录（第一步永远是它）
python3 tools/new_day.py

# 1. 取数（10 秒）
python3 tools/aihot_fetch.py hot --save data/raw/$(date +%F)/hot-topics.json

# 2. 选题：10 条里筛 2 条（1 分钟）
python3 tools/topic_score.py --profile news     # 资讯号
python3 tools/topic_score.py --profile tool     # 工具号
python3 tools/topic_score.py --profile opinion  # 观点号
```

打分器把「短视频可做性」拆成 5 个维度（热度 30% / 冲突 25% / 实用 25% / 受众 10% / 可视化 10%），并直接给内容形态建议。
**同一批新闻，工具号和资讯号该做的完全不同**——所以有 `--profile`：

- 工具号（`--profile tool`）今天该做「DeepSeek 发布 V4.1-Flash-1017」（实用分 100）
- 资讯号（`--profile news`）今天该做「美国土安全部令移除 DeepSeek」（冲突分 100，完播率高）

```bash
# 3. 拿素材（事件全貌，不是单条快讯）
python3 tools/aihot_fetch.py story <publicId>

# 4. 归一素材（自动抽 facts / numbers / quotes，带来源分层）
python3 skills/ai-news-content/scripts/prep_input.py --aihot-story <publicId> --out material.json

# 5. 出稿：让 Claude/Codex 加载 skills/ai-news-content/SKILL.md 按流程写
#    （也能吃任意来源：--url https://...  或  pbpaste | --file -）

# 6. 机器自检（全绿才发）
python3 skills/ai-news-content/scripts/check_copy.py 稿件.md --material material.json

# 7. 收工：体检 + 提交
python3 tools/doctor.py
git add -A && git commit -m "data: <今天> <一句话>" && git push
```

---

## 6. 视频 / 生图怎么用（arcloop 版，这是最容易白干的地方）

**你在 arcloop.ai 上手动生成，不调模型厂 API**，所以提示词必须按 arcloop 的真实模型和参数写。

### 三件反直觉的事（不知道就会废掉一半提示词）

1. **arcloop 没有独立的「负面词」输入框**。负面约束必须写成提示词的最后一段，不写等于没写
2. **3:4 图片比例在图片侧不支持**（只在视频侧有）。小红书 3:4 卡片 = 按 9:16 出图后裁掉上下
3. **图片模型会自作主张加中文**。官方实测：GPT Image 2.5 Sunburst 擅自加了没审批过的标语。所以默认走「无字底图 + 后期加字」

### 模型怎么选

| 做什么 | 用哪个 | 关键参数 |
|---|---|---|
| 中文卡片 / 封面 | **GPT Image 2.5 Sunburst** | 9:16 / 2K；文字排版官方评级 Excellent |
| 密集信息图（要拆图层改） | **Seedream 5 Pro** | 支持图层拆分、空间标注改图 |
| 30 秒资讯短片一条过 | **Seedance 2.5** | 单次 30s，唯一能一口气 30s |
| 主镜头 4K / 多镜头一次出 | **Seedance 2.5** | — |
| 首帧图 → 动起来 | **Vidu Q4 Preview (i2v)** | 1 张起始帧，比例跟图 |
| 首帧 + 尾帧指定 | **MiniMax H3 Max Turbo** | **唯一**支持尾帧 |
| 快速试错 / 二次编辑 | **MiniMax H3** | 便宜快 |
| 口播 / 旁白 | **Seed Audio 1.0** | ≤2 分钟，支持中文 |

### 四条纪律

1. **短镜不写死秒数**（5–10s 镜头在下拉框选时长）；但 Seedance 2.5 一次出 30s 时，官方示例允许写 `0-8s / 8-18s` 分段
2. **每镜只给一种运镜**，每镜必须有**显式端点**（`then comes to rest`），防生成到一半卡住
3. **画面零文字**。数字、平台名、中文标题全部后期贴
4. **风格词要具体**：写「磨砂玻璃 + 阳极氧化铝 + 5600K 柔光箱」，不要写「电影级光影」「史诗感」

完整模板见 [references/05-video-prompts.md](skills/ai-news-content/references/05-video-prompts.md) 和 [arcloop-models.md](skills/ai-news-content/references/arcloop-models.md)。

---

## 7. 发布纪律（必须看）

| 项 | 规则 | 为什么 |
|---|---|---|
| **AI 生成标识** | 全 AI 生成画面必须显著标识（角标「本视频含 AI 生成画面」+ 平台声明） | 《人工智能生成合成内容标识办法》2025-09-01 已施行，不标是硬违规 |
| **事实核验** | 每个数字回查 `story` JSON；区分「官方首发」和「第三方转述」 | 这条链的最大翻车点。实测稿子里「许可证未公布」是缺席推断、「1M 上下文」是第三方转述，写错就是造谣 |
| **不带导流** | 小红书别写「评论区扣 1 领入口」，改成站内互动 | 站外导流明确违规，轻则限流重则封号 |
| **标注冲突** | 同一件事两个来源数字打架时，写「两个口径」而不是选一个 | 我们实测遇到官方「成本 1/3」vs 第三方「定价一半」 |
| **别写使用体感** | 「我用了三个月」「实测爽到」——你没用就别写 | 资讯号掉粉最快的方式，被评论区抓到一次就完了 |

---

## 8. 已知局限（诚实说）

- **视频提示词只产画面，不产内容结构**。「15 秒讲哪三个信息点」得靠你自己或先用文案 skill 定好
- 两个视频 skill 都**没有资讯/新闻题材模板**（shortfilm 的 29 个模板全是电影题材）。做新闻片得自己搭画面系统，`out/*/03-视频提示词.md` 里的那套「深蓝网格 + 数据条 + 数字牌」可以当模板复用
- **cn-skills 只有 1 个 star**。规则好不等于社区验证过，把它当你团队内部 SOP 用，别当行业标准
- 中文视频提示词赛道整体水很深，很多是「提示词合集」冒充 skill。我们只留下了 lanshu 和 shortfilm 两个有明确工程约束的
- AIHOT 的 `items` 只回溯 7 天，更早的历史搜索不保证
- `check_copy.py` 只能查「数字有没有出处」「格式对不对」，查不出「这句话是不是推断」和「语气像不像人话」——最终仍要人看
- 数字核验是 **token 比对**，能抓编造的数字，但抓不到**单位/语境错位**（素材卡有「100 万 token」，你写「100 元」照样过）——这一步必须人核
- arcloop 站点迭代快，模型页随时可能变；`arcloop-models.md` 标了核实日期（2026-10-20），用前先扫一眼生成器下拉框
- 自研 skill 的 02/03 平台参考是把 cn-skills 的规则重构过来的，cn-skills 本身只有 1 个 star——规则好用，但没经过大规模社区验证

---

*所有 skill 的 star 数与 commit 见各目录下 `provenance.md`（查证时间 2026-10-20）。*

*`ai-news-content` 经过两轮对抗审校：第一轮抓到 6 条执行卡点（已修），第二轮抓到 8 条 P0（检查器橡皮图章、标题不扫、`#` 截断正文、tier 语义混乱等，已修 7 条，剩余 1 条属工具边界并已在文档标明）。审校报告：[research/skill-review.md](research/skill-review.md)。*
