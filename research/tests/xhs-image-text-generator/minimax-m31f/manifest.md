# 小红书图文交付清单

- 主题：MiniMax M3.1 Flash 发布（AIHOT 2026-10-20 热点 No.01）
- 页面数：8（3:4 / 1080×1350，HTML 排版基准）
- 状态：文案与分页完成；图片页因环境限制交付 HTML（沙箱内无生图模型，Chrome headless 被拦截）
- 默认发布账号：AI 工具情报号

## 页面列表（角色 / 标题）

1. cover — 成本砍到 1/3
2. pain — 跑一次 agent，账单先到
3. overview — 三个数字看懂这次发布
4. step — 匿名榜一大哥，就是它
5. step — 分数不算顶，但够用
6. case — 和 DeepSeek V4.1 比怎么选
7. pitfall — 三个坑，先别急着换
8. cta — 先白嫖，再决定

## 发布说明

- 首图用 page-01，正文复制 `caption.txt`，标签复制 `hashtags.txt`
- 评论区先发置顶评论（`comments.txt`）
- 图片：浏览器打开 `cards.html` 逐页截图，或用 `image-prompts.md` 走生图模型（文字必须与 `carousel.json` 一致）

## 事实边界

- 所有数字来自 AIHOT 事件页与其中引用的官方/第三方发布
- 许可证未公布、1M 上下文为第三方转述，已在 page-07 明示
