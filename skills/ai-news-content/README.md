# ai-news-content —— 一条 AI 新闻，五种成品

这是把三个社区 skill 合并重构后的自研 skill。给做 AI 资讯号（小红书/抖音）的人用。

---

## 1. 它解决什么问题

原来要装三个 skill、来回切换：

| 原来的 | 干什么 | 问题 |
|---|---|---|
| `cn-skills`（xiaohongshu-post + douyin-script） | 写小红书/抖音文案 | 只懂平台规则，不懂 AI 新闻；没有事实核验 |
| `shuorenhua` | 去 AI 味 | 面向「改稿」，不是「写稿」，完整版偏长 |
| `lanshu-video-kit` | 视频提示词 | 按即梦/可灵/Sora 的 API 写，而用户实际在 **arcloop.ai** 手动生成 |

合并后一个 skill 解决全链路：**输入归一 → 选题判断 → 事实分层 → 文案 → 生图/视频提示词 → 机器自检**。

---

## 2. 和原来比，改了什么

**吸收的**
- cn-skills 全部量化约束（标题 ≤20 字、正文 300–800 字、emoji ≤8、标签 5–8、语速 240–280 字/分、每句 ≤15 字）
- shuorenhua 「保住事实/数字/责任主体，只做减法」的编辑哲学，压成一页可执行清单
- lanshu 的「图生视频只描述运动」「每镜一运镜」「不写死秒数」「显式端点」

**修掉的**
| 原 skill 的问题 | 这个 skill 怎么处理 |
|---|---|
| 只能吃固定来源 | 输入层支持 AIHOT / 任意 URL / 本地文件 / stdin 四种 |
| 没有事实分层 | `facts[].tier` 四档：official / first-party / third-party / unverified |
| 没有合规环节 | 专章处理 AI 生成标识、站外导流、广告法 |
| 视频提示词按模型厂 API 写 | 全部按 arcloop 真实模型重写（无负面词字段 → 内联；3:4 不支持 → 裁切） |
| 没有自检 | `check_copy.py` 机器校验 + `prep_input.py --check` |

**新增的**
- `prep_input.py`：多源归一化，产出素材卡
- `check_copy.py`：发布前机器校验（标题/字数/emoji/标签/AI 腔/绝对化/导流/AI 标识/数字溯源）
- 预测型内容的纪律（全篇条件句 + 写清样本量 + 预设失败话术）
- 生图模式（只出图不发视频的场景，比如热点预测、快讯海报）

---

## 3. 怎么安装

**Claude Code / Codex / Gemini CLI / OpenCode 等支持 Agent Skills 的工具**：把整个目录放进 skills 目录

```bash
# 个人级（所有项目可用）
cp -R skills/ai-news-content ~/.claude/skills/
# 或项目级
mkdir -p .claude/skills && cp -R skills/ai-news-content .claude/skills/
```

装完新开一个会话，说「把今天 AIHOT 热点里最值得做的一条，做成小红书图文」验证。

**依赖**：Python 3.9+，只用标准库。脚本都在 `scripts/` 下。

---

## 4. 怎么用

### 最省事的一句话
> 把今天 AIHOT 热点第一名做成小红书图文 + 生图提示词

skill 会自动走：取素材 → 判断选题 → 写稿 → 出提示词 → 自检。

### 手动跑脚本

```bash
# 1. 归一化输入
python3 scripts/prep_input.py --aihot-story <publicId> --out material.json
python3 scripts/prep_input.py --url https://www.minimax.io/blog/minimax-m31f --out material.json
pbpaste | python3 scripts/prep_input.py --file - --out material.json

# 2. 写稿（交给模型，按 SKILL.md 的流程）

# 3. 自检
python3 scripts/check_copy.py 稿件.md --material material.json
```

---

## 5. 输出模式

| 模式 | 产出 | 什么时候用 |
|---|---|---|
| `meme` | 梗概念卡 + 1–3 张整活图 + 字幕文案 | **默认先考虑**：蹭电影/赛事/热歌/爆火梗 |
| `meme-video` | 梗概念卡 + 15–30 秒视频提示词 | 动作本身是梗（骑乘/对决/翻车） |
| `flash` | 1 张图 + 60–120 字 | 追速度，发群/微博/朋友圈 |
| `xhs` | 封面 + 3–4 内页 + 正文 + 标签 | 小红书，追收藏 |
| `douyin` | 口播稿 + 分镜 + 视觉提示词 | 抖音/视频号，追完播 |
| `image` | 生图提示词包 | 只出图（预测、快讯海报） |
| `video` | 视频提示词包（arcloop 模型） | 已有脚本只要画面 |
| `full` | 全套 | 大新闻做全平台 |

---

## 6. 文件结构

```
ai-news-content/
├── SKILL.md                      # 主入口：路由表 + 工作流 + 硬规则
├── README.md                     # 本文件
├── references/
│   ├── 00-sourcing-and-rights.md # 数据来源与使用权（事实 vs 表达）
│   ├── input-adapters.md         # 素材卡 schema + 非 AIHOT 新闻源
│   ├── 02-platform-xiaohongshu.md
│   ├── 03-platform-douyin.md
│   ├── 08-meme-engine.md         # 梗引擎：注意力公式 + 三种借势机制
│   ├── 09-meme-templates.md      # 14 个可复用梗模板
│   ├── 04-image-prompts.md       # 生图（arcloop 图片模型）
│   ├── 05-video-prompts.md       # 视频（arcloop 视频模型）
│   ├── 06-fact-check.md          # 事实核验流程
│   ├── 07-compliance.md          # 发布合规
│   └── arcloop-models.md         # arcloop 模型参数与选型
├── scripts/
│   ├── prep_input.py             # 多源归一化
│   └── check_copy.py             # 发布前机器校验
└── assets/
    ├── output-template.md        # 统一输出骨架
    └── card-layouts.md           # 卡片版式参考
```

---

## 7. 设计原则（如果你要改它）

0. **注意力优先**：先问「这能不能变成梗」，再问「信息全不全」。没人点开等于零
1. **事实入，表达出**：不搬运别人的叙述，只取事实自己写
2. **约束写死，能机器判的全机器判**：字数、emoji、标签、导流词交给脚本
3. **预测必须标注**：条件词、样本量、失败话术，三件套
4. **视觉先图后视频**：图能发就发，别一上来做视频
5. **平台适配跟着真实工具走**：arcloop 改了，就改 `references/arcloop-models.md`，别改 SKILL.md 的流程

---

## 8. 已知局限

- 事实核验是「提示 + 工具」，最终判断仍要人；脚本只能查数字有没有出处，查不出「这句话是不是推断」
- arcloop 站点迭代快，模型页可能变；`arcloop-models.md` 标了核实日期，用之前先扫一眼生成器下拉框
- cn-skills 原本只有 1 个 star，它的规则好用但没经过社区大规模验证；我们保留了规则、补了自检
- 不支持平台自动发布（发布仍要手动）
