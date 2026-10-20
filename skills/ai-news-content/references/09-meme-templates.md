# 梗模板库：14 个拿到就能改的骨架

> 上游：`08-meme-engine.md` 给**机制**（置换 / 对决 / 预告）和**注意力公式**；本文件给**成品骨架**。
> 下游：图 → `04-image-prompts.md` 的版式规则；视频 → `05-video-prompts.md` 的镜头卡规则；模型参数 → `arcloop-models.md`。
> 核实日期：**2026-10-20**。热点窗口见 `research/trends-2026-10.md`。

---

## 0. 怎么用（30 秒）

```
1. 从 08 §4 匹配矩阵确定机制（A 置换 / B 对决 / C 预告）
2. 在本文件挑一个模板，复制它的「出图骨架」
3. 只替换 [方括号] 里的变量，其余一个字都不改（改多了模型就漂）
4. 出图 → 检查有没有瞎加字 → 后期贴字（画面本身零文字）
5. 查该模板的「风险」和「避坑」，对一遍
6. 发之前跑 `07-compliance.md` 的 10 项清单
```

**选模板的硬规则**：
- 有**数字/比分** → 模板 1、9、12
- 有**档期/倒数** → 模板 10
- 有**动作**（骑、打、飞、翻车）→ 模板 4，且值得做视频
- 只有**一句话的反转** → 模板 11、14，纯图文最省
- 涉及**真人**（Tibo、马斯克）→ 只能走模板 4/10/13 的抽象化路线，**不做脸**

---

## 1. 全局铁律（14 个模板共用，违反任何一条都会翻车）

| # | 铁律 | 为什么 |
|---|---|---|
| 1 | **画面零文字**：不出现字母、数字、伪文字、UI 标签、招牌 | arcloop 出文字必崩（官方实测会乱加标语、写坏小字）；文字 100% 后期贴 |
| 2 | **负面约束内联在提示词末尾** | arcloop 没有独立负面词字段，不写等于没写 |
| 3 | **不做真脸、不贴官方 logo、不复刻官方字体** | 肖像权 + 商标，`08` §5 的 L3 红线 |
| 4 | **比分/数字可以是玩笑，不能是伪造赛果** | 「reset 13:0 no reset」✓；「T1 3:0 BLG」✗ |
| 5 | **一条只用一个梗** | 塞三个梗 = 一个都记不住 |
| 6 | **图生视频只写运动，不重述图里有什么** | 重述 = 模型重画 = 脸/材质漂移 |
| 7 | **短镜不写秒数**（时长在下拉框选）；只有 Seedance 2.5 一次出 30s 才允许写 `0-8s / 8-18s` | 写死秒数会出异常 |
| 8 | **AI 生成标识**：画面左下角常驻小字 + 发布页勾选 | 《AI 生成合成内容标识办法》 |

**模型路由（本文件所有骨架默认按这个选）**

| 要什么 | 用哪个 | 备注 |
|---|---|---|
| 一张成片底图（质感/荒诞感要真） | **Seedream 5 Pro**（2K） | 空间标注改图 + 图层拆分；密集排版也能扛 |
| 出图 + 后期只贴少量大标题 | **GPT Image 2.5 Sunburst**（2K） | 排版最强，但会自己加戏 → 必须 `no other text` |
| 一次出 8 张变体试方向 | **Seedream 5 Lite** / **GPT Image 2.5 Flare** | 快；成片再换 Pro/Sunburst 重跑 |
| 15s 单镜 / B-roll | **Seedance 2.0**、**MiniMax H3**、**Vidu Q4** | H3 最便宜快；Vidu 必须给首帧图 |
| 一次 30s 一镜 | **Seedance 2.5** | 唯一能一口气 30s |
| 已有首帧 → 让它动 | **Vidu Q4 Preview（image-to-video）** | ❌ 不支持尾帧 / 纯文本 / 参考视频；比例跟图 |
| 首帧 + 尾帧 | **Kling 3.0 Omni** 或 **MiniMax H3 Max Turbo** | Vidu Q4 明确不支持尾帧 |
| **音乐卡点 / 节拍切** | **MiniMax H3** | 官方 shot-type map 点名卡点用 H3 |
| **15s 内多镜头 + 中文台词 + 角色发声** | **Kling 3.0 Omni** | 公开资料里唯一同时有「元素配音 + 原生音频 + 多镜头」的档 |
| 旁白 / 音效 / 环境声 | **Seed Audio 1.0** | 单次 ≤2 分钟，支持中文 |

> **关于 Kling（2026-10-20 更正版，别用旧结论）**
> Kling 在 arcloop 上**确实可用**，只是**没有独立规格页**（`/models/en-US/kling-omni` 404），入口在**生成器的模型下拉 / Story Settings**。能力数据来自**快手可灵官方文档**（非 arcloop 规格），四个必知：
> 1. **时长 3–15s 整数**，9:16 直选，最高 4K —— **封顶 15s，30s 一镜只能用 Seedance 2.5**；
> 2. **`settings.audio` 默认 `off`** —— ⚠️ **不主动开就是哑片**，这是最容易踩的坑；
> 3. **多镜头默认开**，写法 `shot n, m, words;`（n=1–6，m=秒，各镜头时长之和＝总时长，每镜 prompt ≤512 字符）；
> 4. 提示词上限 **3072 字符**（建议 ≤2500），负面描述**写在 prompt 里**，无独立字段。
> 做「会说中文、会演多镜头」的整活短片先用它；纯氛围 B-roll 用 H3/Vidu 更省事。详见 `arcloop-models.md` §9。

**图 vs 视频的语言**：图片提示词用**中文**（官方自己就在用中文写图片示例）；视频提示词用**英文**（官方建议，镜头术语英文更成熟）。下面的骨架都按这个来。

---

## 2. 通用负面约束段（复制，按需删）

**A. 无人物版（模板 1/2/5/7/9/10/12 用）**
```
负面约束：无文字、无字母、无数字、无伪文字、无乱码字符、无字幕、无水印、无 logo、无招牌、无 UI 标签、无标签牌、无多余的手、无多余的指头、无重复物体、无拼贴感、无镜头光晕、无粒子、无烟雾、无闪烁、无形变。
```
```
Negative constraints: no text, no letters, no numbers, no gibberish characters, no subtitles, no watermark, no logo, no signage, no UI labels, no labels of any kind, no extra hands, no extra fingers, no duplicated objects, no collage look, no lens flare, no particles, no smoke, no flicker, no morphing.
```

**B. 有人物/手版（模板 3/4/6/8/13 用）**——把 `no hands / no faces` 换成 `no recognizable faces`：
```
负面约束：无文字、无字母、无数字、无伪文字、无字幕、无水印、无 logo、无招牌、无 UI 标签、无清晰可辨认的人脸、无重复物体、无拼贴感、无粒子、无闪烁、无形变。
```

**C. 视频版（所有出片模板用）**
```
Negative constraints: no text, no letters, no numbers, no subtitles, no watermark, no logo,
no camera shake, no flicker, no morphing, no duplicated limbs, no scene cut, no added objects,
no readable markings anywhere.
```

> ⚠️ **矛盾自检**：如果这镜本来就要手（模板 13）、要慢动作、要颗粒感，**先把对应条目删掉**再粘。`no hands` + `hand enters` 会让模型两头摇摆。

---

## 3. 变量表（所有骨架共用）

| 变量 | 含义 | 举例 |
|---|---|---|
| `[主体]` | 这条新闻的主角（**抽象化**：发光方块/陶俑/机器人/剪影，不是真 logo） | `一个深蓝色发光方块`／`一个陶俑将军` |
| `[对手]` | 对立面 | `一个灰色金属方块`／`一叠空白的重置卡` |
| `[数字]` | 要后期贴的关键数字 | `13 : 0`／`10/23`／`-67%` |
| `[日期]` | 窗口锚点 | `10/23` |
| `[坐骑]` | 骑乘模板的坐骑 | `鹈鹕`／`北极熊`／`扫地机器人` |
| `[场景]` | 生活化场景（**越日常越好**） | `便利店门口`／`县城篮球场`／`地铁站台` |

---

# 正文：14 个模板

---

## 模板 1｜比分对决（把事件做成一边倒的比分）

**梗公式**：把 A 和 B 做成比分 `A 13 : 0 B`，用赛事级包装（比分板 + 解说腔），悬殊到一眼看出是玩笑。

| | |
|---|---|
| **机制** | B 对决 |
| **适用新闻** | 降价 / 免费 vs 付费 / 额度重置 / 封杀 vs 放开 / 新模型吊打旧模型 / 开源 vs 闭源 |
| **借势窗口** | 不限。VCT 决赛期（10/18 前后）最佳，可现在只剩长尾；LOL 瑞士轮比赛日可借 |
| **风险** | **L2 中**。比分必须夸张到不可能当真；**不出现真实队名/队标/官方 UI** |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，室内篮球馆高机位俯拍，画面中央是两块对置的巨大空白电子比分板，板面朝镜头微微倾斜，
两块板中间是一条光带，把场地劈成两半。
左半边站着一个深蓝色【[主体]：一个深蓝色半透明发光方块，边缘有细密电路纹理】，体量巨大，占据左侧三分之二；
右半边站着一个灰色【[对手]：一个灰色哑光金属方块】，只有左侧的三分之一高，显得很小。
场地地面是深色木地板，反光能照出两个影子的长短差。
顶光 5600K 冷白 + 右侧一盏 3200K 暖色侧逆光，空气里有轻微的体积雾。
留白：画面上方 20% 保持干净暗部（后期贴比分），下方 25% 保持低细节（后期贴字幕）。
负面约束：（粘贴 §2-A）
```
**出片骨架（可选，做 6–8s 卡点更带感）**— MiniMax H3（卡点切）
```
Wide static shot of a dark basketball court from a high angle. Two glowing blocks face each other across a light strip.
Action: the left blue block pulses once and grows slightly taller; the right grey block shrinks a little;
both settle. Camera: one slow push-in only, then comes to rest.
Lighting: cold 5600K top light with one warm rim from the right; light haze in the air.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**（所有文字都在这一步加）
| 位置 | 内容 | 样式 |
|---|---|---|
| 上方 15% | `13 : 0`（或 `免费 : 收费`） | 超粗无衬线，白字黑描边，占宽 60% |
| 左下角 | `[主体名] vs [对手名]`（**不写真实队名**） | 中号，等宽字体 |
| 底部安全区 | 一句解说腔字幕 | 见下 |

**字幕文案（3 变体）**
1. `裁判都没反应过来——13:0，直接带走。`
2. `[主体] 一分没让，[对手] 连暂停都来不及叫。`
3. `解说：这一局已经没有悬念了，让我们把镜头给到对手的定价页。`

**避坑**
- 比分数字**必须离谱**（13:0、100:0），现实里真有的 3:0 不要拿来当「我们赢了」的证据；
- 比分板**空白出图**，数字后期贴——让模型画数字必崩；
- 别用真实赛事 UI 配色 + 真实队标组合，那是 L3。

---

## 模板 2｜电影海报 parody（把 AI 事件做成一张电影海报）

**梗公式**：`[电影海报构图] × [AI 事件]` + 一句 tagline，片名就是新闻本身。

| | |
|---|---|
| **机制** | C 预告 |
| **适用新闻** | 封杀 / 许可证未公布 / 大版本发布 / 裁员 / 事故 / 融资 |
| **借势窗口** | 正预热期的电影最猛（**《复仇者联盟5：毁灭之日》12/16 内地上映**，11 月中起动手）；万圣节档（10/25 起）适合惊悚向 |
| **风险** | **中高**。电影 IP 商标密集：借构图不借 logo |

**出图骨架**（Seedream 5 Pro 或 GPT Image 2.5 Sunburst，9:16，2K）
```
9:16 竖版电影海报构图。画面下方三分之一是一个背对镜头的黑色剪影人物，站在一条空旷的公路尽头；
人物很小，天空占据画面上方三分之二，天空是压得很低的暗金色积雨云，云缝里透出一道垂直的冷光，
光柱正好落在剪影头顶。公路两侧是烧焦的荒草，远处几个模糊的巨型轮廓（不要清晰可辨）。
整体是「史诗灾难片」的色温：青灰底 + 一道琥珀金的主光，颗粒感适中，暗部有层次。
片名区：画面最下方 22% 是一条干净的深色渐变带，没有任何文字和图案（后期贴片名）。
tagline 区：剪影上方留 1 行干净的低细节天空。
负面约束：（粘贴 §2-A）
```
**出片骨架（可选，8–10s 氛围）**— Seedance 2.5 或 Vidu Q4（用上图作首帧）
```
Image-to-video, keep the frame composition and the figure silhouette unchanged.
Action: the vertical light beam brightens once, then fades; the low clouds drift slowly to the left;
the figure's shoulders rise a little as it breathes in. Camera: one very slow push-in, then comes to rest.
Lighting: keep the teal-grey base and the single amber beam; do not change the light direction.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 底部 22% 深色带 | **片名**：`《[事件名]》` | 宋体/黑体超粗，白字；**自己排版，不复刻任何电影官方字体** |
| 片名上方 | tagline：一句反转短句 | 小号细体，字距拉开 |
| 片名下方 | `[档期] 上映`／`暂未定档` | 最小号，必须真实 |

**字幕文案（3 变体）**
1. 片名《许可证》：`10 月 23 日，全国上映（暂未定档）`
2. 片名《最后一个人类员工》：`他不是被裁的，他是自愿的。`
3. 片名《重置》第二季：`这一次，按钮真的丢了。`

**避坑**
- **改结构不改 logo**：不要 P 漫威/任何片厂 logo，不要用官方剧照，不要复刻官方标题字；
- 「暂未定档」「预计」这类词必须有时间锚点（如「截至 10/20 未公布」），否则就是把猜测说成事实；
- 海报里的片名是**你的作品名**，不是那部真电影的名字——不要写成「复联 5 定档 12/16」这种会被当新闻转的句式。

---

## 模板 3｜赛事解说 / 转会窗式（把模型发布讲成转会官宣）

**梗公式**：把 `[主体]` 的发布/跳槽/合作，讲成「转会官宣 + 解说三连」，用体育媒体的话术包装一条产品新闻。

| | |
|---|---|
| **机制** | B 对决（软对抗）+ 置换（壳换成体育） |
| **适用新闻** | 模型发布 / 团队挖人 / 公司合作 / 开源权重开放 / 平台上线 / 融资 |
| **借势窗口** | **LOL 世界赛瑞士轮（10/21 起比赛日）**；VCT 已结束只剩长尾 |
| **风险** | **L2 中**。可提赛事名与赛制，不伪造对阵；不出现选手真脸与队标 |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，体育转会官宣式的发布会现场：一张深色长桌，桌后坐着一个【[主体]：深蓝色半透明发光方块】，
方块前方摆着一件完全空白的球衣（无号码、无队徽、无任何字样），球衣是深蓝色配金色描边。
桌面反光，背景是一面巨大的空白背景板（无 logo、无字样），板前有一排长枪短炮的相机剪影。
闪光灯在空气里拉出几道短促的白色光斑，右侧补充一盏 3200K 暖光打亮球衣肩线。
上方 18% 留干净暗部（后期贴官宣大字），下方 25% 留低细节（后期贴字幕）。
负面约束：（粘贴 §2-B）
```
**出片骨架（6–8s）**— MiniMax H3（便宜快）／**Kling 3.0 Omni**（要「中文解说腔」就选它，见下方 B 方案）
```
Medium shot of a dark press-conference table. A glowing blue cube sits behind it; a blank blue jersey with gold trim
is laid flat on the table in front. Action: camera flashes pop three times in quick succession, each pop briefly
brightening the jersey; the cube's glow pulses once in sync; then everything comes to rest.
Camera: one slow push-in only. Lighting: keep the warm 3200K key on the jersey shoulder line.
Negative constraints: （粘贴 §2-C）
```
**B 方案（要原声解说就换这个）**— **Kling 3.0 Omni**，3–15s，多镜头打开，**记得手动开 audio**
```
Vertical 9:16, 12 seconds, multi_shot on.
shot 1, 4, words; Medium shot of a dark press-conference table. A blank blue jersey with gold trim lies flat on it.
Camera flashes pop twice; the jersey shoulder flashes white each time.
shot 2, 4, words; Low angle on a glowing blue cube behind the table, its edge light pulsing once as a hard key
light sweeps across it and settles.
shot 3, 4, words; Wide shot of a blank backdrop wall, three camera flashes fire in sequence from the lower-left
corner, then everything comes to rest.
Audio: neutral male Mandarin commentary voice, calm broadcast tone, low in the mix behind room tone.
No background music, no crowd noise.
Negative constraints: 无文字、无字母、无数字、无 logo、无队标、无招牌。
```
> ⚠️ Kling 的 `audio` 默认 **off**，不开就是哑片；台词内容**自己写死**，别让它自由发挥出真实队名/选手名。中文提示词在 arcloop 上是否完全可用**未公开**，首条先小成本试。

**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 上方 18% | `官宣` / `HERE WE GO`（**用通用词，不用真实媒体名**） | 超粗白字，带轻微倾斜 |
| 球衣胸口 | `[主体名]` —— **在后期叠在胸口的空白区**，不要写号码 | 中号，白色 |
| 底部 | 解说三连 | 见下 |

**字幕文案（3 变体）**
1. `转会窗关闭前 1 小时，[主体] 官宣加盟。合同细节未披露，但据说附带 200 万 token 签字费。`
2. `解说：这笔引援太关键了，[主体] 一来，中前场的上下文长度直接翻倍。`
3. `官方还没发公告，但球衣已经挂上了——第 [N] 号，名字叫 [主体]。`

**避坑**
- **球衣必须空白出图**，名字后期贴（模型画球衣号码会崩，也是伪造队服的入口）；
- 不写真实俱乐部名、不做「官宣海报」的官方样式复刻；
- 「官宣」是你的叙述语气，**不代表厂商真的官宣** → 字幕里要么写「我们宣布」，要么写「（玩梗）」。

---

## 模板 4｜荒诞骑乘（鹈鹕骑车 / 秦始皇骑熊式）

**梗公式**：`[熟悉场景] × [不该出现的坐骑] × [我们的主体]`，让主体骑着一个荒谬的东西出现在最日常的地方。

| | |
|---|---|
| **机制** | A 置换（这是最正宗的一种） |
| **适用新闻** | 额度重置 / 发布 / 降价 / 事故 / 任何「它在跑」的新闻 |
| **借势窗口** | 常青。**鹈鹕骑车已 benchmark 化**（OpenRouter Sketch benchmarks 有分类页），认知度最高；北极熊在传 |
| **风险** | **L1 低**（自己生成，不搬别人图）→ 但涉及历史人物（秦始皇）时升到 **L2 中低** |

**参考锚点（写提示词前看这个）**
- **鹈鹕骑车**：原点是 Simon Willison 的测试题「画一只骑自行车的鹈鹕」，2026 年已进 OpenRouter 的 sketch benchmark，并被 36Kr 写成「Agent 时代顶流明星」→ 你画一只骑车的鹈鹕，**观众有现成认知，不用解释**。
- **秦始皇骑北极熊**：B 站二创《秦始皇骑北极熊》验证了「千古一帝 ÷ 离谱坐骑」的可行；坐骑越荒谬、场景越日常，反差越大。

**坐骑池（按荒诞度/认知度）**：`鹈鹕 > 北极熊 > 鲸鱼 > 鸵鸟 > 扫地机器人 > 复印机 > 带轮子的服务器`。
⚠️ **不要用恐龙/赛博机械兽**——太像美术设定，不像梗。

**出图骨架**（Seedream 5 Pro，16:9 或 9:16，2K）
```
【真实感优先】照片级写实，午后强光，[场景：县城便利店门口的柏油路]。
画面主体是一只体型被放大到摩托大小的【[坐骑]：一只羽毛蓬乱的鹈鹕】，正用两条橘色腿吃力地蹬着一辆
掉漆的共享单车，单车后座上侧坐着一个【[主体]：一个深蓝色半透明发光方块，用两根细长的金属支架扶住车把】。
方块表面有细微的电路纹理在反光，鹈鹕脖子上的皮褶随着用力一抖一抖，车轮压过地面一小滩积水，溅起几滴。
背景有几辆停歪的电动车和一个塑料袋，远处是关了一半的卷帘门。
光线：正午顶光偏硬，路面蒸腾感，色温偏暖，轻微过曝，手机随手拍画质。
留白：上方 20% 干净天空（后期贴大字），下方 20% 低细节路面（后期贴字幕）。
负面约束：（粘贴 §2-B）
```
**出片骨架（5–8s，这条最值得做视频）**— Vidu Q4 image-to-video（用上图作首帧）
```
Image-to-video, keep the frame composition exactly.
Action: the pelican pedals twice, its neck bobs with the effort; the glowing cube on the back seat sways slightly
and its grip tightens; the bicycle rolls forward half a metre into the puddle and the spray flashes once in the
sunlight; then the wheels slow and come to rest.
Camera: one slow tracking follow from the side, then stop.
Lighting: keep the hard midday sun and the warm overcast tone; keep the wet-road highlights.
Negative constraints: （粘贴 §2-C）
```
**B 方案（让鹈鹕/坐骑开口说话）**— **Kling 3.0 Omni**，3–15s，多镜头 + 元素配音 + **手动开 audio**
```
Vertical 9:16, 8 seconds, multi_shot on.
shot 1, 4, words; Side tracking shot of a motorcycle-sized pelican pedalling a battered shared bicycle along a
sunlit suburban street, a glowing blue cube riding on the back seat, its metal supports gripping the handlebars.
The bike rolls through a puddle and the spray flashes once.
shot 2, 4, words; Close-up of the pelican's head turning to camera, beak slightly open, neck feathers ruffled,
then it looks forward again and settles.
Audio: the pelican speaks one short line in tired Mandarin, dry deadpan tone, no music, ambient street noise only.
Negative constraints: 无文字、无字母、无数字、无 logo、无招牌、无清晰人脸。
```
> 用法：把 `[坐骑]` 换掉、把 `Audio:` 那行的台词换成**你写的**一句吐槽（例如「我不懂 AI，我只知道他每天坐我后座不付钱」）。⚠️ 台词**必须自己写死**，不要让模型自由发挥；不出现真人脸。

**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 上方 | `[主体] 骑鹈鹕上班` 一类荒诞短句 | 粗黑体，白字黑边 |
| 底部 | 一句反转 | 见下 |

**字幕文案（3 变体）**
1. `[主体] 不会开车，但它会骑鹈鹕——而且它已经在路上了。`
2. `别人骑马，它骑鹈鹕。别人卷价格，它卷交通工具。`
3. `鹈鹕：我不懂 AI，我只知道他每天坐我后座不付钱。`（**换视角 = 白送一层笑点**）

**避坑**
- **不要直接搬 36Kr / Simon Willison 的图**，自己生成；
- 用秦始皇等历史人物时：**自己生成风格化陶俑**，不要用真实兵马俑照片；不做政治隐喻；
- 荒诞骑乘的笑点全在「写实」——所以提示词要写**手机随手拍、过曝、日常场景**，写成赛博朋克就死了；
- 视频别超过 8s，动作一停就立刻收；
- 用 Kling 让坐骑说台词时：**audio 必须手动开**（默认 off），台词自己写死。

---

## 模板 5｜音乐卡点（歌词字幕 + 画面按拍切）

**梗公式**：选一段**节奏明确**的段落，画面每 0.5–1 秒切一次，字幕跟着歌词走，让「新闻」变成「MV」。

| | |
|---|---|
| **机制** | A 置换 + 节奏强化 |
| **适用新闻** | 多模型连发 / 一周综述 / 降价连环 / 排队抢号 / 发布会亮点 |
| **借势窗口** | 常青。**不依赖某首歌**——用节拍而不是用具体热歌，避免版权和过期两重坑 |
| **风险** | **中**（BGM 版权是主要风险，不是画面） |

**BGM 决策（先定这个，否则白做）**
1. 优先用**平台曲库**（抖音/小红书内置商用曲库），个人号也安全；
2. 想用热门流行曲 → 先查授权，**带货/商单场景别用**；
3. 完全没把握 → **Seed Audio 1.0 出一段同风格配乐**（`Soundtrack: 120bpm, four-on-the-floor, 8 bars`），版权干净。

**出图骨架（做首帧）**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，livehouse 舞台侧后方机位，一束从地面打上来的青色追光穿过薄雾。
舞台中央立着一个【[主体]：深蓝色半透明发光方块】，被支架架在麦架上，方块前方立着一支老式金属立麦。
舞台边缘有返听音箱和几圈缠住的话筒线，地板是磨花的黑色胶地，被光照出一道道划痕。
背景全黑，只有追光切开的一小片空气是亮的，雾里有细小的尘粒。
下方 25% 是干净的暗部地面（后期贴歌词字幕）。
负面约束：（粘贴 §2-A）
```
**出片骨架（3–4 个镜头，每个 1.5–2s，H3 卡点切）** — MiniMax H3（官方 shot-type map 点名卡点用它）
```
Shot 1: close-up of the metal microphone stand, the glowing cube reflected in its chrome surface.
Action: one harsh strobe flash hits the chrome; the reflection flares then settles.
Camera: locked off. Lighting: single cyan floor-up beam, no fill.
Negative constraints: （粘贴 §2-C）
```
```
Shot 2: medium shot, the glowing cube on the stand pulses on each beat. Action: the cube brightens and dims
three times, the haze around it swirls once. Camera: locked off, no movement. Lighting: same cyan beam.
Negative constraints: （粘贴 §2-C）
```
```
Shot 3: wide shot of the empty stage, one follow spot sweeping across the floor from left to right and stopping
at centre. Action: the sweep ends, the beam locks, then holds. Camera: one pan only.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**：字幕固定在**画面下三分之一**，一行最多 8 字，跟拍切点换行；关键数字放大一号。

**字幕文案（3 变体，配节拍）**
1. 副歌位：`发布（拍）降（拍）价（拍）再（拍）降（拍）` —— 一字一拍
2. `这一周：三个模型，两次降价，一次宕机（重拍）`
3. `他们说这是比赛（拍）其实这是流水线（拍）`

**避坑**
- **画面里绝对不出现歌词文字**，歌词是后期字幕；
- 每镜 1.5–2s，**别指望一个 15s 镜头卡鼓点**——卡点在剪辑台上完成，不靠模型；
- 用「节拍」不用「某首歌」是刻意的：热歌半衰期短，节拍永不过期。

---

## 模板 6｜突发新闻插播（Breaking News）

**梗公式**：把事件包装成「紧急插播」——红色警报条 + 空演播台 + 倒计时，用新闻的严肃感反衬内容的荒唐。

| | |
|---|---|
| **机制** | 置换（壳＝电视新闻） |
| **适用新闻** | 宕机 / 事故 / 封杀 / 突然降价 / 权重泄漏 / 抢额度 |
| **借势窗口** | 任何突发事件当天。**突发类时效性最强：4 小时内发** |
| **风险** | **L2 中**。不能伪造真实媒体台标，不能冒充官方公告 |

**出图骨架**（GPT Image 2.5 Sunburst 或 Seedream 5 Pro，16:9 或 9:16，2K）
```
新闻演播室，正面机位。画面中央是一张深灰色主播台，台上放着一杯水和一叠空白稿件；
主播位是空的，椅子还转着，麦克风悬在半空。
背景是一面巨大的深蓝色屏幕墙，屏幕完全空白（无任何图形、无字样），屏幕墙被一道从左侧打来的
红色警报光扫过，把主播台边缘染红。
天花板上有两盏红色的警报灯正在亮，光打在雾里形成两道红色光柱。地面是深色反光材质。
下方 25% 留低细节暗部（后期贴红色警报条和字幕），上方 12% 留暗部（后期贴台标位置，但不放真实台标）。
负面约束：（粘贴 §2-B）
```
**出片骨架（6s）**— Seedance 2.0 或 MiniMax H3
```
Front-facing news studio shot, empty anchor desk, blank screen wall behind.
Action: the two red ceiling alarm lights rotate left to right and back once, sweeping red beams across the desk;
the empty chair turns slowly a few degrees and comes to rest; a sheet of paper on the desk lifts at the corner
in the draft. Camera: locked off, no movement. Lighting: keep the red alarm beams and the cold blue fill.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 顶部 12% | 你自己设计的**抽象台标**（不是真实台标） | 白字 |
| 底部 25% | 红色警报条：`BREAKING` + 事件一句话 | 红底白字，滚动 |
| 中段 | 大号数字/时间 | 等宽字体 |

**字幕文案（3 变体）**
1. `【突发】[主体] 的额度又没了。本台记者正在赶往服务器机房。`
2. `插播一条：原定今天发布的东西，今天可能不发布了。`
3. `我们刚刚收到消息——（停顿）——它说它在修。`

**避坑**
- **台标必须是你自己设计的抽象标记**，不能是 CNN/BBC/央视等真实台标（伪造媒体 = 高处罚风险）；
- 警报条里的事件描述必须是真的，**只有包装是假的**；
- 「突发」这个词会拉高期待，里面要是没信息，完播会崩。

---

## 模板 7｜审判 / 开庭（许可证没公布 → 开庭）

**梗公式**：把一个悬而未决的问题（许可证、合规、价格、真实性）做成「开庭审理」，被告是问题本身。

| | |
|---|---|
| **机制** | C 预告 + 置换（法庭） |
| **适用新闻** | 许可证未公布 / 条款含糊 / 版权纠纷 / 数据来源存疑 / 官方说法前后矛盾 |
| **借势窗口** | 常青。**「未公布」类事件的最佳模板**——事件没进展时，可以审「为什么没进展」 |
| **风险** | **L2 中**。法庭是敏感场景，不出现真实法官/真实法院徽章 |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，空法庭内部，仰视机位。画面中央是空着的证人席，木栏上有细密的划痕和一层薄灰。
证人席的台面上放着一个【[被告]：一块透明的空白亚克力立牌】，立牌上什么都没有，边缘反着窗光。
背景是两排空着的旁听席，木头长椅，光线从高窗斜切进来，光柱里有缓慢飘动的灰尘。
整体是旧法院的色调：深棕木 + 冷灰石墙 + 一道从高窗进来的 5600K 冷光。
下方 28% 留干净的深色木地板（后期贴判决字幕），上方留高窗的亮部。
负面约束：（粘贴 §2-A）
```
**出片骨架（5s）**— MiniMax H3
```
Low-angle shot of an empty courtroom witness stand, a blank acrylic placard standing on it.
Action: a shaft of window light slides slowly across the placard's surface, a single dust mote drifts through it,
the placard's reflection on the polished wood stretches then shrinks; then everything stills.
Camera: one slow tilt up, then comes to rest. Lighting: cold 5600K shaft only, deep shadow elsewhere.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 上方 | `开庭` / `第 [N] 次开庭` | 宋体，白字，居中 |
| 中段立牌位置 | `被告：[问题]` —— 后期叠在白牌上 | 黑体 |
| 底部 | 判决/延期字幕 | 见下 |

**字幕文案（3 变体）**
1. `被告：许可证。罪名：迟迟不出庭。本次庭审延期，下次开庭时间未知。`
2. `法官：你说你 23 号开放权重，那许可证呢？被告：……（休庭）`
3. `本庭宣判：[主体] 无罪，罚写更新日志三千字。`

**避坑**
- 不用真实法院徽章、不出现法官真脸、不做国徽；
- 「判决」是你的玩笑，**不能写成法律意见**（`07-compliance.md` §5）；
- 涉及许可证/合规的真实细节时，只陈述「未公布」+ 日期，不做推断。

---

## 模板 8｜招聘 / 裁员式（AI 取代岗位）

**梗公式**：把 AI 的进展做成一张「招聘广告」或一份「裁员通知」，岗位写的是人的工作。

| | |
|---|---|
| **机制** | A 置换（壳＝招聘广告 / 办公场景） |
| **适用新闻** | 裁员 / 岗位替代 / Agent 上岗 / 自动化 / 外包 / 「AI 员工」 |
| **借势窗口** | 常青，裁员新闻当天最佳 |
| **风险** | **L1 低**（不点名具体公司/真人时）。**点名公司 → 中高**（商誉风险） |

**出图骨架**（GPT Image 2.5 Sunburst，9:16，2K）
```
9:16 竖版，一间空置的开放式办公室，纵深机位。一排排工位整齐延伸向背景，所有椅子都是空的，
桌上只有一台台亮着冷白屏保的显示器（屏幕内容不可辨），没有一个坐人。
最近处的工位上贴着一张完全空白的白纸（无字样），椅背上搭着一件灰色外套。
地面是灰色地毯，格子隔断的顶端反着天花板的条形灯。
光线：天花冷白条形灯 + 从落地窗进来的午后暖光斜切在地毯上，形成冷暖对照。
上方 20% 是干净的暗色天花板（后期贴招聘大字），下方 25% 是低细节地毯（后期贴字幕）。
负面约束：（粘贴 §2-B）
```
**出片骨架（8–10s，镜头往纵深推最压抑最带感）**— Seedance 2.5 / H3
```
Wide shot of an empty open-plan office, rows of vacant desks receding into the background.
Action: the overhead strip lights flicker on one by one from the back of the room towards the camera, each one
lighting up a new row of empty monitors; a grey jacket on the nearest chair back slips a centimetre and settles.
Camera: one steady dolly forward along the centre aisle, then comes to rest.
Lighting: cold overhead strips plus a warm afternoon shaft from the window on the right.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 上方 | `招聘` / `岗位：[人的工作]` | 粗黑体 |
| 底部 | `岗位职责` 三行（越正经越好笑） | 小号，等宽 |
| 右下 | `薪资面议` | 最小号 |

**字幕文案（3 变体）**
1. `岗位：[你的工作]。要求：不用睡觉。薪资：你的薪资。`
2. `我们不是在裁员，我们是在给岗位做一次「模型升级」。`
3. `HR：这个岗位以后只招一个人，负责给 AI 点「继续」。`

**避坑**
- **不要点名具体公司裁员**（商誉 + 事实风险）→ 说「某公司」「一家做 XX 的公司」；
- 不出现真人照片、不做出真实企业的内部文件样式；
- 笑点要落在「制度荒诞」而不是「嘲笑失业的人」——后者会被反噬。

---

## 模板 9｜价格战擂台（称重 / 对轰 / 打价）

**梗公式**：把两家的定价做成「拳击称重 / 打擂台」，谁降价谁出拳，价格用大数字后期砸出来。

| | |
|---|---|
| **机制** | B 对决 |
| **适用新闻** | 降价 / 免费额度 / 按次计费 / 订阅涨价 / 开源 vs 闭源定价 |
| **借势窗口** | 常青。**10/19 谷歌「白菜价打赢 Pro」的讨论正在传**；DeepSeek 按次计费新闻可搭 |
| **风险** | **L2 中**。不贴真实 logo、不伪造「官方降价公告」 |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，拳击擂台赛前的称重台，正面略仰机位。画面中央是一台老式机械台秤，
秤台上放着【[主体]：一个深蓝色半透明发光方块】，秤的指针区域被设计成完全空白的圆形刻度盘（无数字）。
台秤右侧的地面上放着【[对手]：一个灰色哑光金属方块】，明显比秤上的小。
背景是一面完全空白的深红色幕布，幕布上方打下一束强烈的顶光，空气中有灰尘在光里翻。
地面是磨旧的木地板，有胶带贴出的站位标记（无字样）。
下方 25% 留干净地板（后期贴价格数字）。
负面约束：（粘贴 §2-A）
```
**出片骨架（6s）**— MiniMax H3 Max Turbo（可用首尾帧：结尾定格在指针处）
```
Medium shot of an old mechanical weighing scale on a wooden platform, a glowing blue block resting on the pan.
Action: the block settles onto the pan, the blank dial's needle swings once hard to the right, overshoots, then
swings back and comes to rest. Camera: locked off, no movement. Lighting: one hard top spot through dust.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 指针处 | `[价格]` 大数字（如 `$0.15`）砸在刻度盘上 | 超粗，白字红描边 |
| 顶部 | `[主体] vs [对手]` | 中号 |
| 底部 | `第 [N] 回合` | 小号 |

**字幕文案（3 变体）**
1. `第一回合：对方降 30%，[主体] 直接砍到脚踝。比赛结束。`
2. `称重结果出来了——[主体] 比对手轻 3 倍，快 2 倍，便宜 1 个数量级。`
3. `裁判：[主体] 这一拳打的是性价比，对手表示要回去改定价页。`

**避坑**
- 价格数字**必须有出处**（官方定价页），别估算；
- 刻度盘**空白出图**，指针是模型画的，数字是后期贴的——两者分开；
- 用「降维打击」类说法时注意广告法：**绝对化用语要么有评测出处，要么改口**（`07` §3）。

---

## 模板 10｜时间轴 / 倒计时（Day N）

**梗公式**：把「还有几天 / 第几天」做成一块巨大的物理倒计时牌，数字是唯一的信息量。

| | |
|---|---|
| **机制** | C 预告（悬念） |
| **适用新闻** | 权重开放日 / 发布会倒计时 / 「第 N 天没重置」/ 预测窗口 / 截止日期 |
| **借势窗口** | **今天最该用**：Tibo 重置间隔推算窗口（10/20–10/21）；**MiniMax M3.1 Flash 权重 10/23 开放** |
| **风险** | **L1 低**。⚠️ 但「预测」必须标「预测」，不能写成「已确认」 |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，一块立在旷野里的巨型翻页倒计时牌（机场/车站那种），仰视机位。
牌面由十几个空白翻页卡片拼成，所有卡片都是空白的深灰色（无数字、无字样），
有几张卡片卡在半翻的状态，露出一点侧边。
倒计时牌立在龟裂的盐碱地上，远处地平线很低，天空是厚重均匀的铅灰色积云，云层下缘透出一线橙红。
地面有一小片积水，倒映着牌子的轮廓和那一线橙红。
光线：阴天散射光为主，唯一的暖光是地平线那一线橙红，冷灰是主调。
上方留出积云（后期贴标题），下方 25% 是低细节盐碱地（后期贴数字）。
负面约束：（粘贴 §2-A）
```
**出片骨架（5s，翻页感最佳）**— MiniMax H3 Max Turbo 或 **Kling 3.0 Omni**（**这里用首尾帧**：首帧牌面完整，尾帧一张卡片翻到一半）
```
Wide low-angle shot of a giant split-flap countdown board standing in a salt flat.
Action: a few of the blank grey flaps flip over one after another and settle; the reflection in the puddle
shivers once. Camera: locked off, no movement. Lighting: overcast flat light with one thin orange band at
the horizon staying unchanged.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 牌面 | 大数字 `[N]` 或 `[日期]` —— 逐张卡位对齐 | 等宽超粗，做旧 |
| 顶部 | `距 [事件] 还有 [N] 天` | 中号 |
| 底部 | 一行小字说明这是预测（**必须有**） | 最小号 |

**字幕文案（3 变体）**
1. `第 [N] 天，重置还没来。按前三次的间隔算，窗口在今天或明天。（预测）`
2. `距权重开放还有 [N] 天。牌子上不会写，但我们数着。`
3. `Tibo 上次是 47 小时，再上次 64 小时。今天是第 [N] 小时——我们不催，我们只是路过。`

**避坑**
- **预测必须写明是预测**，并且给推算依据（前三次时间 + 间隔），错了才有台阶下；
- 牌面数字是后期贴的，卡位要**一张一张对齐**，贴歪了整套质感就废；
- 别用「倒计时」包装不确定的事（比如「许可证 3 天内公布」），那是造谣。

---

## 模板 11｜期望 vs 现实（表情包对照）

**梗公式**：左图「你以为的」/ 右图「实际上的」，两格并置，落差本身就是笑点。

| | |
|---|---|
| **机制** | A 置换（壳＝对比图） |
| **适用新闻** | 宣传 vs 实测 / benchmark 翻车 / 你的 prompt vs 它出的图 / 发布会 vs 上线后 |
| **借势窗口** | 常青。**「AI 为什么总在画美女」这个话题正在传**（36Kr 专稿），可正面接 |
| **风险** | **L1 低** |

**出图骨架**（GPT Image 2.5 Sunburst，3:4/9:16 后裁，2K）—— **一次出两格，中间留白缝**
```
竖版对比图，左右两格，中间一条 8px 宽的白色分隔缝。
左格：极干净、极规整的科幻城市，玻璃幕墙反着整齐的蓝天，构图完美对称，色调冷白，像官方宣传图；
右格：一模一样的场景，但玻璃幕墙歪倒、天空是浑浊的橙灰、街边停着一排歪七扭八的共享单车，
远处有一个巨大的、看起来不对劲的模糊物体（不要清晰可辨）。
两格的机位、焦距、构图完全一致（这点最关键），只有「完成度」差了一个世界。
光照：左格是干净的 5600K，右格是脏掉的 4300K 加一层灰霾。
每格上方 18% 留干净的空白区（后期分别贴两格标题）。
负面约束：（粘贴 §2-A）
```
**出片骨架（可选 4s，右格轻微抖动）**— MiniMax H3
```
Split-screen shot, a clean sci-fi city on the left and its ruined version on the right, identical camera.
Action: on the right panel only, a bent roadside sign wobbles once and stops; dust drifts. Left panel stays
perfectly still, no movement at all. Camera: locked off for both. Lighting: left clean 5600K, right hazy 4300K.
Negative constraints: （粘贴 §2-C）+ "the two panels must keep identical perspective"
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 左格上方 | `期望` / `发布会上的样子` | 白字 |
| 右格上方 | `现实` / `你实际用到的样子` | 白字，略抖/略斜 |
| 底部 | 一句反转 | 见下 |

**字幕文案（3 变体）**
1. `期望：一句话生成电影。现实：一句话生成了六个手指。`
2. `我让它画赛博城市，它给我画了个美女。这也是赛博。`
3. `发布会：[主体] 什么都能干。上线后：什么都能干，就是不太能干对。`

**避坑**
- **两格机位必须一致**，否则读者会以为是两张不同的图，梗就散了（提示词里要强调 `identical camera`）；
- 不嘲讽具体使用者，嘲讽「宣传/现实的落差」；
- 「六个手指」是安全的梗，但**别真让模型画六根指头当卖点**，那会被当质量事故转。

---

## 模板 12｜排行榜 / 奖杯（颁奖礼）

**梗公式**：给事件颁一个奖——奖杯、领奖台、背景板，奖名自己编（越正经越好笑）。

| | |
|---|---|
| **机制** | B 对决（软排名） |
| **适用新闻** | 榜单 / 评测 / 融资 / 下载量 / 融资额 / 用户数 / 年度总结 |
| **借势窗口** | 常青；**Anthropic 5% 股份公益基金**这类「姿态类」新闻适合颁「最佳配角奖」 |
| **风险** | **L2 中**。排名要有出处；不伪造官方颁奖典礼 |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，颁奖礼舞台，正面平视机位。画面中央是一部三级台阶的白色领奖台（左低中高右中），
台面上是三个空白的金属铭牌（无字样），最高的那一级台阶上立着一座金色奖杯（造型抽象，不是任何真实奖项的造型）。
背景是一面完全空白的深蓝色巨型背景板（无 logo、无字样），板前地面铺着深蓝色地毯。
舞台顶上有三束追光分别打在三级台阶上，空气里有细小的金色纸屑在飘。
奖杯表面有强烈的镜面反光，把追光揉成一团亮斑。
下方 22% 留干净的地毯（后期贴奖项名和名字）。
负面约束：（粘贴 §2-A）
```
**出片骨架（6s）**— Seedance 2.5 / H3
```
Medium shot of a three-tier white podium on a blue carpet, one abstract gold trophy on the top tier.
Action: golden confetti drifts down slowly and settles on the top tier; the trophy catches a single hard
spotlight and a starburst highlight blooms then reduces; the light settles. Camera: one slow push-in.
Lighting: three overhead spotlights, deep blue fill, one strong mirror highlight on the trophy.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**
| 位置 | 内容 | 样式 |
|---|---|---|
| 顶部 | `[奖项名]` | 宋体/黑体，白字居中 |
| 台前铭牌 | 第 1/2/3 名 | 小号，金色 |
| 底部 | 一句吐槽 | 见下 |

**字幕文案（3 变体）**
1. `年度最佳配角奖：[主体]。得奖理由是，它让所有人都便宜了。`
2. `冠军：[主体]。亚军：[对手]。季军：还在改定价页的那位。`
3. `颁奖词：感谢它，让我们的 API 账单第一次出现了「↓」这个符号。`

**避坑**
- 排名**必须有出处**（哪个榜、哪一期、谁排的），没出处就改成「网友投票」「我们瞎排的」；
- 奖杯**造型要抽象**，不能做成奥斯卡/金球奖等真实奖项的造型（那是 IP）；
- 背景板不能有真实赞助商 logo。

---

## 模板 13｜重置卡（Tibo 小卡片式：把福利做成一张实体卡）

**梗公式**：把「额度重置」这种虚拟福利，做成一张**可以发到手里的实体卡片**——越具体越好笑。

| | |
|---|---|
| **机制** | A 置换（虚→实） |
| **适用新闻** | 额度重置 / 免费额度 / 优惠券 / 邀请码 / 奖励发放 / 限量开放 |
| **借势窗口** | **现在最好用**。Tibo 原话：「人们都逃出时间线，在街上找我要重置了，我打算做点小卡片发给大家」——这条原话本身就是脚本 |
| **风险** | **中（L2）**。涉及真人 Tibo → 只能抽象化，**不做脸** |

**出图骨架**（Seedream 5 Pro，9:16，2K）
```
9:16 竖版，街头抓拍视角，浅景深。画面中央偏下是一只伸出来的手（只到小臂，手腕戴着一只普通黑色手表），
手里捏着一小叠厚卡纸卡片，卡片是空白的米白色，边缘有轻微的毛边和压痕，像名片。
卡片最上面那张微微翘起，正对着光。
背景虚化的街道：便利店灯箱（无字样）、玻璃门上反着路灯光、模糊的行人身影（面部不可辨）。
光线：傍晚的混合光——便利店的冷白灯箱 + 路灯的暖黄，卡片表面被冷光打亮，边缘挂一层暖色轮廓光。
卡片区域占画面中段，上方 20% 留虚化背景（后期贴大字），下方 20% 留虚化的地面（后期贴字幕）。
负面约束：（粘贴 §2-B，把手部条目改为允许一只手）
```
**出片骨架（5–7s，卡片翻起来那一下最好看）**— MiniMax H3 Max Turbo 或 **Kling 3.0 Omni**（用首尾帧锁「卡片翻起」）
```
Close-up of a hand holding a small stack of blank cream cards at street level, shallow depth of field.
Action: the top card lifts slightly on the breeze, rotates a few degrees, and is caught between finger and thumb;
then it settles back onto the stack. Camera: one very slow push-in, then comes to rest.
Lighting: cold convenience-store light on the card face, warm street-lamp rim on the card edges.
Negative constraints: （粘贴 §2-C）+ "no recognizable faces in the background"
```
**后期贴字**（文字全贴在卡片上）
| 位置 | 内容 | 样式 |
|---|---|---|
| 卡片正面 | `RESET` / `额度已重置` | 极小的字，像真卡片 |
| 卡片一角 | `No.[N]` 序号 | 更小 |
| 卡片背面（做第二张图时） | `第 [N] 次重置 · [日期]` | 手写体 |
| 顶部 | 一句大字标题 | 见下 |

**字幕文案（3 变体）**
1. `Tibo 说他要做点小卡片发给大家。这是第 4 版设计稿。（图：一叠卡片）`
2. `凭此卡可兑换：一次重置。有效期：到下一次重置。`
3. `卡片背面写着：本卡不可转让，但可以截图发群里。`

**避坑**
- **绝不能出现 Tibo 的脸**：手、背影、剪影都可以，脸不行（肖像权，`08` §5）；
- 卡片上用**你自己编的**文案，不要伪造 X 官方卡片/官方物料的样子；
- 「凭此卡兑换」只是梗，**不能让人真以为有实体福利**——字幕要有一句「（玩梗）」或明确是设计稿。

---

## 模板 14｜补丁说明 / 更新日志 parody（把发布做成 2.0.1 patch notes）

**梗公式**：把一条新闻写成游戏 `Patch Notes`：`新增 / 修复 / 已知问题` 三段式，越像正经日志越好笑。

| | |
|---|---|
| **机制** | 置换（壳＝游戏更新界面） |
| **适用新闻** | 小版本迭代 / 修 bug / 改额度 / 调价 / 悄悄改条款 / 「更新了但没更新什么」 |
| **借势窗口** | 常青，随时可用。**现成素材**：Tibo 相关的神评论「如果让 Tibo 来发布 DeepSeek 的新模型：第一天提速…第二天重置…第二十八天发 v4.5 天王星 Ultra fast」 |
| **风险** | **L1 低** |

**出图骨架**（GPT Image 2.5 Sunburst，16:9 或 9:16，2K）
```
深色游戏启动器界面截图风格，暗色 UI。画面左侧是一列纵向排列的半透明深灰色面板（像更新日志的条目卡），
每张卡片内部都是空的、只有一道细发光的分隔线；右侧是一大块暗色留白区。
屏幕底部有一条水平进度条，进度条是空的、未填充，两端有细小的发光端点。
整体是深蓝黑主色 + 青蓝色高光，卡片边缘有极细的 1px 描边和轻微玻璃反光，UI 上有细致的磨砂质感。
构图：左侧卡片占 55% 宽，右侧留白供后期贴大标题；底部进度条占 8% 高。
负面约束：（粘贴 §2-A）+ "no interface labels, no menu items, no icons with text"
```
**出片骨架（5s，进度条爬升）**— Seedance 2.0 / H3
```
Screen-recording style shot of a dark game launcher UI, static camera.
Action: the horizontal progress bar at the bottom fills slowly from left to right up to about 15 percent, then
stops; the thin glowing border on the leftmost panel brightens once; then everything holds still.
Camera: locked off, absolutely no movement, no parallax.
Lighting: keep the deep blue-black base and the cyan edge highlights only.
Negative constraints: （粘贴 §2-C）
```
**后期贴字**（全部后期叠在 UI 上，像真补丁说明）
| 位置 | 内容 | 样式 |
|---|---|---|
| 左侧卡片 1 | `新增` + 2 条 | 小号等宽，青蓝 |
| 左侧卡片 2 | `修复` + 2 条 | 同上 |
| 左侧卡片 3 | `已知问题` + 1 条（**笑点放这**） | 同上，第三行用灰色 |
| 右侧 | 大版本号 `[版本号]` | 超粗 |

**字幕文案（3 变体）**
1. `v4.5 更新日志：新增「速度提升」。修复「速度太慢」。已知问题：没有。`
2. `第 28 天：发布全新模型，命名 DeepSeek v4.5 天王星 Ultra fast。（来源：网友）`
3. `已知问题：重置按钮仍在寻找中。我们会在它回来时通知你。`

**避坑**
- 「已知问题」那一栏是全部笑点，**别写成真 bug 通告**（会被当官方公告转）；
- 版本号/命名如果是**网友玩梗**，必须标来源（如「来源：网友」），不能写成官方口径；
- UI 不能做得像某家真实产品的界面（不抄布局与配色），抽象成「通用启动器」。

---

## 4. 一页速查：模板 × 新闻类型 × 风险

| # | 模板 | 最佳新闻类型 | 图/视频 | 风险 | 上手难度 |
|---|---|---|---|---|---|
| 1 | 比分对决 | 降价、重置、吊打 | 图（+可选 6s） | L2 中 | ★ |
| 2 | 电影海报 | 封杀、许可证、大版本 | 图（+可选 10s） | 中高 | ★★ |
| 3 | 赛事解说/转会 | 发布、挖人、合作 | 图（+可选 8s） | L2 中 | ★★ |
| 4 | 荒诞骑乘 | 重置、发布、任何「在跑」的 | 图 + 视频（首选） | L1 低 | ★★ |
| 5 | 音乐卡点 | 一周综述、连环降价 | 图 + 3–4 镜 | 中（BGM） | ★★★ |
| 6 | 突发插播 | 宕机、事故、突然降价 | 图（+6s） | L2 中 | ★ |
| 7 | 审判/开庭 | 许可证、条款、纠纷 | 图（+5s） | L2 中 | ★★ |
| 8 | 招聘/裁员 | 裁员、Agent 上岗 | 图（+10s） | L1 低 | ★ |
| 9 | 价格战擂台 | 降价、按次计费 | 图（+6s） | L2 中 | ★★ |
| 10 | 倒计时/Day N | 权重日、预测窗口 | 图（+5s） | L1 低 | ★ |
| 11 | 期望 vs 现实 | 宣传 vs 实测 | 图（+4s） | L1 低 | ★ |
| 12 | 排行榜/奖杯 | 榜单、融资、年度 | 图（+6s） | L2 中 | ★ |
| 13 | 重置卡 | 额度、优惠、限量 | 图（+7s） | L2 中 | ★★ |
| 14 | 补丁说明 | 小版本、悄悄改条款 | 图（+5s） | L1 低 | ★ |

**今天就该做的三个**（2026-10-20）：
1. **模板 10 + 13 组合**：Tibo 重置窗口（10/20–10/21）+ 「小卡片」原话 → 一条图 + 一条「设计稿」→ 成本最低、时效最紧。
2. **模板 4**：鹈鹕骑车已经 benchmark 化，认知度最高，随便挑一条在跑的新闻都能骑上去。
3. **模板 14**：把「如果让 Tibo 来发布 DeepSeek 新模型」那条神评论做成补丁说明图 → 纯后期，0 生成风险。

---

## 5. 发之前最后 6 项自查

- [ ] 画面里**一个字都没有**（含数字、伪文字、招牌、UI 标签）
- [ ] 台账里每个数字/比分/日期都有出处；**预测已标「预测」**
- [ ] 没有真人脸、没有官方 logo、没有复刻官方字体/奖杯造型
- [ ] 涉及赛事：没伪造赛果、没冒充官方；涉及电影：只借结构不借素材
- [ ] AI 生成标识：左下角小字 + 发布页勾选（`07` §1）
- [ ] 一条里只有一个梗

---

*最后更新 2026-10-20 · 骨架基于 arcloop 真实模型能力（`arcloop-models.md` 同日核实）· 热点依据见 `research/trends-2026-10.md`（本次核实仅到标题级，正文待人工确认）*
