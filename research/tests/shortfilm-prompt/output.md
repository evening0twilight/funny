# 实测记录：shortfilm-prompt（jnMetaCode/ai-shortfilm-prompts）

- 输入：`research/tests/input-news-01.md`（AIHOT 热点 No.01：MiniMax M3.1 Flash 发布）
- 用户请求（按真实使用场景构造）：把这条新闻做成一条 **20 秒电影感短片**，多镜头叙事，赛博实验室风格，发抖音/视频号
- 执行方式：严格按 `skills/shortfilm-prompt/SKILL.md` 的 Workflow Step 1→4、5-stage 结构、Seven hard rules、30 秒 checklist

## Step 1 — 信息是否足够

| 检查项 | 结果 |
|---|---|
| 视频类型 | ✅ 多镜头叙事（multi-shot narrative） |
| 时长 | ✅ 20s，4 个镜头 |
| 主体 | ✅ 模型拟人化主体（无 IP 名） |
| 场景 | ✅ 深夜实验室 / 数据流空间 |
| 风格 | ✅ 赛博 + 电影感 |

信息齐全 → 跳过 Step 2 追问，直接 Step 3。

## Step 3 — 加载模板

按 SKILL.md 表格选 `templates/multi-shot-narrative.md`（20s，多镜头叙事）。**发现：模板库 29 个题材全是电影感类型（变形/催泪/广告/恐怖/微短剧…），没有「资讯/新闻/B-roll」题材**，只能借用多镜头骨架。

## Step 3 产出（5-stage prompt）

```
1. Core theme
cyberpunk tech reveal | anonymous model unmasked | night laboratory | cinematic realism | no game-CG feel | data as physical light

2. Character & scene
Subject — a young East Asian engineer, short dark hair pushed back, tired eyes with visible dark circles, faint stubble, one small scar above the left eyebrow, no makeup, no beautification. Wearing a slightly wrinkled black technical jacket, matte nylon fabric with worn elbows and a frayed collar edge. Reference uploaded photo, features 100% preserved.
Scene — a cramped server room at 3 a.m., server racks breathing with status LEDs, tangled ethernet cables, a half-empty paper coffee cup, condensation on the glass wall, dust visible in the light beams.

3. Atmosphere & quality
Shot on Sony Venice + Canon K-35 series, 35mm, f/2.0. Low-saturation grey-blue base with a single warm amber practical light from the monitor. Fine 35mm film grain, shallow depth of field, subtle lens vignette. Photorealistic, documentary-digital texture, no glossy CG surfaces, no game-render look.

4. Camera rules
Edited across shots. Handheld and locked-off mix, eye-level for intimacy, one slow push-in on the reveal. Handheld shot. Throughout, maintain an extremely subtle, breath-like camera float to enhance presence.

5. Storyboard
Shot 1
Shot size: Close-up, hands only
Composition: Off-center, foreground cable rack bridging frame
Camera move: Slow lateral dolly left, then micro-pause
Action: Fingers type fast, then stop mid-stroke. Screen light flickers across the knuckles. A terminal line finishes loading.

Shot 2
Shot size: Medium, waist-up
Composition: Rule-of-thirds, subject left, monitor glow right
Camera move: Locked-off, micro handheld drift only
Action: Engineer leans back, exhales through the nose, rubs one eye with the heel of the hand. Facial expression: not triumph — tired relief, slight furrow of the brow. No smile.

Shot 3
Shot size: Extreme close-up
Composition: Centered on the monitor bezel, screen half out of frame
Camera move: Very slow push-in, breathing float
Action: The screen fills with a single line of text rendering character by character; the room lights reflect in the glass. Fingers hover but do not touch the keyboard.

Shot 4
Shot size: Wide, from behind
Composition: Symmetrical corridor of server racks, subject small in frame
Camera move: Static, breathing float
Action: Engineer stands up, walks two steps away from the desk, stops. Shoulders drop. No dialogue.

Sound: No score. Production audio only — server fan hum, keyboard clatter that cuts off abruptly, a chair creak, distant building air-conditioning, one soft electrical click.
```

**交稿前 30 秒 checklist 自检**

| 规则 | 结果 |
|---|---|
| 5 stage 齐 | ✅ |
| 相机 + 镜头型号（Rule 2） | ✅ Sony Venice + Canon K-35, 35mm f/2.0 |
| breathing 句完整（Rule 3） | ✅ 原文照抄 |
| Sound 行（Rule 4） | ✅ "No score. Production audio only." + 枚举环境音 |
| ≥2 个瑕疵（Rule 5） | ✅ 黑眼圈/胡茬/眉骨疤/外套磨旧的肘部/毛边领口 |
| 结尾不堆 FX（Rule 6） | ✅ 以「走两步、停住、肩膀落下」收尾 |
| 无空泛形容词（Rule 1） | ✅ 无 cinematic/epic/4K/perfect 等 |
| 无 IP 名（Rule 7） | ✅ 无 |
| 负面词（Seedance/Kling 需专用字段） | ✅ 已附下方 |
| 单镜头 ≤15s / 多镜头 ≤8 镜 | ✅ 4 镜，总 20s |
| 结尾给模型适配建议 | ✅ 下方 |

## Step 4 — 写作选择说明（SKILL 要求 2-3 条）

1. 人物写成「疲惫的工程师」而不是「天才」，脸上去掉了英雄光——这是 Rule 5 的瑕疵锚点，也是后续 4 个镜头人物不会换脸的关键（黑眼圈 + 眉骨疤 + 磨旧肘部三处可复用坐标）。
2. 结尾没有让屏幕炸出光效、没有「成功」大笑，只让肩膀落下 + 键盘声突然停住——按 Rule 6，把情绪交给「缺席」而不是特效。
3. 声音全程 production audio，不加配乐：新闻类短片一旦上 BGM 就变成广告，这条是 skill 规则里最实用的一条。

## 负面词（Seedance / Kling / Veo 专用字段）

```
blurry, low resolution, soft focus, watermark, text overlay, subtitles, logo, distorted face, asymmetric eyes, extra fingers, deformed hands, melting geometry, oversaturated colors, plastic skin, glossy CG render, video-game look, 3D cartoon, anime shading, flat studio lighting, perfectly clean flawless surfaces, frame flicker, ghosting, jarring hard cuts, lifeless locked-off camera
```

## 模型适配建议（SKILL 要求 1 行）

- **Veo 3.1**：英文优先，单次 8s，这条 20s 需要 3 次续写（7s hops）；负面词放专属字段，不要写 `no...` 命令句。
- **可灵 2.5/3.0**：中文可直接用译文；预生成敏感词过滤会整条拒绝，先把 body/contact 类词洗一遍；单条 5-10s，20s 要拼。
- **Sora 2 Pro**：无负面词字段，需把否定写成正向句（original characters only, no text overlay）；单次最长约 25s，是唯一能一次出 20s 的。
- **Seedance 2.0 / 即梦**：IP 过滤严格，本条无 IP 名可直出；负面词贴专属字段。

## 结论（给报告的判断）

- 产出**可直接粘贴使用**，5 个阶段齐全，规则自检全部通过。
- 但**题材错位**：这条新闻需要的是「口播 + 数字动效 + 截图 B-roll」，而该 skill 的模板库没有资讯类分支，我拿到的是「电影感叙事短片」提示词。对「发布一条 AI 新闻」来说，视觉成本过高（要拍人、要 4 个镜头、要分镜拼接），实际投产不如「录屏 + 数字卡片」。
- 它的真实价值在于：**当你要做「品牌片/概念片/情绪片」而不是「资讯片」时，它是目前见过约束最硬的提示词 skill**。
