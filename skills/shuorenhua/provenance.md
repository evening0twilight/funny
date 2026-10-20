# provenance — shuorenhua（说人话）

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/MrGeDiao/shuorenhua |
| Star | 2184（GitHub API 查证于 2026-10-20 11:35 +08:00） |
| License | MIT |
| Commit | `6c4b9353b87185c26e684c4525be1af47f82fee9`（2026-10-16T14:32:59+08:00） |
| Last push | 2026-10-19T06:48:46Z |
| Open issues | 2 |
| 安装方式 | `git clone --depth 1`，拷 `SKILL.md` + `references/` + LICENSE |

## 为什么选它

它不是「写文案」skill，而是**投稿前的最后一道工序**：把 AI 初稿里的套话、翻译腔、重复铺垫清掉，同时保住事实、数字、责任主体和作者口气。对「AI 新闻 → 小红书文案」这条链路，AI 味是最大杀手，所以它是 A 类技能的补位件。

1. **有真实评测**：仓库带 `evals/`（benchmark 123 cases + 20 个场景样本 + 多版本 results-v*.md + 盲测 benchmark-blind.md），v2.6.0 有独立评测记录。这是本次调研里**唯一有公开 benchmark 数字的中文写作 skill**。
2. **约束非常硬**：明确「删除必须不丢命题、不丢否定/情态/完成状态/比较关系」；只允许删空招呼、重复、无源身份认证等；「去 AI 味」不等于「写平实」，`写平实` 需要用户显式授权才允许降夸饰；范围参数 `structural / bounded / in-place`、`audit-only` 等模式明确。
3. **不吹**：README 明说「不判断文章是不是 AI 写的，不提供 AI 含量或规避检测的保证」，反「AI 检测绕过」套路，态度可信。
4. 有 CHANGELOG、版本号、CONTRIBUTING、runtime-files.json，维护正常。

## 已知局限

- 它**只做减法**，不负责选题、扩写、起标题、配分镜。单独用不足以完成 A，必须和 A 类主 skill 串联。
- 4.2MB 仓库里大量 assets/dist 未安装，只需根 SKILL.md + references。
