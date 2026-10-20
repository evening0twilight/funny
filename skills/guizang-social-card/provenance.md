# provenance — guizang-social-card

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/op7418/guizang-social-card-skill |
| Star | 7596（GitHub API 查证于 2026-10-20 11:35 +08:00）**全表最高** |
| License | **AGPL-3.0**（商用需评估；仓库另有 `COMMERCIAL_LICENSING.md`） |
| Commit | `cf4b810fac1c73fb65a2bb31d8c9278d82cbc4c5`（2026-07-02T00:38:49+08:00） |
| Last push | 2026-07-01T16:39:11Z |
| Open issues | 13 |
| 安装方式 | `git clone --depth 1`，拷 `SKILL.md` + `references/` + `scripts/` + LICENSE（`assets/` 演示图未装） |

## 为什么选它

1. **中文内容社区里 star 最高的「小红书图文」skill**（7.5k），且是设计系统级产出：336 行 SKILL.md + **16 篇 references**（layout-recipes / components / style-system / theme-presets / portrait-fill / content-planning / qa-checklist …）+ 校验脚本 `validate-social-deck.mjs`。
2. **约束细到可执行**：3:4 比例、中文字号最小可读值、中文标题字数区间、Swiss 卡片留白互斥规则、图片容器比例类、Lucide 图标规则、真人脸/主体避让、截图 `.frame-shot` vs `.frame-img` 取舍。
3. **诚实的能力边界**：SKILL.md 直接写「美食大片摆盘 / 日常 OOTD 全身 / 梦核风 / Y2K / 纯摄影showcase 不在能力圈，要当场拒绝而不是硬凑」，这在同类里极少见。
4. 有 `validate-social-deck.mjs` 自校验 + `check-skill-docs.mjs`，说明作者把它当工程维护。

## 已知局限

- **AGPL-3.0**：个人发笔记没问题，但若用户把生成的模板做成对外产品/服务，需看 `COMMERCIAL_LICENSING.md`。
- 它是**配图/排版层**，不做文案扩写；本次实测定位为「A 的视觉搭档」，不是文案主力。
- 距上次更新已 3 个多月（last push 2026-07-01），维护节奏慢于视频类 skill。
