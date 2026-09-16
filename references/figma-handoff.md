# 推到 Figma 精修

交付后固定提一句「要精修可以推到 Figma，我带你配置」。用户点头才读这份并往下走；
用户没回应或说不用，就到此为止，不追问。默认路径仍是本地改 HTML 再重建。

这里讲的是：把 deck 的页推进 Figma，变成原生可编辑图层（Frame + Text，不用 AutoLayout），
用户在 Figma 里精修、**自己导出，流程就结束**。

## 什么时候用哪条

| | 本地改 HTML（默认） | 推到 Figma |
|---|---|---|
| 能改什么 | 改字、换配方、换色对、重建 | 图层级别全都能改：挪 2px、调间距、加图形、抽组件、进设计库 |
| 速度 | 秒开 | 推送一页一次调用，3 页约 40 个图层，几十秒 |
| 门槛 | 无 | Figma 付费席位 + 装好 figma 插件 |
| 出图 | 浏览器直接放 | **用户在 Figma 自己导**，门禁止步于推送那一刻 |
| 适合 | 内容修正、换风格 | 版面要做设计级调整，或页要进设计系统继续用 |

## 硬前提

1. **Figma 付费席位**：Professional / Education / Organization / Enterprise。
   免费 Starter 用不了写入，推送会失败。
2. **装了 figma 插件**（官方 marketplace 的 `figma`，自带 MCP 连接和一组 figma-* skill）。
3. 用户手里有一个能写的 Figma 文件，或者让我新建一个。

## 首次配置引导（用户没配过时，一步一步来，别一次抛完）

**第 1 步 · 确认席位。** 让用户打开 Figma → 左上角头像 → Settings → 看 Plan。
写 Starter 就到此为止，告诉用户这条路走不通，回本地改 HTML。

**第 2 步 · 装插件。** 在 Claude Code 里：

```bash
claude plugin install figma@claude-plugins-official
```

装完要重开一次会话，插件的 MCP 才会挂上。

**第 3 步 · 授权。** 重开会话后跑 `/mcp`，找到 `figma` 那一条，选它走 OAuth，
浏览器会跳到 Figma 让用户点同意。回到终端显示 connected 就成了。
这一步必须用户自己在交互式终端里做，我代不了，也不要向用户要授权码或回调地址。

**第 4 步 · 验证。** 我调一次 `whoami`，能返回用户身份就通了。

**第 5 步 · 要目标位置。** 问用户：推到现有文件的某个位置，还是新建一个文件？
要现有文件就让他发**带 node-id 的链接**（在 Figma 里选中那个 Section 或 Frame，
右键 Copy link to selection）。同时问推哪几页（默认前 3 页，让用户先看效果再决定全推）。

已经配过的用户直接从第 5 步开始。

## 推送前必须先过门禁

**先验后推。** 推过去之后 HTML 就不再是最终版了，门禁再也管不到，所以推的必须是
已经过门的干净基线：

```
build_deck.py 生成 → check_contrast.py 全绿 → SKILL.md 工作流第 5 条自检全过 → 才推
```

用户在 Figma 里只做精修，不做补救。没过门就推，等于把没验过的东西交出去。

## 推送步骤（零依赖，不装 puppeteer）

### 1. 在浏览器里量几何

用内置浏览器打开 `<dest>/index.html`，`resize_window` 到 1920×1080，
然后把 `scripts/figma_extract.js` 整个文件内容贴进 `javascript_tool` 执行。
要改页范围就改文件开头的 `SLIDE_RANGE`。

它做三件事：先把 `[data-anim]` 钉到入场终态并清掉 GSAP timeline（否则量到的是动画中间态），
再按 `getBoundingClientRect` 逐元素读几何和样式，最后返回 JSON：
`{ viewport, fonts, unresolved, pages: [{ index, w, h, nodes }] }`。

**先看 `unresolved`。** chassis 目前只用实色 + 发丝线，正常为空。有东西就是这页写了
背景图 / 阴影 / 伪元素 / transform，推完要手工补，先跟用户说清楚。

**注意** `viewport` 必须是 1920×1080，不是就重新 resize 再量。file:// 下字体可能加载失败，
不影响位置（vw/vh 定的），只影响单行标签的测宽，建图模板已兜底。

### 2. 查字体

Figma 里 `listAvailableFontsAsync()` 查 `fonts` 列出的 family 在不在。当前底盘的映射：

| HTML | Figma | 备注 |
|---|---|---|
| Newsreader | Newsreader | 拉丁字体，中文靠 Figma 自动回退 |
| Noto Serif SC | Noto Serif SC | |
| IBM Plex Mono | IBM Plex Mono | |
| PingFang SC | **Noto Sans SC** | Figma 没有苹方；600 降到 Medium |
| 得意黑（risograph） | 查到就用，查不到 Noto Sans SC | 交付时说明 |

**字体换过就必须告诉用户**，说清哪几个 family 换成了什么，以及这只影响字形、不影响版面位置。

### 3. 一页一次 `use_figma` 建图

用 `scripts/figma_build.js` 做模板，替换开头三个占位：`__DATA__`（这页的 `nodes` JSON）、
`__SLIDE_INDEX__`（0,1,2…决定横向摆放）、`__TARGET_ID__`（用户给的 node id）。
调用前先 load `figma-use` skill，`skillNames` 传 `figma-use`。

模板已经处理好：字体加载、按 DOM 层级嵌套普通 Frame、单边 stroke 还原发丝线、
`setRange*` 还原混排（大数字 + 小单位、`<br>`、`<em>`）、文本框 autoResize 顺序、
短标签自动宽 + 右对齐锚定。每次返回 `textReport`：`htmlH` 和 `figH` 差 2px 以上说明
换行数变了，记下来报给用户。

页与页横向排开，间距 160，从目标区 (80, 80) 起。目标区里已有东西就先扫一遍 children，
把起点挪到空处。

### 4. 自查再交付

模板末尾自带 `screenshot({scale:0.5})`，逐页对着浏览器截图比：有没有文字换行数变了、
标签有没有折行、发丝线位置对不对、页码在不在右上角。

交付时说清楚这几件事：

- Figma 链接（带 node-id）和每页的 rootId
- 推了哪几页，一共多少图层
- **换了哪些字体**
- **`unresolved` 里没还原的视觉**，具体是哪一页哪个元素
- 页码是引擎运行时注入的值（如 `02 / 13`），推过去的就是当时的总页数，只推部分页时提醒用户
- **从这里开始 HTML 不再更新，门禁停在推送前那一版**；用户在 Figma 里改的部分没有程序保障
- 用户自己在 Figma 里 Export（选中 Frame → 右侧 Export → PNG，1x 就是 1920×1080）

## 回流（只在用户明确要求时做）

默认不做。用户说「把 Figma 里的改动同步回来」才做，做之前先说清楚：能带回来的是
**文案和颜色**，带不回来的是位置微调（版面由 chassis 的 CSS 算出来，硬塞绝对坐标会破坏
配方，而且违反「不改 chassis」的红线）。

1. `get_metadata` 拿结构，`use_figma` 读回文字和样式
2. 跟推送时的 extract JSON 逐项比：
   - **文案变了** → 改 `index.html` 对应的字，重跑工作流第 5 条自检（孤字、占位、页码）
   - **颜色变了** → 改 `dnas/*.json` 的 `bg / fg / accent`，重跑 `check_contrast.py`，不写行内 hex
   - **字号 / 间距变了** → 不追。`--sz-*` 和密度是锁死的，告诉用户这类改动只存在于 Figma
   - **位置挪了** → 判断是不是配方意图变了（比如 split 改成单栏）。是就换配方重建；只是挪了几像素就不追
3. 改完重建、门禁全过
4. 报告时分开说：哪些带回来了、哪些没带、HTML 版和 Figma 版现在差在哪

## 已知会掉的东西

| 掉的东西 | 为什么 | 怎么办 |
|---|---|---|
| 伪元素装饰 | extract 只量元素盒 | `unresolved` 里给了内容和声明尺寸，手工补 |
| 渐变 / 背景图 / 阴影 | extract 不解析 | chassis 不用；出现了就是页内自写，手工补或改回实色 |
| transform | 只冻结了 data-anim 的入场位移 | 其余 transform 会进 `unresolved` |
| 图片 / SVG | 当前模板不建图片图层 | 有图的页先说明，需要时用 `upload_assets` 单独补 |
| 翻页动效 | Figma 没有对应物 | 不推，静态页 |
