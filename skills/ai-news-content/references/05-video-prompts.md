# 视频提示词：arcloop 版（不是即梦/可灵版）

> 平台前提：arcloop.ai 手动生成，选模型 → 填提示词 → 出片。
> 规格来源：`arcloop-models.md`（2026-10-20 核实）。**如果你在网上看到「即梦/可灵/Sora 四版本写法」，那是给直连模型厂的流程，在 arcloop 上不适用。**

---

## 0. 五条平台硬约束（先记这个，比技巧重要）

| # | 约束 | 后果 |
|---|---|---|
| 1 | **没有独立负面词字段** | 负面约束必须内联进提示词末尾，不写等于没有 |
| 2 | **视频提示词建议英文**（官方口径：镜头术语英文更成熟） | 中文写也能出，但复杂镜头容易跑偏 |
| 3 | **单次时长有硬顶**：Seedance 2.5 = 30s；Seedance 2/ H3 系 = 15s；Vidu Q4 = 16s | 想做 30s+ 只能拼，或一镜 30s |
| 4 | **图生视频的首帧能力不通用**：Vidu Q4 只吃 1 张起始帧、不支持尾帧；尾帧只有 MiniMax H3 Max Turbo 支持 | 想做首尾帧动画 → 只能用 H3 Max Turbo |
| 5 | **比例由模型决定**：图生视频跟随起始图比例 | 首帧就出 9:16，后面不用再管 |

---

## 1. 两条生产路线，先选一条

| 路线 | 做法 | 适用 | 成本 |
|---|---|---|---|
| **A. 一镜 30 秒** | Seedance 2.5 单次生成 30s，一镜到底或内部多镜头 | 口播型资讯、氛围型、需要连贯 | 低（一次生成） |
| **B. 分镜拼接** | 每镜 ≤15s（Seedance 2 / H3 / Vidu Q4），Edit 时间线拼接 | 信息量大的资讯、要精确控制每一镜 | 中（多次生成） |

**默认建议走 B**：资讯号要的是「每一镜讲清一个信息点」，一镜到底很难控制信息节奏。
**只有一种情况走 A**：口播 30 秒、画面只需要一个持续氛围（比如主播出镜 + 背景）。

---

## 2. 模型路由

| 你要拍的镜头 | 模型 | 备注 |
|---|---|---|
| 主镜头 / 最终 4K / 多镜头一次出 | **Seedance 2.5** | 单次 30s，唯一能一口气 30s |
| 快速试错 / 音乐卡点 / 近景还原 | **MiniMax H3** | 便宜快，2K 主镜头脸准 |
| 已有首帧图 → 动起来 | **Vidu Q4 Preview (i2v)** | 1 张起始帧，比例跟图 |
| 首帧 + 尾帧指定 | **MiniMax H3 Max Turbo** | 唯一支持可选尾帧 |
| 多段拼接的 B-roll | Seedance 2.0 / H3 | 每段 ≤15s |
| 口播 / 旁白 | **Seed Audio 1.0** | 单次 ≤2 分钟，支持中文，别指望视频模型自带音频 |

> ⚠️ Seedance 2.5「是否原生出音频」官方资料自相矛盾（模型页说支持，手册说要后期）。**按「需要后期兜底」准备。**

---

## 3. 镜头卡写法（官方骨架，照抄）

```
[Shot size] of [subject] in [scene].
Frame map: 上三分之一 / 中段 / 下三分之一 分别放什么（下三分之一留给字幕安全区）.
Action: 一个动作，按时间顺序，写清起点和终点.
Camera: 一个镜头运动（推/拉/摇/移/跟，只选一个）.
Lighting: 光的方向 + 质感.
Negative constraints: ...
```

**七条写作规则**（前四条来自 lanshu 的方法论，后三条是 arcloop 特有）：

1. **每镜只给一种运镜**。推 + 摇就拆两镜
2. **短镜不写死秒数**。5–10s 的镜头，时长在生成器下拉框选，提示词里写「0–3 秒」会出异常。
   **例外**：Seedance 2.5 一次生成 30s 时，**可以**用 `0-8s / 8-18s / 18-30s` 分段描述内部节拍——官方示例就是这么写的（见 `arcloop-models.md` §5 示例 2）。判断标准：**一次生成内部有多段变化才写时间点，单镜单动作不写**。
3. **必须有显式端点**：`then settles` / `fades out` / `comes to rest`，防 99% 卡住
4. **图生视频只描述运动**，不要重复描述图里已有的东西
5. **负面约束内联**，写成最后一段（见 §5）
6. **身份靠资产不靠形容词**：角色/场景先用 `@资产名` 建好，提示词里只写 @ 名字
7. **换模型不改描述**：同一镜换模型时只换模型，提示词保持不动，否则脸会变

---

## 4. 资讯号的镜头类型库（直接套）

| 镜型 | 用来讲什么 | 关键提示词元素 |
|---|---|---|
| **数据对比镜** | 新 vs 旧、成本/速度对比 | 两根柱/两条进度条，只让柱体生长，不重绘数字 |
| **时间轴镜** | 事件发展、版本迭代 | 一条水平线 + 3 个节点，节点依次点亮 |
| **铭牌揭晓镜** | 发布/首发/身份揭晓 | 一块空铭牌，光从一侧扫过，牌面不出现文字 |
| **计价牌镜** | 价格/参数 | 2–3 块空白卡片依次亮起 |
| **收尾风险镜** | 「但是…」的转折 | 一处未扣上的锁 / 一块空白告示牌，冷色转暖 |
| **平台矩阵镜** | 多家上线/多平台 | 3–5 个色块依次点亮（**不要写字**） |

> 所有镜型的共同点：**画面里不出现文字**。数字与平台名全部后期花字叠加。

---

## 5. 负面约束段（每条提示词都复制粘贴这段，按需删减）

> ⚠️ **这段是「无人物信息卡」风格专用的**。如果你的镜头本来就要出现手、人物、胶片质感、慢动作，**必须先把对应条目删掉**——否则提示词自相矛盾，模型会忽左忽右。
> 官方示例 2 里就有 `a hand enters` 和 `film grain`，拿这段包去套它等于自己打自己。

```
Negative constraints: no text, no letters, no numbers, no captions, no subtitles,
no watermarks, no logos, no UI elements, no hands, no faces, no gibberish characters,
no lens flare, no particles, no smoke, no film grain, no slow motion, no camera shake,
no flicker, no morphing, no duplicated objects, no re-lettering of any existing marks,
do not invent any labels or signage.
```

中文项目可以补一句中文版（部分模型中文理解更好）：
```
负面约束：无文字、无字母、无数字、无字幕、无水印、无 logo、无手、无脸、无乱码字符、
无镜头光晕、无粒子、无烟雾、无胶片颗粒、无升格慢动作、无镜头晃动、无闪烁、无形变、无重复物体。
```

---

## 6. 完整示例：一条 28 秒 AI 资讯短片

**前提**：先按 `04-image-prompts.md` 出 6 张无字底图（首帧），再用「图生视频」让它们动起来。

| 镜 | 时长 | 讲什么 | 模型 | 后期花字 |
|---|---|---|---|---|
| S1 | 5s | 身份揭晓 | Vidu Q4 (i2v) | `M3.1 Flash` |
| S2 | 5s | 成本对比 | Vidu Q4 (i2v) | `1/3` `3x` |
| S3 | 5s | 价格 | Vidu Q4 (i2v) | `$0.15` `$0.60` |
| S4 | 4s | 第三方评测 | Vidu Q4 (i2v) | `42` `+13` |
| S5 | 5s | 多平台上线 | Seedance 2.5 | 平台名 ×3 |
| S6 | 4s | 风险收尾 | Vidu Q4 (i2v) | `10/23` |

总计 28 秒，6 镜，全部竖屏 9:16。

> 注意：本表里的「5s / 4s」是**剪辑时间轴**和生成器下拉框的选择，不是写进提示词的秒数。
> 如果你改用 Seedance 2.5 一次出 30s，则按官方示例允许在提示词里写 `0-8s / 8-18s` 分段（见 §3 规则 2 的例外）。

**S1 图生视频提示词（英文，直接复制）**：
```
Image-to-video, keep the frame composition unchanged.
Action: a soft cool-white key light sweeps slowly from the upper-left across a blank brushed-aluminum
nameplate and settles; the small blank tag leaning at the lower-left tilts slightly, then comes to rest.
Camera: slow push-in, one single move, no panning.
Lighting: top 5600K softbox, thin 4300K rim light from the right edge, no shadows on the plate face.
Negative constraints: no text, no letters, no numbers, no logos, no watermarks, no lens flare,
no particles, no camera shake, no flicker, no morphing, do not add any labels or signage.
```

**S2 首帧（文生图，无字）**：
```
9:16 vertical, deep navy-black gradient background with a faint 1px grid.
Two brushed-aluminum vertical bars side by side, bottom-aligned: the left bar is full height,
the right bar is about one third of the left bar's height. Both bars have a blank recessed plate
at the top. Top softbox 5600K, cool rim light from the right, matte frosted-glass floor reflection.
No text, no numbers, no scale marks, no logo, no watermark, no people, no particles, no lens flare.
```

**拼接注意**：Seedance 2.5 单次 30s 可以直接把这些镜合并成一次生成，但信息节奏会失控；资讯号建议 **B 路线逐镜生成 + Edit 拼接**。

---

## 7. 口播音频怎么做

- **Seed Audio 1.0** 单次 ≤2 分钟，支持中文，用它出旁白
- 视频模型自带的音频只到「场景音」级别，**人声别指望**
- 流程：口播稿 → Seed Audio 1.0 出声 → Edit 里对齐画面
- 语速对照：240–280 字/分钟（`03-platform-douyin.md` 有完整规则）

---

## 8. 常见翻车

| 现象 | 原因 | 修法 |
|---|---|---|
| 画面里的字全糊了 | 让模型画文字 | 画面零文字，后期贴 |
| 生成到一半卡住/崩坏 | 没有显式端点 | 补 `then comes to rest` |
| 两镜之间主体变形 | 描述变了 | 同一镜换模型时提示词一字不改 |
| 视频比口播短 | 没算时长 | 口播字数 ÷ 240 × 60 = 最少需要的秒数 |
| 用慢放凑时长 | 懒 | 会撞 `no slow motion`，正片会明显变卡；改补镜或压口播 |
| 做 30s 但只给了 15s 素材 | 不知道时长硬顶 | Seedance 2.5 才能 30s，其它 ≤15/16s |
| 首尾帧动画做不出来 | 选错模型 | 只有 MiniMax H3 Max Turbo 支持尾帧 |
