# provenance — xhs-image-text-generator

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/sanqi-cd/Sanqi-Skills |
| 子路径 | `xhs-image-text-generator/` |
| Star | 28（GitHub API 查证于 2026-10-20 11:35 +08:00，Asia/Singapore） |
| License | MIT（仓库根 LICENSE；SKILL.md frontmatter 也标 `license: MIT`） |
| Commit | `faa1a75e3b9a726f6a925b70401e3afd35ba50d1`（浅克隆 HEAD，2026-10-01 提交） |
| Last push | 2026-10-01T19:07:34Z |
| Open issues | 1 |
| 安装方式 | `git clone --depth 1` 后把 `xhs-image-text-generator/` 整目录拷入（不走任何写 `$HOME` 的安装器） |

## 为什么选它（star 少，但门槛达标的地方）

star 只有 28，远低于「>=500 star」的优先线，这是它最大的硬伤，必须在报告里点名。选它做实测的理由是**可验证的工程质量**，不是热度：

1. **真有工作流**：203 行 SKILL.md，5 个 Step（素材归一 → 补齐上下文 → 发布方案 → 生成图片页 → 整理交付包），每一步都有可执行动作或产物定义。
2. **有可跑脚本，不是纯提示词**：`scripts/normalize_input.py`（URL/HTML/MD 抽正文）、`render_carousel_html.py`（carousel.json → 排版 HTML，锁定文字与页数）、`init_delivery_package.py`、`validate_delivery.py`（交付包校验，不合格不许算完成）。
3. **有约束**：高风险主题开工门槛；「只有提示词或空占位目录不算完成」；6 维质量评分，低于 4 分必须给修改建议。
4. **有 evals**：`evals/evals.json` + `evals/trigger-evals.json`，同仓库另有 `docs/evaluations.md`。
5. **交付物定义到文件级**：`manifest.md` / `caption.txt` / `hashtags.txt` / `comments.txt` / `image-prompts.md` / `carousel.json` / `quality-check.md`，这正是内容生产者要的东西。

## 已知局限

- 它要「生图」，而实测环境没有图片生成模型；SKILL.md 明确允许用 `render_carousel_html.py` 的 HTML 作为中文文字的排版基准（`--allow-html`），本次实测即走这条路径 + Chrome headless 截图。
- 社区认可度弱：单一作者、star 少、无被 awesome 清单收录的证据。
