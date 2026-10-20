# 实测记录（反面样本）：vivy-yi/xiaohongshu-skills

- 仓库：https://github.com/vivy-yi/xiaohongshu-skills（493 star，no license，last push 2026-01-23，139 个 SKILL.md）
- 输入：同一条新闻 `research/tests/input-news-01.md`
- 执行：按 `skills/01-内容创作/copywriting-skills/SKILL.md` + `title-writing/SKILL.md` 的步骤写一条小红书笔记

## 它到底写了什么（原文摘录，全部来自 SKILL.md）

`copywriting-skills/SKILL.md` 第 3 步「Implementation」的全部可执行内容：

> **Step 1: Write Compelling Opening Hook**
> - **Question**: "你还在...吗?"
> - **Surprising**: "没想到..."
> - **Relatable**: "姐妹们,我也是..."
> - **Promise**: "让我告诉你..."
>
> **Step 2: Use Conversational Tone**
> - Use "姐妹们", "大家", "宝宝们" (inclusive terms)
> - Add emoji: 💖, ✨, 🔥, 😭 (emotionally)
> - Be enthusiastic: "OMG", "绝绝子", "真香"
>
> **Step 5: Create Emotional Connection**
> - "真的感动哭了" / "后悔没早点发现" / "无限回购" / "相见恨晚"

## 按它执行后的产出（如实写，不做人工美化）

> OMG姐妹们！没想到 MiniMax 这次直接放大招了🔥
>
> 姐妹们，我最近用了 M3.1 Flash，真的绝绝子！成本只要三分之一，速度快 3 倍，简直相见恨晚😭
>
> 说实话，我之前用别的模型真的花了不少冤枉钱，这次终于找到本命了✨
>
> 💡 我的使用感受：
> 1. 成本真的低，学生党也能冲
> 2. 速度真的快，不卡顿
> 3. 还限时免费 3 天，真的别错过
>
> 真的感动哭了，后悔没早点发现😭
>
> 关注我，不迷路～评论区告诉我你的看法！

## 为什么这个产出不能用（逐条对比）

| 问题 | 具体证据 |
|---|---|
| 无事实约束 | 产出里「我最近用了」「花了冤枉钱」是编的；SKILL 没有任何「不得编造体验/数据」的约束 |
| 无平台格式规范 | 不知道小红书不渲染 Markdown、标题 ≤20 字、正文 300-800 字、标签 5-8 个大垂搭配；`title-writing` 也只有「Question/Surprising/Relatable/Promise」四类，无字数与平台规则 |
| 无交付物定义 | 不规定输出结构（标题备选 3 个 / 封面文案 / 正文 / 标签），每次产出形状都不同 |
| 语气与赛道的错配 | 「绝绝子/本命/感动哭了」是美妆个护语气；对 AI 工具号是灾难 |
| 「Before/After」是自我描述不是方法 | 全文「Before」是坏文案示例、「After」是「OMG姐妹们」示例，属于**用文案解释文案**，不是可执行流程 |
| 约束形同虚设 | 文末写「Related Skills: **REQUIRED**: content-planning / persona-building」，但没有任何机制或检查去保证先跑它们 |
| 规模换质量 | 139 个 SKILL.md、目录分类华丽（9 大类），但每个都是「Overview / When to Use / Before-After / Implementation 泛论」的 SEO 长文模板；`content-layout` 623 行里大半是「❌ 文字太小看不清 / ✅ 清晰层级」这类常识 |
| License 缺失 | 仓库无 LICENSE 文件，**法律上不可复用**，这点比质量更致命 |

## 评分

| 维度 | 分 | 说明 |
|---|---|---|
| 指令可执行度 | 1 | 只有方向性形容词（be enthusiastic），没有输出契约 |
| 产出可用度 | 1 | 产出是编造体验 + 错语气，0 处可直接发 |
| 中文适配 | 3 | 中文句子通顺，但语气是「美妆号」而不是中文内容生产的通用语气 |
| 无需返工 | 1 | 全部重写 |

**结论：典型「star 数高、SKILL.md 数量多、实际是提示词散文集」的仓库，不建议用。**
