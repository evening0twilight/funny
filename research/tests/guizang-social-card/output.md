# 实测记录：guizang-social-card（op7418/guizang-social-card-skill）

- 输入：`research/tests/input-news-01.md`（AIHOT 热点 No.01：MiniMax M3.1 Flash 发布）
- 任务：给这条 AI 新闻做小红书 3:4 卡片（封面 + 数据页 + 避坑页）
- 执行：严格按 `SKILL.md` 的 Workflow：Intake → Extract Story → Choose Style Mode → Plan Pages → **4.5 Copy The Seed Template** → 填 S01/S03/S05 recipe
- 选择：**Swiss International**（发布型内容 = release note 感，适合 Swiss 的「工程感/量化」立场）+ 默认 accent `ikb`（IKB Blue）
- 产出：`index.html`（3 张 1080×1440 poster，含 S01 封面 / 数据页 / 陷阱页）

## 执行轨迹（对应 SKILL.md 步骤）

| Step | 动作 | 结果 |
|---|---|---|
| 1 Intake | 读取源文，判断内容类别 | 不在它列的 11 个小红书常见类别内（旅行/职场/游戏/影视/美食/彩妆/穿搭/家居/健身/情感/推荐），按「AI 工具发布」自行判断在能力圈内（文案+结构+系统图，不涉及真实摄影） |
| 1 Intake | SKILL 要求「News/Tutorial/Data/Review 内容主动索要截图作为证据层」 | 本环境无截图 → 记下这是本次成品的**最大缺陷**：没有真实 UI/榜单截图，卡片会偏"海报" |
| 2 Extract | 页面计划 | 3 页：cover / data / trap（SKILL 建议 5-9 页，本次只做验证用的 3 页） |
| 3 Style | 选模式与主题 | Swiss + IKB；deck 内只用 1 个 accent |
| 4.5 Seed | **不手写 HTML，复制 `assets/template-swiss-card.html`** | ✅ 已按规则复制，只替换 `<!-- POSTERS_HERE -->` |
| 4.5 | 只用 template 已定义的 class | ✅ 脚本校验：使用 25 个 class，全部在模板 CSS 中存在（`xhs` 是 poster 尺寸修饰符） |

## 硬规则合规检查（SKILL 明文要求）

- [x] deck 内只有一个 `--accent`（`data-accent="ikb"`）
- [x] 无 border-radius / box-shadow / gradient（沿用模板，未加）
- [x] card-ink / card-accent / card-fill / card-outlined 未在同一节点混用（本次未用 card 系列）
- [x] 「the larger, the lighter」：大字号用模板的 weight 200，未覆盖字重
- [x] 中文标题 ≤28 字（封面标题 12 字）
- [x] 不写「3s / Live Photo / information budget」这类内部术语到可见文案（首屏文案全为读者视角）

## 产出片段（index.html 节选）

```html
<section class="poster xhs" id="xhs-01">
  <div class="content stack gap-9">
    <div class="chrome-min"><span>AIHOT No.01 · Swiss</span><span>2026.10.20</span></div>
    <div class="stack gap-7">
      <p class="t-cat">封面 · Cover</p>
      <h1 class="h-statement">成本<br>砍到 1/3</h1>
    </div>
    <div class="grow"></div>
    <hr class="hr-accent">
    <p class="lead">MiniMax M3.1 Flash 发布：速度 3 倍、200+ TPS，模型权重 10 月 23 日开放。</p>
    ...
```

## 环境限制（必须诚实说明）

- 本沙箱**无法运行浏览器**：Chrome headless 被系统拦截（`Trace/BPT trap`），QuickLook（`qlmanage`）也报 `sandbox initialization failed`。因此**无法把 HTML 截成最终 PNG**。
- 也就是说：我验证了它能产出**结构正确、class 合法、规则合规的卡片 HTML**，但没能验证「肉眼看到的效果」。这对 guizang 这种纯视觉 skill 是重大缺口——它的价值恰恰在视觉。

## 评分

| 维度 | 分 | 说明 |
|---|---|---|
| 指令可执行度 | 5 | 336 行 SKILL.md + 16 篇 references + seed 模板，规则可逐条勾选；「不许手写 HTML，复制 seed」这条极大降低跑偏概率 |
| 产出可用度 | 3 | HTML 结构合法，但① 需要自己截图才能发；② 无真实截图证据层 → 偏「海报」；③ 未验证视觉效果 |
| 中文适配 | 5 | 中文字号最小值、中文标题字数区间、宋体/思源字号体系都是为中文设计的，比英文搬运的设计规范强 |
| 无需返工 | 3 | 依赖生图/截图素材与浏览器渲染；纯文本场景只能产出「可发布但不出彩」的设计稿 |

## 结论（给报告的判断）

- **它不是文案 skill**，是「把已经写好的文案变成能发的卡片」的视觉层。用户的 A 需求（扩写）它一点不碰。
- 作为**配图层**，它是我见过最专业的（能力圈诚实、规则硬、有 seed 模板 + 校验脚本）。但 AGPL-3.0 + 需要真实截图 + 需要本地浏览器，三个门槛都必须提前告诉用户。
- 若用户只用纯文本产出，推荐顺序应是「文案 skill 主做 + guizang 只在需要卡片时启用」。
