# arcloop.ai 能力规格书（提示词写作专用）

> 用途：本 skill 的所有图片/视频提示词都在 **arcloop.ai 网页上手动生成**（没有模型厂 API）。
> 所以本文件只记录「arcloop 生成器里真实存在的模型 + 真实能设的参数」，不写模型厂 API 参数。
>
> - 核实日期：**2026-10-20**（站点在快速迭代，参数随时可能变；每次开工先扫一眼生成器里的下拉框）
> - 核实口径：只采信 arcloop.ai 官方页面原文。**二手资料一律不用来断言参数**。
> - 凡本文件写「未公开」= 翻遍官方页面没找到，**不要猜、不要当成能力去写提示词**。
> - 价格/额度：**不写**。官方页面只有两处数字（见 §7），其余一律「未公开」。

> **修订记录**
> - **v2（2026-10-20）**：新增 §9（Kling 系列）与 §10（Canvas 工作流）；修正 §6 第 13 条——Kling 在 arcloop 上**可用**，此前「不为其写提示词」的判断有误。§1–§8 原有结论与来源保留。

---

## 1. 选型路由表（做什么内容 → 用哪个模型）

| 你要做的东西 | 首选模型 | 备选 / 备注 |
|---|---|---|
| 小红书封面图（中文大标题 + 人物/氛围） | **GPT Image 2.5 Sunburst** | 草稿用 Flare；中文标题让它写进图里，但必须逐字校对 |
| 单图「信息卡片」（中文标题 + 3~5 条要点） | **GPT Image 2.5 Sunburst**（文字排版强） | 密集信息图/多层海报/需要拆图层 → **Seedream 5 Pro** |
| 文字压不住的复杂中文排版 | **无字底图 + Canvas 加字**（GPT Image 2.5 Sunburst 出无字背景） | 官方推荐的两条路线之一，见 §5 |
| 一次出几十张封面变体 / 九宫格草图 | **Seedream 5 Lite** 或 **GPT Image 2.5 Flare** | 快、适合批量（积分成本官方未公开）；成片再换 Pro/Sunburst 重跑 |
| 改图（换背景/加元素/只改一处） | **GPT Image 2.5**（Sunburst 保细节 / Flare 求快） | 精确标注改图（点/框/箭头）→ **Seedream 5 Pro** |
| 把方图扩成 9:16 / 1:1 | **图片编辑 → 智能扩图**（不限模型） | 官方支持 1:1 / 16:9 / 9:16 / 4:3 |
| 30 秒资讯短片（一条过） | **Seedance 2.5**（单次 30s + 原生音频） | 只有它能一口气 30s；见 §3 |
| 8~15s 单镜头 / B-roll / 转场 | **Seedance 2.0**、**MiniMax H3**、**Vidu Q4 Preview** | 见 §3 的镜头级路由 |
| 已有封面图 → 让它动起来（图生视频） | **Vidu Q4 Preview（image-to-video）** | 比例跟随起始图；也可用 Seedance 2.5 以图作参考 |
| 需要「首帧 + 尾帧」 | **MiniMax H3 Max Turbo**（图生视频支持可选尾帧） | Vidu Q4 **明确不支持尾帧** |
| 便宜快速的试错草稿 | **MiniMax H3 Max** / **H3 Max Turbo** | Turbo **没有** reference-to-video，锁不住人物 |
| 多段拼接成 30s+ | 每段 ≤15s 的镜头（Seedance 2 / H3 / Vidu）+ Edit 时间线拼接 | Canvas/Storyboard 里每条 shot 是 1 次生成 |
| 口播 / 旁白 / 音效 / 环境声 | **Seed Audio 1.0**（单次 ≤2 分钟，支持中文） | 视频模型自带音频只到「场景音」级别 |
| 一次图 → 切九张 | **GPT Image 2.5 生成 3×3** → Canvas「切分图片」选 3×3 | 切出来的是低清面板，只适合分镜/预览 |

**镜头级路由（转写自官方 shot-type map）**
20–30s 连续表演 / 多镜头一次出 / 多人多资产 → Seedance 2.5；
音乐卡点 / 必须还原某张插画的近景 / 快速试错 → MiniMax H3；
最终 4K → Seedance 2.5；最终 2K 主镜头要脸准 → MiniMax H3。
来源：<https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5>

> **v2 补充**：上表「首帧+尾帧」只写了 H3 Max Turbo；**Kling 3.0 Omni 同样支持 Start & End Frames**，且多了「多镜头+元素配音+中文台词」这条整活刚需 → 见 **§9.3** 的选型对照。

---

## 2. 五个关键问题的直接答案

### Q1 单次能出几秒？30 秒要怎么拼？

| 模型 | 单次时长 | 来源 |
|---|---|---|
| Seedance 2.5 | **最长 30s**（模型页/对比页）；可延长；「长视频模式可达数分钟」；另有页面写「最长 50s」 | [model](https://arcloop.ai/models/en-US/seedance-2.5) · [对比](https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5) · [get-started](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style) |
| Seedance 2.0 | **最长 15s**（最高 4K） | [model](https://arcloop.ai/models/en-US/seedance-2) |
| MiniMax H3 | **4–15s** | [model](https://arcloop.ai/models/en-US/minimax-h3) |
| MiniMax H3 Max | **5–15s** | [model](https://arcloop.ai/models/en-US/minimax-h3-max) |
| MiniMax H3 Max Turbo | **5–15s** | [turbo](https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained) |
| Vidu Q4 Preview | **3–16s** | [model](https://arcloop.ai/models/en-US/vidu-q4) |

**结论**
- **30s = 1 次 Seedance 2.5**，或 **2 段 15s**（Seedance 2 / H3）拼，或 **2 段 16s**（Vidu）拼后剪掉 2s。
- 有没有 5s/10s 这种档位：**固定档位枚举未公开**。官方给的是一段连续区间（3–16 / 4–15 / 5–15），界面里按秒选；官网示例卡出现过的具体值是 **3s / 10s / 15s**，说明不是只有 5/10 两档。
- 想看真实可选项：打开生成器看 duration 控件，**不要**照本文件猜整数。

### Q2 9:16 竖屏怎么设？

| 位置 | 怎么设 | 来源 |
|---|---|---|
| **项目级（推荐）** | Story Brief 里选 **9:16**，之后该项目的每个 Episode、每张 shot card 自动继承 | [first-episode](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) · [vertical](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) |
| **单次生成** | 生成器里选 aspect ratio；或在提示词里显式写 `Vertical 9:16` / `framed vertically 9:16`（官方示例这么写） | [vertical](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) |
| **图片侧** | 图片生成器同样有「画面比例」；9:16 @2K、16:9 @2K 出现在官方示例卡里，1:1 出现在官方示例提示词内声明的设置中 | [六段式](https://arcloop.ai/handbook/en-US/six-block-prompt-structure-anti-drift) · [flare/sunburst](https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst) |

**各模型比例能力**
- **Seedance 2.5**：16:9 / **9:16** / 1:1 / 2.39:1（官方明列）→ [get-started](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style)
- **MiniMax H3 / H3 Max**：21:9 / 16:9 / 4:3 / 1:1 / **3:4** / **9:16** / auto → [limits](https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits)
- **H3 Max Turbo**：六种比例，含 9:16 与 21:9 → [turbo](https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained)
- **Vidu Q4**：图生视频**跟随起始图比例**；参考生视频给 16:9 / **9:16** / 1:1 / **3:4** / 4:3 → [model](https://arcloop.ai/models/en-US/vidu-q4)
- **Seedance 2.0**：在 settings 里选比例，官方未给完整列表 → 未公开
- **图片模型（Seedream 5 / GPT Image 2 / 2.5）**：完整比例列表**未公开**；官方示例实际出现过 9:16、16:9、1:1（均 2K）

> **9:16 的真正难点不是设比例，是构图。** 官方给的硬规则：脸放上三分之一；手/证据放中段；**下三分之一留给字幕和平台 UI**；上下边缘留呼吸；首帧和尾帧分别设计。
> 来源：<https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video>

### Q3 图生视频怎么走？首帧/尾帧/参考图？

| 路线 | 具体做法 | 限制 | 来源 |
|---|---|---|---|
| **Vidu Q4 image-to-video** | 1 张图作为**起始帧**，比例随图；提示词只写「动什么、镜头怎么动」 | ❌ 不接受尾帧；❌ 不接受参考视频；❌ **纯文本不行（必须给图）** | [model](https://arcloop.ai/models/en-US/vidu-q4) · [tool](https://arcloop.ai/tools/en-US/vidu-image-to-video) |
| **Vidu Q4 reference-to-video** | 1–15 张参考图 + 最多 3 条音频参考，用来锁人物/场景 | 参考只「引导」，不保证完全连续 | 同上 |
| **Seedance 2 / 2.5 参考图** | 上传图/视频/音频，在提示词里用 `@` 点名每个素材负责什么 | **Seedance 系列要求元素先作为项目资产存在**，才能 `@` 引用 | [seedance-2](https://arcloop.ai/models/en-US/seedance-2) · [对比](https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5) |
| **Seedance 2.5 上限** | 最多 30 图 + 10 视频 + 10 音频（宣传语写 50 个多模态参考） | 官方提醒：参考不是越多越好，10–20 个足够 | [model](https://arcloop.ai/models/en-US/seedance-2.5) · [get-started](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style) |
| **MiniMax H3** | 图/视频/音频参考；9 图 + 3 视频段（2–15s，合计 15s）+ 3 音频 | **音频参考必须配一个画面**，不能单独交音频 | [limits](https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits) |
| **首尾帧** | **Canvas 的 Video 节点支持 first/last-frame 模式**；模型层已确认 **H3 Max Turbo 图生视频支持「可选尾帧」** | 哪些模型在 arcloop 里开放尾帧=**逐模型未公开** | [canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) · [turbo](https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained) |

**操作路径（一条图 → 一条片）**
1. 图存进 Library / 绑到资产（Character / Scene / Prop / Visual reference）→ [image-editing](https://arcloop.ai/handbook/en-US/image-editing-tools)
2. 进 Canvas → 加 **Video Node** → 选模型 → 挂参考图（或在 shot card 里写 `@资产名`）
3. 提示词**只写新增信息**：一个动作 + 一个镜头指令 + 情绪 + 光线延续；**不要在提示词里重新描述人物长相**（身份该来自资产）
4. 生成 → 看首帧是否被尊重、动作是否读懂、尾帧能不能剪

### Q4 中文还是英文？负面词有独立字段吗？

**语言策略（官方口径）**
- **视频：建议英文。** 「Seedance 2.5 能处理相当长的英文提示词，我们建议用英文，因为电影镜头术语在英文里更成熟」；复杂场景 100–300 词；Seedance 2.0 建议 **<1500 词**。
  来源：[get-started](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style) · [seedance-2 FAQ](https://arcloop.ai/models/en-US/seedance-2)
- **图片：中文可用，且官方自己在用中文写示例。** 官方中文提示词示例（GPT Image 2.5、Seedream 5 Pro 模板卡）均为中文原文。
  来源：[flare/sunburst zh-TW](https://arcloop.ai/handbook/zh-TW/arcloop-gpt-image-2-5-flare-sunburst-guide) · [sketch-to-storyboard zh-TW](https://arcloop.ai/handbook/zh-TW/sketch-to-storyboard-arcloop) · [Seedream 5 Le/Pro](https://arcloop.ai/handbook/en-US/seedream-5-lite-vs-pro-guide)
- **界面语言**：Story Brief 里可设**故事/对白语言**（中文/英文/日文/韩文…）；拆解镜头描述跟这个走。
  来源：[first-episode](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop)
- **实用结论**：`画面指令/镜头术语 → 英文`；`要渲染在图上的中文文案 → 中文原文照抄进引号`。

**负面词：没有独立字段（公开页面未见）。**
官方做法是把 **Negative constraints 写成提示词的第六段**（六段式：主体 / 服装 / 构图与姿态 / 背景环境 / 光线色彩风格 / 负面约束）。
来源：[six-block](https://arcloop.ai/handbook/en-US/six-block-prompt-structure-anti-drift)
视频侧同样写在正文末尾，例如官方示例：「Negative constraints: no cropped hands, card must not enter the subtitle zone, no extra passenger…」
来源：[vertical](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video)

> ⚠️ 因此**每一条提示词都必须自带一段负面约束**，不能指望生成器里有 negative prompt 框。

### Q5 3:4 / 9:16 小红书卡片怎么做？Seedream 5 vs GPT Image 2.5 各擅长什么？

**比例**
- **9:16：已确认可直接出**（图片示例卡 9:16 @2K）。
- **3:4：官方公开页面里没找到图片侧的 3:4 证据 → 未公开。** 已知 3:4 只出现在**视频**侧（MiniMax H3 比例列表、Vidu Q4 参考生视频）。
- **兜底方案（可以放心写进流程）**：
  1. 先生成 **9:16**，按 3:4 的取景重心构图，后期裁掉上下（9:16 → 3:4 只裁上下，不裁宽度）；
  2. 或用**图片编辑的智能扩图**（官方支持 1:1 / 16:9 / 9:16 / 4:3）把底图改到接近的版式。来源：[image-editing](https://arcloop.ai/handbook/en-US/image-editing-tools)
- 输出分辨率：图片侧示例常见 **1K / 2K**；Seedream 5 Lite 支持 2K/3K，Pro 支持 1K/2K。来源：[lite vs pro](https://arcloop.ai/handbook/en-US/seedream-5-lite-vs-pro-guide)

**两个模型的分工（官方对比原文）**

| 维度 | GPT Image 2.5 | Seedream 5（Lite / Pro 两个档） |
|---|---|---|
| 定位 | 快 + 精确编辑 + **文字与排版最强** | 视觉方向探索 / 角色 / 场景 / 海报 |
| 文字排版 | 官方评级 **Excellent**（GPT Image 2 是 Good） | Pro：**原生多语种文字**（14 种语言，列举日/韩/俄/阿/泰） |
| 编辑 | 参考图编辑、主体保留强 | Pro：**空间标注编辑**（点/框/箭头/草图）+ **图层拆分** |
| 密集信息图 | 海报/信息图/社交图 OK | **Pro 的强项**：infographic / diagram / 海报 / slides |
| 速度 | Very Fast（比 Image 2 快至多 50%） | Lite 适合高频批量；Pro 更慢更贵 |
| 适合谁 | 中文标题卡片、海报、封面、改字改版式 | 角色/场景/道具、密集信息图、需要拆层再排版 |

来源：[gpt-image-2.5](https://arcloop.ai/models/en-US/gpt-image-2.5) · [seedream-5](https://arcloop.ai/models/en-US/seedream-5) · [lite vs pro](https://arcloop.ai/handbook/en-US/seedream-5-lite-vs-pro-guide)

**中文上图的真实水平（官方实测原文，很关键）**
> 官方用同一提示词让两档写三个字符串：`契约之痕` / `THE MARK OF THE CONTRACT` / `第1集 · EP.01` —— **两档都写对了，连毛笔字效果都对**。
> 但同一个测试里，Sunburst **擅自加了没审批过的中文标语**，还把弧形标签上的 `VOL.1` 写坏。
> 官方给的必做动作：**列出精确文案 + 加一句「no other text」+ 100% 放大逐字校对。**

来源（实测）：<https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst>
来源（中文封面流程）：<https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop>

---

## 3. 模型参数卡

> 标注约定：✅=官方明确支持　❌=官方明确不支持　⚠️=有前提条件　❔=未公开
> 每张卡底部是该模型**唯一**官方规格页。

### 3.1 视频模型

#### Seedance 2.5　`seedance-2.5`
| 项 | 值 |
|---|---|
| 单次时长 | 最长 **30s**（可延长；另有 50s / 长视频模式数分钟口径，见 §7） |
| 分辨率 | 最高 **4K**；入口默认 720p |
| 比例 | 16:9 / 9:16 / 1:1 / 2.39:1 |
| 输入 | 文 / 图 / 视频 / 音频；**30 图 + 10 视频 + 10 音频**（宣传口径 50 个多模态参考） |
| 图生视频 | ✅ 加图作角色/场景/视觉参考 |
| 首尾帧 | ❔ 模型页未写；Canvas Video 节点有 first/last-frame 模式 |
| 原生音频 | ✅ 对白/音乐/环境/音效 + **11 语言唇形同步**（与另一篇手册冲突，见 §7） |
| 时间戳编辑 | ✅ 可改某时间点的角色/动作/物体/镜头/音频；可向前向后延长 |
| 语言 | 官方建议**英文**，复杂场景 100–300 词 |
| 负面词 | ❌ 无独立字段 → 写在提示词里 |
| 导出 | MOV / H.264 / YUV444P / PCM |
| 已知限制 | 多人复杂调度难；精确物理交互、文字数字易错；参考图并非越多越好（10–20 足够） |

来源：[model](https://arcloop.ai/models/en-US/seedance-2.5) · [get-started](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style) · [对比](https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5)

#### Seedance 2.0　`seedance-2.0`
| 项 | 值 |
|---|---|
| 单次时长 | 最长 **15s** |
| 分辨率 | 最高 **4K**；入口默认 720p |
| 比例 | settings 里选（完整列表 ❔）；示例卡出现过 16:9 / 9:16 |
| 输入 | 文 / 图 / 视频 / 音频；提示词里用 `@` 点名素材职责 |
| 图生视频 | ✅（加图当角色/场景参考） |
| 首尾帧 | ❔ 未在模型页写明 |
| 音频 | 支持音频参考；是否原生生成对白/音效 ❔（2.5 才明确写原生音频） |
| 语言 | 英文优先；提示词 **<1500 词** |
| 负面词 | ❌ 无独立字段 |
| 已知限制 | 参考视频只「参考动态」不逐帧复刻；**元素必须先作为资产存在**才能 `@` |
| 官方价格口径 | FAQ 原文「around 150–450 credits per second」（仅引用，不作为预算依据） |

来源：[model](https://arcloop.ai/models/en-US/seedance-2)

#### MiniMax H3
| 项 | 值 |
|---|---|
| 单次时长 | **4–15s**（15s 是每一档的硬顶） |
| 分辨率 | 托管版 **2K（2560×1440）**；基模/自托管 768p（2K 是二次放大阶段） |
| 比例 | 21:9 / 16:9 / 4:3 / 1:1 / **3:4** / **9:16** / auto |
| 输入 | 文 / 图 / 视频 / 音频；**9 图 + 3 视频段（每段 2–15s，合计 15s）+ 3 音频** |
| 图生视频 | ✅ |
| 首尾帧 | 👉 用 H3 Max Turbo 的「可选尾帧」 |
| 原生音频 | ✅ 32kHz 立体声，画面同时生成；音视频「续写」✅ |
| 语言 | 英文术语优先；按顺序描述 |
| 负面词 | ❌ 无独立字段 |
| 已知限制 | ⚠️ **音频参考必须伴随画面**；2K 生成是分钟级；多角色调度难 |

来源：[model](https://arcloop.ai/models/en-US/minimax-h3) · [limits](https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits)

#### MiniMax H3 Max
| 项 | 值 |
|---|---|
| 单次时长 | **5–15s** |
| 分辨率 | **480p / 768p**（无 2K 阶段） |
| 比例 | 同 H3 家族（含 9:16） |
| 输入 | 文 / 图 / 视频 / 音频参考；最多 9 图 / 3 视频 / 3 音频（参考模式上线后才有） |
| 图生视频 | ✅ |
| 原生音频 | ✅ |
| 续写 | ❌ 没有 continuation 模式 |
| 语言 / 负面词 | 同 H3 |
| 已知限制 | 是 fal 基于 H3 开放权重后训练的「快档」（不是更大模型）；5s@480p ≈3s 出片；15s@480p ≈16s |
| 用途 | **草稿/卡点/构图试错**，不要拿它出成片细节 |

来源：[model](https://arcloop.ai/models/en-US/minimax-h3-max) · [limits](https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits)

#### MiniMax H3 Max Turbo
| 项 | 值 |
|---|---|
| 单次时长 | **5–15s**，**24fps** |
| 分辨率 | **480p / 768p** |
| 比例 | 六种，含 9:16 / 21:9 |
| 输入 | 文 / 图（**可选尾帧**） |
| **首尾帧** | ✅ **图生视频支持可选 end frame**（本平台唯一明确的尾帧能力） |
| reference-to-video | ❌ **不支持** → 锁不住人物/风格 |
| 原生音频 | ✅ 立体声随画面生成 |
| 语言 / 负面词 | 同 H3 |
| 已知限制 | 是 fal 的蒸馏预览档；速度约 2×、成本约 ½；**不要指望它保脸** |

来源：[turbo](https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained)

#### Vidu Q4 Preview
| 项 | 值 |
|---|---|
| 单次时长 | **3–16s** |
| 分辨率 | 540p / 720p / 1080p / 2K / 4K |
| 比例 | 图生视频**跟随起始图**；参考生视频 16:9 / 9:16 / 1:1 / **3:4** / 4:3 |
| 模式 | **image-to-video**（1 张起始帧） / **reference-to-video**（1–15 图 + ≤3 音频） |
| 纯文本 | ❌ **不支持**（必须给图） |
| 尾帧 | ❌ **不支持** |
| 参考视频 | ❌ **不支持** |
| 音频 | ✅ 生成音频可开可关；reference 模式可加 ≤3 条音频参考 |
| 语言 | 英文；提示词写「一条明确动作 + 一个镜头指令」，用 `@` 引用资产 |
| 负面词 | ❌ 无独立字段（官方示例写在句尾：`No hands, no object rotation, and no cuts.`） |
| 已知限制 | 参考画面只能「引导」，不保证逐帧连续；相机路径不可精确复现 |

来源：[model](https://arcloop.ai/models/en-US/vidu-q4) · [tool](https://arcloop.ai/tools/en-US/vidu-image-to-video) · [prompt guide](https://arcloop.ai/handbook/en-US/vidu-q4-preview-prompt-guide)

### 3.2 图片模型

> ⚠️ 先在 **Story Settings → Image Model** 里确认档位名，再写提示词。同一个宣传名在生成器里可能拆成两个档。

#### GPT Image 2.5 —— 生成器里分成两档：**Flare** / **Sunburst**
| 项 | Flare | Sunburst |
|---|---|---|
| 定位 | 忠实执行提示词、快、偏动漫/平面 | 材质/结构/排版更强、会「自己设计」、偏写实 |
| 适合 | 草稿、连镜、构图探索、社交比例测试 | 封面、主视觉、材质特写、密集文字成片 |
| 速度 | 快（纯图约快 10%；带文字排版约快 2×） | 慢 |
| 文字排版 | 照抄你给的字符串 | 更会排，但**会加你没批准的字** |
| 质量档 | **low / medium / high / xhigh / max**（五级） | 同一套 |
| 分辨率 | 示例：1K / 2K | 示例：1K / 2K |
| 比例 | 已见 9:16、16:9、1:1（均 2K）；完整列表 ❔ | 同 |
| 输入 | 文生图 + 参考图编辑（主体保留强） | 同 |
| 语言 | 中文提示词可用（官方中文示例） | 同 |
| 负面词 | ❌ 无独立字段 → 必须写「Only these exact strings… No other text.」 | 同 |
| 已知限制 | 材质/细节不如 Sunburst | 会加戏、会写错弧形小字、偏写实会破坏动漫风 |

来源：[flare/sunburst](https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst) · [五级质量 zh-TW](https://arcloop.ai/handbook/zh-TW/arcloop-gpt-image-2-5-flare-sunburst-guide) · [model](https://arcloop.ai/models/en-US/gpt-image-2.5)

#### GPT Image 2
| 项 | 值 |
|---|---|
| 输入 | 文生图 + 参考图编辑（改物体/衣服/背景/文字/版式） |
| 排版 | 官方评级 Good（2.5 是 Excellent）→ **只当兜底** |
| 分辨率 | 入口默认 2K |
| 比例 | ❔ 完整列表未公开 |
| 语言 | 中文可用 |
| 负面词 | ❌ 无独立字段 |

来源：[model](https://arcloop.ai/models/en-US/gpt-image-2)

#### Seedream 5 —— 生成器里是两个档：**Seedream 5 Lite** / **Seedream 5 Pro**
| 项 | Lite | Pro |
|---|---|---|
| 分辨率 | **2K / 3K** | **1K / 2K** |
| 生成方式 | 文生图 + 图生图 | 文生图 + 图生图 |
| 提示词跟随 | 通用创作强 | **密集结构化指令更好** |
| 编辑 | 自然语言编辑 | **空间标注**（点/框/箭头/草图）+ **图层拆分** |
| 多语种文字 | 通用文字生成 | **原生多语种文字（14 种语言）** |
| 适合 | 概念、故事板、高频批量 | 成片、精确改图、本地化海报/版式、信息图 |
| 比例 | 已见 9:16 @2K | 已见 16:9 @2K；完整列表 ❔ |
| 负面词 | ❌ 无独立字段 | 同 |
| 已知限制 | 密集排版会糊；不代表最终质量 | 慢；提示词结构差照样崩；仍需人工校对 |

来源：[lite vs pro](https://arcloop.ai/handbook/en-US/seedream-5-lite-vs-pro-guide) · [model](https://arcloop.ai/models/en-US/seedream-5)

### 3.3 音频

#### Seed Audio 1.0
| 项 | 值 |
|---|---|
| 单次时长 | **≤2 分钟**（可续写） |
| 语言 | **20+ 语言，含中文** |
| 能力 | 对白 + 环境声 + 音效 + 配乐**一次成场景**；按叙事顺序排布，精度约 100ms |
| 参考 | 声音参考：**最多 3 段 ×30s**；另有 T2A / A2A 两种模式 |
| 写法 | `角色名（年龄/音色/语速）：「台词」`；音效单独成行；配乐用 `Soundtrack:` 标签并写时长 |
| 已知限制 | 不可复现：同一提示词两次结果会不同；配乐若只写情绪词，常被压成 2 秒音效 |

来源：[model](https://arcloop.ai/models/en-US/seed-audio-1.0)

---

## 4. 官方推荐的提示词结构（直接照这个写）

### 4.1 图片：六段式（官方 anti-drift 结构）
1. **Subject character** — 身份块：脸型、发、眼、年龄、1–2 个记忆锚点
2. **Outfit** — 服装块：轮廓、面料、色块、鞋、1 个配饰
3. **Composition and pose** — 构图块：景别 + **只写一个动作**
4. **Background environment** — 场景块：一个地点 + 一个视觉任务；需要时「不要可读招牌」
5. **Light, color, and style** — 配方块：材质底层 + 线条/笔触 + 色板
6. **Negative constraints** — 约束块：不要文字/logo/水印/多手多指/风格失败项

铁律：**顺序不能乱**（风格放最前会把人重设计）；**每块只干一件事**；空白块 = 模型自由发挥。
来源：<https://arcloop.ai/handbook/en-US/six-block-prompt-structure-anti-drift>

### 4.2 信息卡片（中文标题型）的官方套路
**路线 1：图 + 短标题一次出**
```
<比例/画质> + 主体与位置 + 精确文案（引号内逐字） + 只显示这几行 + 留白/安全区 + no other text
```
**路线 2（推荐给「改字频繁」的资讯号）：无字底图 + 后期加字**
先出「无文字背景图」（标题区留低细节暗部），再在 **Canvas 的文字/裁剪/扩图** 里加中文，或导出后用设计工具排。
官方理由：文字变化频繁时，无字底图比每次重生成整张图更可控。
来源：<https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop>

### 4.3 视频：镜头卡写法
```
[景别] of @角色 in @场景. 
Frame map（上三分/中段/下三分留字幕）.
Action: 一个动作，按时间顺序.
Camera: 一个镜头运动.
Lighting: 光的方向与质感.
Negative constraints: ...
```
官方 9:16 三条示例都是这个骨架。
来源：<https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video>

### 4.4 身份靠资产，不靠形容词
- 角色/场景/道具先建资产（Main image + Reference images），提示词里只写 `@资产名`。
- 换模型不改脸：同一 shot 换模型时**保持描述不变**，只换模型。
来源：[canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) · [对比](https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5)

---

## 5. 三条改写自官网示例的提示词

> 三条都是**按官网示例结构改写**成资讯号场景，改写依据已标注；不是凭空创作。
> 方括号 `[...]` 是每期替换的变量。

### 示例 1｜中文信息卡片（封面）
**改写自**：官方「GPT Image 2.5 中文封面系统」Route 1 + Flare/Sunburst 例 3
（<https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop> ／ <https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst>）

```
Create a vertical cover (9:16, 2K) for an AI news card.
Put a single abstract glowing object on the right third, floating above a dark low-detail background; keep the left side dark, empty and clean for typography.
On the left, show exactly these three lines and nothing else:
“AI 周报” in heavy white Chinese type, largest;
“第 [07] 期” clearly smaller beneath it;
“[关键词]” as a small accent line with a bright accent color.
Keep the title, subject and edges inside a safe area with breathing room on every side.
No English, no logo, no watermark, no date, no badge, no tagline, no extra glyphs, no gibberish text.
Image model: GPT Image 2.5 Sunburst, 2K.
```
**为什么这么写**：精确字符串 + 只有这几行 + no other text（挡 Sunburst 加戏）+ 安全区。生成后 **100% 放大逐字校对中文笔画**。

### 示例 2｜30 秒资讯短片（Seedance 2.5 单次）
**改写自**：官方 Seedance 2.5 风格块 + 竖版镜头卡 + 时长三段式
（<https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style> ／ <https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video>）

```
Vertical 9:16, 30 seconds, 30fps. One continuous shot in a dark studio desk setup.

Frame map: the desk surface and a glowing phone sit in the center band; the upper third holds soft window light; the lower third stays empty for subtitles.

0-8s: the camera slowly pushes in on the phone screen as a notification light pulses once.
8-18s: a hand enters from the bottom, lifts the phone, and tilts it toward the light; reflections slide across the glass.
18-30s: the hand lowers the phone and settles; the light stabilizes and the frame holds calm for the last two seconds.

Style: desaturated cool blue palette with one warm amber accent, Rembrandt side light, subtle rim light, volumetric haze, film grain.
Sound: quiet room tone, one soft notification chime at 6s, no music.
Negative constraints: no readable random text, no extra hands, no camera roll, no cuts, no scene change, no face, no watermark.
```

### 示例 3｜图生视频（封面图 → 1 个镜头动起来）
**改写自**：官方 Vidu Q4「灯笼特写」三条镜头方向之一
（<https://arcloop.ai/handbook/en-US/vidu-q4-preview-prompt-guide> ／ <https://arcloop.ai/tools/en-US/vidu-image-to-video>）

```
Close shot of @[信息卡片] resting on a dark desk in @[演播室]. Move the camera slowly forward along a straight path, keeping the card centered and completely inside the frame.
The card remains stationary, its base touching the desk. Preserve the card edges, the title block and the color blocks exactly; let a soft highlight travel slowly across the surface while the warm light inside the accent element flickers once.
Keep background objects soft and the light direction unchanged. End the movement gently before the top edge of the card reaches the frame edge.
No hands, no object rotation, no cut, no text changes, no new objects.
```
**注意**：Vidu 的 image-to-video **不接受尾帧、不接受参考视频、不接受纯文本**；比例跟随起始图，所以卡片要**先生成好 9:16 的图**（3:4 是否可选未证实，需要 3:4 就在出图后裁）。

---

## 6. 「arcloop 上做不到的事」清单

> 这一节是防废提示词的核心。**写提示词前先扫一遍。**

1. **Vidu Q4 不能纯文生视频** —— 必须给图；且**不能给尾帧**、**不能上传参考视频**。
   <https://arcloop.ai/models/en-US/vidu-q4>
2. **单次时长硬顶**：H3 / H3 Max / H3 Max Turbo / Seedance 2 都是 **15s**，Vidu 是 **16s**。**30s 只能靠 Seedance 2.5 一次出，或拼两段。**不能再幻想「一个提示词出 30 秒」用在 H3 上。
   <https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits>
3. **没有独立的负面词输入框**（公开页面未见任何 negative prompt 字段）。负向约束必须写进提示词，否则等于没写。
   <https://arcloop.ai/handbook/en-US/six-block-prompt-structure-anti-drift>
4. **H3 Max Turbo 没有 reference-to-video** —— 不能靠参考图锁人物/风格，只适合草稿。
   <https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained>
5. **中文小字不能盲信**：官方实测 Sunburst 会**自己加没批准的文案**、会把弧形小字写坏；官方要求「列出精确字符串 + no other text + 100% 逐字校对」。要绝对可控 → 用无字底图 + Canvas 加字。
   <https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst>
6. **3:4 图片比例没有公开证据** —— 只在视频侧出现。小红书 3:4 卡片请按 9:16 生成后裁切，或先确认生成器下拉里有没有 3:4。
7. **不能一次出多个比例的同一张图** —— 官方做法是「在 Canvas 里选比例重新生成或扩图」，不是裁剪拉伸。
   <https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop>
8. **精确物理交互 / 多人精确走位 / 精确手指动作** 明确超出模型能力（官方自述边界），不要写这类要求。
   <https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style>
9. **Seedance 系列要先有资产**：想 `@` 引用角色/道具，元素必须先在项目里作为资产存在。
   <https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5>
10. **H3 的音频参考不能单独交**，必须配一个画面/视频参考。
    <https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits>
11. **4K 只有 Seedance 2.5 / Seedance 2 / Vidu Q4**；H3 封顶 2K；H3 Max / Turbo 只有 768p（480p）。
12. **音频单次 ≤2 分钟**（Seed Audio 1.0），更长要续写。
    <https://arcloop.ai/models/en-US/seed-audio-1.0>
13. **模型清单不止 /models 那 9 个页面**：站内还提到 Nano Banana 2 / Nano Banana Pro / **Kling Omni** / Grok Imagine / ElevenLabs，这些**没有公开规格页**。
    → **但「没规格页」≠「不能用」**：Kling 在 arcloop 官方手册里被点名推荐，属于会员可用模型，**规格需现场在下拉框和生成器里确认**（详见 §9）。
    仍未找到公开规格页、本文档暂不为其写提示词的：Nano Banana 2 / Nano Banana Pro / Grok Imagine / ElevenLabs。
    <https://arcloop.ai/models/en-US/seedream-5> · <https://arcloop.ai/handbook/en-US/how-to-rotoscope-with-ai>
14. **平台是手动操作**：公开页面未见开放 API；批量只能靠 Canvas 多节点 + 资产库复用。
15. **额度/并发/排队/订阅档位一律未公开**；唯一可靠动作是生成前看生成器里的积分估算。

---

## 7. 官方资料自相矛盾 / 未公开（写提示词时按这里取保守值）

| 冲突点 | 说法 A | 说法 B | 本文件取哪个 |
|---|---|---|---|
| Seedance 2.5 是否原生出音频 | 模型页 FAQ：**是**，对白/音乐/音效 + 11 语言唇形同步 | 官方 get-started 手册 1.3：**「不直接生成音频，声音和对白需要后期」** | 取 A（模型页 + 型号对比表一致），但仍**在生成器里确认音频开关**，并准备后期兜底 |
| Seedance 2.5 时长上限 | 模型页 / 对比表：30s | get-started：30s，最长 **50s**；对比表：长视频模式**数分钟** | 计划按 **30s/段**，延长能力当作 bonus |
| Seedream 5 的档位名 | 模型页标题写 **Seedream 5.0 Pro** | 同一页「Generate Now」链接实际是 **seedream-5.0-lite**；handbook 把 Lite / Pro 当两个模型 | **以 Story Settings 下拉里的名字为准**，默认入口给的是 Lite |
| 参考图张数 | handbook 示例卡上传控件显示 `最多 4 个文件` | Vidu 1–15 图；Seedance 2.5 30 图；H3 9 图 | 以各模型规格为准；4 个疑为示例组件限制 |
| 图片侧 3:4 | 未在任何官方页面出现 | 视频侧（H3 / Vidu）明确有 3:4 | 视为**未公开**，先按 9:16 出再裁 |
| 图片侧完整比例列表 | 示例卡见 9:16 / 16:9 / 1:1 | 无页面列出完整枚举 | **未公开**，以生成器为准 |
| 价格 | Seedance 2.0 FAQ：约 150–450 积分/秒 | 新用户可领 3,000 赠送积分 | 仅作参考，**不做预算承诺** <br><https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop> |

---

## 8. 每次开工前的 60 秒自检

- [ ] 项目 Story Brief：语言、**9:16**、Realistic/Anime、图片/视频模型都设了吗（会继承到每条 shot）
- [ ] 图片模型下拉选的是 **Flare** 还是 **Sunburst**（不是笼统的「GPT Image 2.5」）
- [ ] 图片模型下拉选的是 **Seedream 5 Lite** 还是 **Pro**
- [ ] 视频模型时长控件实际可选值（别照本文件猜）
- [ ] 提示词里有没有 **负面约束段**（没有就补）
- [ ] 中文文案是否**逐字**列出，并加了 `no other text`
- [ ] 角色/场景是否走 `@资产名`，而不是在提示词里重描述长相
- [ ] 视频是否 ≤ 该模型上限（H3 系 15s / Vidu 16s / Seedance 2 15s / 2.5 30s / **Kling 3.0 Omni 15s**）
- [ ] 用 Kling 时 **audio 开关**开了吗（Kling 默认 `off`，不开就是无声）
- [ ] 生成前看积分估算


---

## 9. 会员可用模型补充：Kling 系列

> **前提**：用户是 arcloop 付费会员、有积分。Kling 在 arcloop 上**可用**——本文档 v1 把「没有公开规格页」错当成了「不要写」，这里更正。
> 但 arcloop **没有** Kling 的规格页，所以 §9.2 的能力数据来自**快手可灵官方文档**，已明确标注为「非 arcloop 页面规格」；**arcloop 侧的真实可选值必须现场确认**。

### 9.1 Kling 在 arcloop 的实际入口（官方页面证据）

| 证据 | 说明 | 来源 |
|---|---|---|
| 模型页页脚「Explore more AI models」列出 **Kling Omni** | 与 Seedance 2.0 / 2.5、Nano Banana Pro、GPT Image 2、Seedream 5.0、Grok Imagine、Seed Audio 1.0、ElevenLabs 并列，说明它在 arcloop 模型集合内 | <https://arcloop.ai/models/en-US/seedream-5> · <https://arcloop.ai/models/en-US/gpt-image-2> |
| 手册《How to Rotoscope with AI》点名推荐 | 原文：「Pick a video model that fits the style you're going for. For this workflow, we recommend the **Seedance 2.0 and Kling Omini 3 series**.」并要求先设 **aspect ratio / resolution / video length** | <https://arcloop.ai/handbook/en-US/how-to-rotoscope-with-ai> |
| **没有独立模型页** | `/models/en-US/kling-omni` → **HTTP 404**；`/sitemaps/models.xml` 只收录 9 个模型 slug，无 kling | <https://arcloop.ai/sitemaps/models.xml> |
| 因此入口在哪 | **生成器的模型下拉 / Story Settings 的 Image Model & Video Model 列表**（与 GPT Image 2.5 Flare/Sunburst 同一套切换方式） | <https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst> |

**仍未公开、必须现场看的三件事**
- 下拉里到底有几档（Kling 3.0 / Kling 3.0 Omni / Kling O1 / Kling 2.x…）→ **未公开**
- 每档在 arcloop 上开放哪些参数（首尾帧？元素参考？audio 开关？）→ **未公开**
- 积分消耗 → **未公开**（以生成前估算为准；本文档不写价格）
- 名称坑：arcloop 手册里写作「Kling **Omini** 3」（疑似 Omni 的拼写变体）；**以生成器下拉的显示名为准**

### 9.2 Kling 3.0 Omni 能力（⚠️ 以下为**快手可灵官方公开能力，非 arcloop 页面规格**）

> 来源：可灵官方用户指南 <https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide>（2026-02-06）
> 来源：可灵官方 API 文档 Text-to-Video <https://kling.ai/document-api/api/video/3-0-omni/text-to-video.md>
> **在 arcloop 上以生成器实际选项为准；下表用于「知道它理论上能干什么」，不是 arcloop 的承诺。**

| 项 | Kling 3.0 Omni（官方口径） | 对我们的意义 |
|---|---|---|
| 文生视频 | ✅ **带原生音频 + 多镜头** | 一条提示词可拆成 1–6 个镜头 |
| 图生视频 | ✅ | 首帧驱动 |
| **首尾帧** | ✅ **Start & End Frames-to-Video** | 与 H3 Max Turbo 一样能定尾帧，做「A→B」的整活变形 |
| 多图参考 / 元素参考 | ✅（多角度图或视频建「元素」，跨镜头锁人物/道具/场景） | 角色一致性走 **element + `@` 引用** |
| 视频元素参考 | ✅（O1 不支持，3.0 Omni 支持上传/录制视频元素） | 可用真人动作当元素 |
| 元素配音 | ✅ 可给元素加声音 | **中文台词/角色定向发声**的关键 |
| 单次时长 | **3–15 秒整数**（API 枚举 3…15，默认 5）；O1 时代上限 10s，3.0 系列提到 15s | 20–30s 片子仍需 ≥2 段拼 |
| 画面比例 | **16:9 / 9:16 / 1:1**（默认 16:9） | **9:16 竖屏直接选** |
| 分辨率 | 720p / 1080p / **4K**（默认 720p） | 4K 可用 |
| 原生音频 | ✅ 但 **`settings.audio` 默认 `off`**（`native` / `off`） | ⚠️ **最容易踩的坑：不主动开音频=哑片** |
| 多镜头 | `multi_shot` 默认 **true**；写法 `shot n, m, words;`（n=1–6，m=秒数，各镜头时长之和=总时长，每镜头 prompt ≤512 字符） | 可一次性写「镜头1 2s…镜头2 3s…」 |
| 提示词语言 | 官方英文文档只给英文示例；可灵是中文原生产品、有完整中文文档，**中文提示词大概率可用但 arcloop 页未确认** | 中文台词、中文吐槽直接写，**首条先小成本试** |
| 负面描述 | API 明确「prompt can include **positive and negative descriptions**」→ **写在 prompt 里，无独立字段** | 与本平台 §4 的写法一致 |
| 提示词长度 | 上限 **3072 字符**，建议 ≤2500 | 比 Seedance 2.0 的 1500 词宽 |
| Motion Brush（运动笔刷） | 可灵网页端功能；⚠️ **arcloop 是否提供未公开，不要假设** | 想用先在画布里找按钮 |

### 9.3 什么时候用 Kling，而不是 Seedance 2.5 / MiniMax H3

| 你的需求 | 选谁 | 理由 |
|---|---|---|
| 15s 内、**多镜头 + 中文台词 + 角色定向发声** | **Kling 3.0 Omni** | 目前公开资料里唯一同时有「元素配音 + native audio + 多镜头」的档 |
| **首帧 + 尾帧**卡死起止画面 | **Kling 3.0 Omni** 或 H3 Max Turbo | Vidu Q4 明确不支持尾帧 |
| 20–30s 一镜到底 | **Seedance 2.5** | Kling 封顶 15s |
| 4K + 超大参考集（30 图/10 视频） | **Seedance 2.5** | Kling 参考走「元素」体系，容量未公开 |
| 音乐卡点、必须还原某张插画的近景 | **MiniMax H3** | 官方 shot-type map 这么分 |
| 真人动作 → 风格化转描（整活常用） | **Kling 3.0 Omni + Seedance 2.0** | arcloop 官方转描指南点名这两条 |
| 纯氛围 B-roll、不要人声 | H3 / Vidu Q4（图生视频） | 更简单，不需要元素体系 |
| 快速试错（速度优先，不谈钱） | H3 Max / H3 Max Turbo（⚠️ Turbo 无 reference-to-video） | 价格未公开，此处只谈速度与能力 |

> 一句话：**要「会说中文、会演多镜头」的整活短片 → 先用 Kling；要「一次 30 秒长镜头」→ Seedance 2.5；要「卡点/保脸」→ H3。**

---

## 10. Canvas 工作流（做整活视频的关键）

> 标注约定：**【官方】** = arcloop 文档明写；**【推断】** = 我们基于官方能力的编排建议，不是官方承诺。

### 10.1 画布能干什么【官方】

| 能力 | 说明 | 来源 |
|---|---|---|
| 入口 | 打开一个 World → 侧边栏 **Canvas**；也可从任意生成结果直接进画布继续改 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| 三类节点 | **Image / Video / Audio** 节点，可自由拖拽排布、缩放 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| Image 节点 | 文生图、挂参考图、继续编辑；出图后可 **下载 / 放大 / 扩图 / 去背景 / 转成视频起始帧** | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| Video 节点 | **文生视频 / 首尾帧 / 多参考** 三种模式 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| Audio 节点 | 写对白、选声音、生成或上传参考音频；**绑定到角色**后，之后引用该角色声音保持一致 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| 资产复用 | 从 IP Project 拉 Character / Scene / Prop / Visual reference，在提示词里 `@` 引用 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) · [资产](https://arcloop.ai/handbook/en-US/image-editing-tools) |
| 历史 | 所有图片/视频/音频结果自动进 **Generation History**，可搜索、可拖回画布 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| 画布内改图 | **AI 生成 / 智能去背 / 智能扩图（1:1、16:9、9:16、4:3）/ 分辨率调整**；结果可下载、存 Library、**Bind 到资产** | [图片编辑](https://arcloop.ai/handbook/en-US/image-editing-tools) |
| 文字/裁剪 | 画布支持 **text、crop、outpainting、download** | [中文封面](https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop) |
| 切图 | 画布「**切分图片**」可选 **3×3**，把九宫格切成 9 张独立图（只切像素，不会补齐内容） | [九宫格](https://arcloop.ai/handbook/zh-TW/sketch-to-storyboard-arcloop) |
| 保存 | Canvas 项目会恢复画板、节点、生成结果、视口与缩放 | [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| 成片交付 | 进 **Edit** 时间线排列/修剪/替换片段 + **Generate Voiceover** + BGM/音效 → **Export / Publish** | [第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) |

**画布上「最值钱」的一个用法**
> **同一个首帧图，在画布上并列生成多条 take，再只把选中的那条拖进时间线。**
> 因为 Video 节点可以挂同一个 Image 节点的结果、且所有结果留在画布与 Generation History 里，所以「改一版→再生成→并排比」不丢上下文；官方也明确建议在 Canvas 里来回对比 take。这一条把「重抽 5 次」从浪费变成可复用资产。
> 来源：<https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas>

**画布上未见官方说明的能力（别假设）**
- 一键批量导出多条片段、字幕样式模板、自动转场/自动踩点 → **未公开/未见**
- Kling / Seedance 各档在 Video 节点里是否全部可选 → **未公开**（以节点里的模型下拉为准）

### 10.2 用 Canvas 做一条 20–30 秒整活视频（完整步骤）

| # | 动作 | 官方 / 推断 |
|---|---|---|
| 1 | **建资产**：My Assets 里给主角建 Character，绑 Main image + 至少 1 张 Reference image；关键道具也建 Prop | 【官方】[第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) · [竖版构图](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) |
| 2 | **Story Brief** 设 **9:16** + 语言 + 风格（Realistic/Anime）+ 图像/视频模型；之后每条 shot 自动继承 | 【官方】[第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) |
| 3 | **先出图再出片**：Image 节点生成首帧，确认构图/脸/字幕区，再花积分生视频 | 【官方】[竖版构图](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) |
| 4 | **写 shot 描述**：一个动作 + 一个镜头 + 光线 + 下三分之一留字幕 + 负面约束；身份用 `@角色` 不重描述 | 【官方】[竖版构图](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) |
| 5 | **Video 节点选模式**：要「动起来」用首帧（图生视频）；要「A 变 B」用首尾帧；要锁人物/风格用多参考 | 【官方】[Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) |
| 6 | **分段拍**：20–30s 建议 **4–6 段 × 5–8s**，或 **1 段 15s（Kling/Seedance/H3）+ 1 段 10–15s** | 【推断】依据各模型时长上限（§2 Q1 / §9.2）；节奏分配是我们的编排建议 |
| 7 | **并排比较 take**：同一首帧多生成几条，画布上并排看首帧/表情/动作/尾帧，只留 1 条 | 【官方】[竖版构图：Canvas 用于并排比较 take](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) · 【推断】比较维度 |
| 8 | **拖进 Edit 时间线**：排列、修剪、替换不合格镜头 | 【官方】[第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) |
| 9 | **字幕在 Edit 里加，不要写进视频提示词**（官方：生成的文字会崩/逐帧变；提示词只负责「留出干净的字幕带 + no generated text」） | 【官方】[字幕排版](https://arcloop.ai/handbook/en-US/subtitles-typography-ai-anime-video) |
| 10 | **配音**：Audio 节点生成对白/旁白（可绑角色），或 Edit 里用 **Generate Voiceover**；再加 BGM/环境声 | 【官方】[Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) · [第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) |
| 11 | **导出**：Export 下载；也可 Publish 到平台（官方说精选作品可能得积分奖励） | 【官方】[第一条片](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop) |

**整活视频的三条实操提醒**
1. **音频默认关**：Kling 的 `audio` 默认 `off`；H3/Seedance 也要在参数里确认音频开关。整活片没声=废。
2. **字幕永远后期加**：官方明确「不要指望生成器写字幕」；视频提示词里只写「留出字幕区 + 不要出现文字」。
3. **首帧决定成败**：先在图片节点把首帧调到满意（脸、构图、字幕区都对），再进 Video 节点——官方明确要求先确认构图再花积分。

---

### 附：本文件引用到的官方页面清单

- 模型总览 <https://arcloop.ai/models/en-US> ｜ 主页 <https://arcloop.ai>
- 模型页：[/seedream-5](https://arcloop.ai/models/en-US/seedream-5) · [/gpt-image-2](https://arcloop.ai/models/en-US/gpt-image-2) · [/gpt-image-2.5](https://arcloop.ai/models/en-US/gpt-image-2.5) · [/seedance-2](https://arcloop.ai/models/en-US/seedance-2) · [/seedance-2.5](https://arcloop.ai/models/en-US/seedance-2.5) · [/minimax-h3](https://arcloop.ai/models/en-US/minimax-h3) · [/minimax-h3-max](https://arcloop.ai/models/en-US/minimax-h3-max) · [/vidu-q4](https://arcloop.ai/models/en-US/vidu-q4) · [/seed-audio-1.0](https://arcloop.ai/models/en-US/seed-audio-1.0)
- 手册：[/handbook/en-US](https://arcloop.ai/handbook/en-US) · [六段式](https://arcloop.ai/handbook/en-US/six-block-prompt-structure-anti-drift) · [H3 时长表](https://arcloop.ai/handbook/en-US/minimax-h3-max-duration-resolution-limits) · [H3 vs 2.5](https://arcloop.ai/handbook/en-US/minimax-h3-vs-seedance-2-5) · [H3 Turbo](https://arcloop.ai/handbook/en-US/minimax-h3-turbo-explained) · [Seedream Lite/Pro](https://arcloop.ai/handbook/en-US/seedream-5-lite-vs-pro-guide) · [Flare/Sunburst](https://arcloop.ai/handbook/en-US/gpt-image-2-5-flare-vs-sunburst) · [中文封面](https://arcloop.ai/handbook/en-US/chinese-covers-typography-arcloop) · [竖版构图](https://arcloop.ai/handbook/en-US/vertical-composition-ai-anime-video) · [Canvas](https://arcloop.ai/handbook/en-US/create-better-ai-videos-with-arcloop-canvas) · [图片编辑](https://arcloop.ai/handbook/en-US/image-editing-tools) · [Seedance 2.5 入门](https://arcloop.ai/handbook/en-US/seedance-2-5-getting-started-visual-style) · [Vidu 提示词](https://arcloop.ai/handbook/en-US/vidu-q4-preview-prompt-guide) · [第一条片流程](https://arcloop.ai/handbook/en-US/how-to-create-your-first-episode-on-arcloop)
- Kling / 画布 / 字幕相关：[可灵 3.0 Omni 用户指南（非 arcloop）](https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide) · [可灵 T2V API（非 arcloop）](https://kling.ai/document-api/api/video/3-0-omni/text-to-video.md) · [转描指南（点名 Kling）](https://arcloop.ai/handbook/en-US/how-to-rotoscope-with-ai) · [字幕排版](https://arcloop.ai/handbook/en-US/subtitles-typography-ai-anime-video) · [sitemap（models 只有 9 个 slug）](https://arcloop.ai/sitemaps/models.xml)
- 中文/繁中官方页：[GPT Image 2.5 上线（五级质量）](https://arcloop.ai/handbook/zh-TW/arcloop-gpt-image-2-5-flare-sunburst-guide) · [九宫格与切图](https://arcloop.ai/handbook/zh-TW/sketch-to-storyboard-arcloop)
- 工具页：[/tools/en-US](https://arcloop.ai/tools/en-US) · [Vidu 图生视频](https://arcloop.ai/tools/en-US/vidu-image-to-video)
