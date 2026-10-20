# provenance — shortfilm-prompt

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/jnMetaCode/ai-shortfilm-prompts |
| 子路径 | `skills/shortfilm-prompt/` |
| Star | 476（GitHub API 查证于 2026-10-20 11:35 +08:00） |
| License | MIT（方法论 / templates / Skill 为 MIT；`prompts/` 里 Mx-Shell 原始材料 © Mx-Shell 保留权利，见仓库 NOTICE，本次安装不含该目录） |
| Commit | `5ec3204daecabb0604f171c39597961fb77cfcfc`（2026-10-19T05:57:05Z） |
| Last push | 2026-10-19T05:57:05Z（**今天仍在维护**） |
| Open issues | 0 |
| 安装方式 | `git clone --depth 1` 后拷 `skills/shortfilm-prompt/` |

## 为什么选它

1. **SKILL.md 411 行，是真工作流**：5 个 Stage（核心主题 / 角色场景 / 氛围画质 / 运镜规则 / 分镜），每段有可执行的写法与禁止项。
2. **有硬约束，能自检**：7 条 hard rules（禁空泛形容词、必须写相机+镜头型号、必须写 breathing 句、必须写 sound 行、≥2 个瑕疵描述、结尾不许堆特效、禁 IP 名 + 每模型建议）+ 交稿前 30 秒 checklist，**不通过不交**。
3. **按模型路由**：Seedance / 可灵 / Veo / 海螺 / Wan / Runway / Pika / Sora 各自的分辨率、时长、负面词字段差异都写了（这条最值钱，社区大多数「提示词合集」没有）。
4. **22 个模板 + 6 个 worked examples（`examples/` 里是完整成品提示词）**，不是空骨架。
5. **有 evals 与 CI**：`evals/` + `.github/workflows/evals.yml`（LLM judge）与 dead-link 扫描；bilingual（`SKILL.zh.md`），中英同步维护。
6. 有 release/版本号与 CHANGELOG（v0.5.0）。

## 已知局限

- 英文是 canonical（SKILL.md 为英文，中文是译本），我用中文任务跑过，可执行但输出风格偏「Mx-Shell 丧尸清道夫」那套电影感，非电影题材需要改写模板。
- 偏「单镜头电影感」，对新闻口播类视频需要自己补讲解层。
