# 每日 SOP

> 目标：每天 30–60 分钟出一条能发的内容（图或视频），且不出事实错误。
> 所有路径都带日期。**日期以 `new_day.py` 打印的为准，不要靠脑子记。**

---

## 0. 开工（1 分钟）

```bash
python3 tools/new_day.py
```

会建好 `data/raw/<今天>/` 和 `out/<今天>/`，并把选题模板生成好。

**如果它说目录已存在**：说明今天已经开工过了，直接继续。

---

## 1. 更新「今天什么在火」（5 分钟）

编辑 `data/hot-trends.md`：

```markdown
## 赛事
- ✅ LoL 瑞士轮 10/23 开打，首场 10/24 01:00（官方赛程）
## 影视
- ✅ 《复联5》内地 12/16（预热期，适合海报 parody）
## 音乐
- 🟡 某首热歌（发布前在曲库确认）
## AI 整活梗
- ✅ 鹈鹕骑车
## 今日禁用
- ❌ VCT 比分（两源冲突）
```

标记：✅ 已核实 / 🟡 待复核 / ❌ 禁用。规则见 `skills/ai-news-content/references/10-trend-injection.md`。

---

## 2. 取数 + 选题（5 分钟）

```bash
python3 tools/aihot_fetch.py hot --save data/raw/<今天>/hot-topics.json
python3 tools/topic_score.py --profile news     # 资讯号
python3 tools/topic_score.py --profile tool     # 工具号
```

挑 **1–2 条**写进 `out/<今天>/00-当日选题.md`，每条填：
- 新闻是什么
- **梗方向**（置换 / 对决 / 预告）
- 输出模式（`meme` / `meme-video` / `flash` / `xhs` / `douyin`）
- 借的什么热点
- 风险

**判断标准**：这条能不能让你 3 秒内想笑/好奇？不能就换。

---

## 3. 归一素材（2 分钟）

```bash
python3 skills/ai-news-content/scripts/prep_input.py \
  --aihot-story <publicId> --out data/raw/<今天>/<slug>/material.json
```

也可以 `--url` 抓官方博客，或 `pbpaste | --file -` 吃一段粘贴的文字。

---

## 4. 出内容（20–40 分钟）

加载 `skills/ai-news-content/SKILL.md`，按它里面的流程走：

```
梗引擎（选机制）→ 模板（套骨架）→ 文案 → 视觉提示词（arcloop）
```

产物落到 `out/<今天>/<slug>/`：

```
00-梗卡.md          # 梗 / 为什么好笑 / 借什么热点 / 画面 / 风险
01-<平台>文案.md     # 小红书正文 或 抖音口播 或 字幕文案
02-视觉提示词.md     # arcloop 模型 + 参数 + 提示词（画面零文字）
自检.md             # check_copy 输出 + 人工核事实记录
```

---

## 5. 自检（5 分钟，不能省）

```bash
python3 skills/ai-news-content/scripts/check_copy.py \
  out/<今天>/<slug>/01-<平台>文案.md \
  --material data/raw/<今天>/<slug>/material.json
```

必须全绿（FAIL 一条都不能留）。然后人工过一遍：

- [ ] 热点事实（比分/档期/场馆）是真的吗
- [ ] 「未公布」有没有带日期锚点
- [ ] 有没有把第三方转述写成官方
- [ ] AI 生成声明 + 角标
- [ ] 有没有编造体验

---

## 6. 出片（arcloop）

| 步骤 | 用什么 |
|---|---|
| 出首帧图 | Seedream 5 Pro（材质）/ GPT Image 2.5 Sunburst（排版） |
| 图生视频 | Vidu Q4（单张首帧）/ Kling（多镜头+中文台词，**audio 默认 off**）/ Seedance 2.5（30s 一镜） |
| 口播配音 | Seed Audio 1.0（≤2 分钟，中文） |
| 拼接/加字幕 | Canvas + 剪映 |

**画面零文字**：所有中文、数字、logo 后期贴。提示词里记得内联负面约束（arcloop 没有负面词框）。

---

## 7. 收工（2 分钟）

```bash
python3 tools/doctor.py
git add -A && git commit -m "data: <今天> <一句话>" && git push
```

`doctor.py` 不通过先修。它能抓：结构不对、跨日引用、skill 引用缺失、脚本编译失败、临时文件残留。

---

## 时间不够时的最简路径

只做这三步也能出一条：**热点更新 → 选题 1 条 → meme 图 + 字幕 → 自检**。
视频可以不做——平台看的是完成度和互动，不是形式。
