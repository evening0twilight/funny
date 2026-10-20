# 交接说明（HANDOFF）

> 这份文档回答一个问题：**如果换一个人接手，他需要知道什么才能不踩坑。**
> 最后更新：2026-10-20

---

## 1. 这个项目是干什么的

把 AI 新闻（主要来自 aihot.news）变成能吸引目光的内容：**梗图 / 短视频 / 小红书图文**，面向小红书、抖音、微博等平台。

**定位是「整活号」，不是「资讯号」**——先让人停下来，再谈信息。这条排序写在 `skills/ai-news-content/SKILL.md` 第一行。

---

## 2. 现在有什么（截至 2026-10-20）

| 模块 | 状态 | 位置 |
|---|---|---|
| 数据采集 | ✅ 可用 | `tools/aihot_fetch.py`（6 个命令，带缓存/限流/ETag） |
| 选题打分 | ✅ 可用 | `tools/topic_score.py`（三种号型 profile） |
| 主 skill | ✅ 可用，两轮对抗审校 | `skills/ai-news-content/`（SKILL.md + 11 份参考 + 2 脚本） |
| 梗引擎 | ✅ 新增 | `references/08-meme-engine.md` |
| 梗模板库 | ✅ 14 个模板 | `references/09-meme-templates.md` |
| 热点注入 | ✅ 机制 + 当日快照 | `data/hot-trends.md` + `references/10-trend-injection.md` |
| arcloop 规格 | ✅ 含 Kling / Canvas | `references/arcloop-models.md`（604 行，34 个来源） |
| 自检 | ✅ 脚本 | `scripts/check_copy.py` |
| 项目体检 | ✅ 脚本 | `tools/doctor.py` |
| 每日工作区 | ✅ 脚本 | `tools/new_day.py` |
| 当日成品 | 4 组 | `out/2026-10-20/` |

**成品索引**（`out/2026-10-20/`）：
- `minimax-m31f/` — 资讯型全套（v2 已过审校，含 8 条 P0 修复记录）
- `codex-reset-predict/` — 预测型（Tibo 重置窗口）
- `memes/` — 三条整活（13:0 比分牌 / 骑鹈鹕 17 秒视频 / 电影海报）
- `skill-tests/` — 新 skill 的三篇实测

---

## 3. 关键决策（和理由）

| 决策 | 理由 |
|---|---|
| 自研 `ai-news-content` 而不是继续用三个社区 skill | 三家各缺一块：cn-skills 不懂新闻、shuorenhua 只能改稿、lanshu 按模型厂 API 写；合并后统一入口 |
| 视频提示词按 **arcloop.ai** 写，不按模型厂 API | 用户是 arcloop 会员，手动生成，没有各厂 key |
| 画面**零文字** | 视频模型画中文必糊，文字全部后期贴 |
| 负面约束**内联** | arcloop 没有独立负面词输入框 |
| 事实分四档 tier | 最容易翻车的是「把转述当官方」 |
| 先判梗再判信息 | 用户明确：吸引目光 > 信息完整 |
| 一天一个内容文件夹 | 防止上下文串日（见 CONVENTIONS §5） |

---

## 4. 已知问题 / 待办

| 优先级 | 问题 | 建议 |
|---|---|---|
| P1 | 热点雷达里影视/赛事/热歌有部分是「标题级」核实 | 每条发布前人工点开原文；`research/trends-2026-10.md` 附了待核实清单 |
| P1 | `check_copy.py` 查不出「单位/语境错位」（如素材卡有「100 万 token」写成「100 元」） | 必须人核，`references/06-fact-check.md` §6 有说明 |
| P2 | VCT 比分两源冲突（3-0 / 3-1） | 未写死；有准信再更新 `data/hot-trends.md` |
| P2 | `research/_scratch/` 曾克隆大量仓库 | 已清理，`.gitignore` 有忽略规则 |
| P2 | 热歌榜是二手来源 | 用 BGM 前在曲库确认 |
| P3 | 没有自动发布 | 发布仍手动（平台风控，不建议自动化） |
| P3 | `skills/` 下的社区原版是**部分拷贝**，内部可能有过期链接（如 shortfilm 的 `../prompts` 没拷） | 只作对照与备选，日常用 `skills/ai-news-content/`；不要照着它们的目录结构找文件 |

---

## 5. 接手后怎么继续（三步）

1. 读 `CONVENTIONS.md`（规则）→ `docs/daily-sop.md`（每天干什么）
2. 跑 `python3 tools/doctor.py`，确认项目是健康的
3. 跑 `python3 tools/new_day.py`，开始今天的活

---

## 6. 角色分工（如果多人协作）

| 角色 | 负责 | 只读/可写 |
|---|---|---|
| 内容生产 | 选题、梗、文案、视觉提示词 | 可写 `out/<日期>/<slug>/` |
| 审校 | 事实核验、合规、出片风险 | 只读产出，写 `自检.md` 与审校报告 |
| 数据 | 取数、热点雷达、arcloop 规格维护 | 可写 `data/` `research/` |
| 负责人 | SKILL.md、README、CONVENTIONS | 规则类文件只有负责人改 |

**冲突原则**：同一文件同一时间只有一个人写；改完在 `docs/handoff.md` 追加一行。

---

## 7. 三条最容易踩的坑

1. **跨日**：今天的稿子引用了昨天的 material。`doctor.py` 会报，别绕过。
2. **伪造事实**：真实队名 + 编的比分 = 造谣。可以编剧本（虚构队名），不能编事实。
3. **忘了 AI 标识**：AI 生成画面必须勾平台声明 + 加角标（《AI 生成合成内容标识办法》2025-09-01 施行）。

---

## 8. 改动记录

| 日期 | 内容 | 谁 |
|---|---|---|
| 2026-10-20 | 项目初始化；自研 skill；梗引擎；arcloop 规格；一日一文件夹规范 | Lead |
