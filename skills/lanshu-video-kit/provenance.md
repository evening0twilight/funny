# provenance — lanshu-video-kit

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/cclank/lanshu-awesome-ai-video-kit |
| 子路径 | `skills/`（7 个 SKILL.md）+ `methodology/`（21 篇 SOP） |
| Star | 424（GitHub API 查证于 2026-10-20 11:35 +08:00） |
| License | MIT |
| Commit | `f4c1bbd09800a0002a169465d14060e3b6a88f1e`（2026-10-07T11:31:16+08:00） |
| Last push | 2026-10-07T03:31:17Z |
| Open issues | 4 |
| 安装方式 | `git clone --depth 1`，只拷 `skills/` + `methodology/` + LICENSE（`prompts/` 1MB 的 594 条提示词库未装，按需再取） |

## 它是「Skill」还是「资料库」？

**两者都是，但 skill 部分是真的**。7 个 SKILL.md 各自有明确职责与「何时不用此 skill」路由：

- `model-selector`（选模型）、`seedance-prompter`（8 要素公式）、`seedance-storyboard`（剧情→3-5 镜头分镜）、`happyhorse-prompter`（30-55 词紧凑 + 原生音频）、`kling-prompter`、`seedance-debugger`（出问题怎么修）、`prompt-translator`（跨模型转换，基于 110 条对照基准 `prompts/data/cross-model-matrix.json`，查表式而非凭感觉重写）。

每个 skill 都有 Step 流程、模板骨架、检查清单、以及指向 `methodology/` 的深读入口；`methodology/` 是 21 篇中文 SOP（基础公式 / 进阶公式 / 约束词清单 / 运镜词典 / 情绪外化表 / 六大模型公式速查 / Veo 公式 / Sora 公式 / Kling 公式 / 避坑 12 问 …），是这批 skill 的知识底座。

## 为什么选它

1. **中文原生**，直接面向即梦/可灵/Seedance/HappyHorse 这些国内用户真在用的模型，不需要先翻译英文方法论。
2. **有工程约束**：字数上限、运镜单一化、主体稳定标签、多主体指代规则、`@图片N` 素材角色分配、负面词/约束词清单。
3. **有 CI 与工具**：GitHub Action 每周监控 24/32 个模型官方端点版本变化（`model-version-monitor.yml`），说明作者在维护而不是一次性 dump。
4. **社区认可度**：424 star + 被 awesome.re 收录 badge（需自行核实）+ 有 CONTRIBUTING / CHANGELOG。

## 已知局限

- 偏商业广告 / 通用剧情口播，缺乏「新闻解说」这类题材模板。
- 部分 skill（model-selector）依赖模型清单时效，模型迭代快时会滞后。
