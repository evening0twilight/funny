# provenance — cn-skills（xiaohongshu-post + douyin-script）

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/LLL-178/cn-skills |
| Star | 1（GitHub API 查证于 2026-10-20 11:35 +08:00） |
| License | MIT |
| Commit | `51f21a0a9c1a430b1506c5495259623b7c9e2633`（2026-09-06T17:43:46+08:00） |
| Last push | 2026-09-06T12:22:30Z |
| 安装方式 | `git clone --depth 1`，只拷 `skills/xiaohongshu-post/` 与 `skills/douyin-script/`（另附 `scripts/` 与 LICENSE） |

## 为什么还留着它

star 只有 1，是全表最低的一档，**不能作为「社区认可」的证据**。放进候选并实测的原因是：它是少见的同时把「小红书笔记」和「抖音口播脚本」写成有量化约束的 SKILL.md 的包，而且约束写得像行业 SOP 而不是「你是一个资深文案」：

- 小红书：标题 ≤20 字且给 5 类公式、正文 300–800 字（>800 完读率断崖）、开头三行定生死、emoji 每段最多 1 个整篇 ≤8 个、**禁止输出 Markdown 加粗**（小红书不渲染）、标签 5–8 个大/垂/自定义搭配、自检清单。
- 抖音：前 3 秒钩子 5 类、语速 240–280 字/分钟折算时长、每句 ≤15 字、每 5–10 秒埋刺激、输出分镜表（画面/口播/字幕/时长）。

## 已知局限

- 无 benchmark、无 evals、无脚本、单作者、star≈0，社区验证为零。
- 内容偏「通用爆款公式」，对 AI/科技类新闻的转化需要额外喂素材。
