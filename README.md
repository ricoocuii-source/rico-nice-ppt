# rico-nice-ppt

把一篇中文报告、方案或分享稿，做成横版 16:9 的单文件 HTML 演示文稿：双击即放，断网可用，整个目录挪走照常工作。

- **一套锁死的底盘。** 字号只有 8 级 token，28 个页配方，间距按亲密性分组（组内 `--gap-sm` / 组间 `--gap-lg`），翻页引擎一份代码管全部模板。版式不靠临场发挥。
- **12 套视觉模板，一套一种纸色。** 每套配色 DNA 只声明 `bg` / `fg` / `accent` 三个源色，其余 9 个槽位（次级正文、mono chrome、色块、发丝线、金字塔色带…）由 `tokens.py` 按对比度目标自动解出，不手填 hex。
- **对比度是门禁，不是建议。** 正文文字对纸色 7.0 起步，次级 4.9，发丝线 2.1，12 套一起跑 `check_contrast.py`，不过不出稿。
- **内容 → 版式有映射表。** 16 个内容语义 role（metrics / trend / ranking / shift / comparison / distribution / process / case…）各有首选和备选配方，选页查表不凭感觉；另有 11 种数据构图（横向条形、折线趋势、斜率图、哑铃图、四象限、评分卡、对决数字、三联并置…），排名、区间变化、离散评分各有专门的画法。
- **离线单文件。** 字体 woff2 和翻页引擎本地打包进 deck 目录，不连 CDN、不连 Google Fonts。GSAP 丢了也能翻页，只是没有动效。

---

## 视觉模板

12 套，先选一级（5 个正反色对 + 2 个特殊），选了色对再定暗纸还是亮纸。同一份 deck 里只有一种纸色，不做深浅翻页。

### ink 墨 · `ink`（暗）

通用汇报的默认款。夜场路演、投屏、光线可控的场合。拿不准选什么就用它。

<img src="docs/shots/ink-1.png" width="30%"> <img src="docs/shots/ink-2.png" width="30%"> <img src="docs/shots/ink-3.png" width="30%">

### 奶油墨 · `butter-ink`（亮）

ink 的亮纸孪生。日光例会、会议室白墙、需要打印或转 PDF 分发时用这套。

<img src="docs/shots/butter-ink-1.png" width="30%"> <img src="docs/shots/butter-ink-2.png" width="30%"> <img src="docs/shots/butter-ink-3.png" width="30%">

### 钴蓝 · `cobalt`（暗）

财经、商务、数据密集内容。深蓝纸配沙色字，大量数字和图表压得住。

<img src="docs/shots/cobalt-1.png" width="30%"> <img src="docs/shots/cobalt-2.png" width="30%"> <img src="docs/shots/cobalt-3.png" width="30%">

### 黄油蓝 · `butter-blue`（亮）

cobalt 的亮纸版。同样面向财经和商务，适合需要长时间阅读的数据报告。

<img src="docs/shots/butter-blue-1.png" width="30%"> <img src="docs/shots/butter-blue-2.png" width="30%"> <img src="docs/shots/butter-blue-3.png" width="30%">

### 橄榄橙 · `olive-orange`（暗）

消费、生活方式、餐饮零售。橄榄绿纸 + 橙字，暖而不甜。

<img src="docs/shots/olive-orange-1.png" width="30%"> <img src="docs/shots/olive-orange-2.png" width="30%"> <img src="docs/shots/olive-orange-3.png" width="30%">

### 橙橄榄 · `orange-olive`（亮）

olive-orange 的亮纸版。品类汇报、门店分享、面向客户的提案。

<img src="docs/shots/orange-olive-1.png" width="30%"> <img src="docs/shots/orange-olive-2.png" width="30%"> <img src="docs/shots/orange-olive-3.png" width="30%">

### 紫黄 · `purple-yellow`（暗）

创意提案、品牌叙事。对比强，适合金句页和章节卡多的结构。

<img src="docs/shots/purple-yellow-1.png" width="30%"> <img src="docs/shots/purple-yellow-2.png" width="30%"> <img src="docs/shots/purple-yellow-3.png" width="30%">

### 黄紫 · `yellow-purple`（亮）

purple-yellow 的亮纸版。品牌 campaign 复盘、创意评审这类要打印挂墙的场合。

<img src="docs/shots/yellow-purple-1.png" width="30%"> <img src="docs/shots/yellow-purple-2.png" width="30%"> <img src="docs/shots/yellow-purple-3.png" width="30%">

### 丁香紫 · `plum-lilac`（暗）

科技、学术、前沿议题。深紫纸偏冷，图表和公式不抢戏。

<img src="docs/shots/plum-lilac-1.png" width="30%"> <img src="docs/shots/plum-lilac-2.png" width="30%"> <img src="docs/shots/plum-lilac-3.png" width="30%">

### 紫丁香 · `lilac-plum`（亮）

plum-lilac 的亮纸版。论文汇报、技术评审、研究综述。

<img src="docs/shots/lilac-plum-1.png" width="30%"> <img src="docs/shots/lilac-plum-2.png" width="30%"> <img src="docs/shots/lilac-plum-3.png" width="30%">

### 报纸头版 · `newspaper-front`

米纸 + 黑字 + 报纸红强调。全体系唯一强调色不等于字色的一套，也是唯一的红。深读报告、社论、行业白皮书。

<img src="docs/shots/newspaper-front-1.png" width="30%"> <img src="docs/shots/newspaper-front-2.png" width="30%"> <img src="docs/shots/newspaper-front-3.png" width="30%">

### 双色印刷 · `risograph`

米纸 + 得意黑 + 荧光粉 + 第二色蓝，全体系唯一换字体的一套。发布会、社区分享、个性场合。

<img src="docs/shots/risograph-1.png" width="30%"> <img src="docs/shots/risograph-2.png" width="30%"> <img src="docs/shots/risograph-3.png" width="30%">

---

## 安装

不绑定任何单一 Agent。适用于 Claude Code、Codex、WorkBuddy 等支持 skill / 自定义指令的 Agent，把仓库 clone 进你的 Agent 读取 skill 的目录即可。

```bash
git clone https://github.com/ricoocuii-source/rico-nice-ppt.git <你的-skills-目录>/rico-nice-ppt
```

Claude Code 为例：

```bash
git clone https://github.com/ricoocuii-source/rico-nice-ppt.git ~/.claude/skills/rico-nice-ppt
```

其他 Agent 换成各自的 skill / prompt 目录即可，SKILL.md 本身就是规范正文，不依赖任何宿主特性。

依赖：Python 3（只用标准库）。字体和 GSAP 已随仓库打包，无需额外下载。

---

## 使用

### 触发

对着 Agent 说：

- `rico-nice-ppt 把这份报告做成 PPT`
- `用报纸头版做一版`
- `riso 那套，发布会用`
- `这份材料出一个 HTML 演示文稿，钴蓝`

### 选模板

首次使用、没点名模板时，skill 会先判断文章类型，推荐 2-3 套并附理由（例如「数据密集的季度复盘 → cobalt 或 butter-blue，夜场投屏选前者」），等你拍板再开工。要看实物就用同一个标题出 3 个封面各一套，打开浏览器挑，不会把 12 套一次摊开。

### 构建

```bash
# 色对 + 暗/亮
python3 scripts/build_deck.py --pair ink --mode dark --out <dest>/index.html

# 直接点 slug
python3 scripts/build_deck.py --dna newspaper-front --out <dest>/index.html

# 12 套样张一次出全
python3 scripts/build_deck.py --all
```

`--out` 会把字体和 GSAP 复制进 `<dest>/assets/`，重复运行幂等。`--pair` 的 id 列表用 `--list` 打印。

### 门禁

```bash
python3 scripts/check_contrast.py
```

12 套一起过，全绿才算数。出稿后还要确认：`build_deck.py` 没打出 `placeholder copy still visible`；源码里没有方括号占位和手写页码；标题折行没有孤字；浏览器控制台 0 错误。完整清单见 `references/checklist.md`。

---

## 目录结构

```
rico-nice-ppt/
├─ SKILL.md              # 唯一规范：红线、role 映射表、工作流
├─ chassis/deck.html     # 锁死的底盘：字号 token、28 个页配方、翻页引擎
├─ dnas/<slug>.json      # 12 套配色 DNA，每套只声明 3 个源色
├─ scripts/
│  ├─ build_deck.py      # 构建，--pair / --dna / --all / --list
│  ├─ tokens.py          # 按对比度目标解出其余 9 个色槽
│  ├─ check_contrast.py  # 门禁
│  └─ content_fills.py
├─ assets/
│  ├─ fonts/*.woff2      # 本地字体
│  └─ vendor/gsap.min.js # GSAP 3.15.0，不走 CDN
└─ references/checklist.md
```

---

## 设计原则（摘自 SKILL.md）

- **一套一种纸色。** 禁止同一份 deck 里深浅翻纸、蓝黄翻页。底盘里的 light / dark class 只保留结构，颜色全部走这套的 `--c-bg` / `--c-fg`。
- **无页脚，页码由引擎注入。** 页脚已废弃，空间归内容区；页码只在页眉右上角出现一次，markup 里手写页码一律禁止。
- **密度底线。** 顶对齐版式的列内容至少填到版心高度的 3/4，补不出真实材料就换配方，不许留半页空白。不用 `space-between` 去抻稀疏内容，5 条单行 bullet 会被拉出 145px 的缝。
- **禁孤字换行。** 标题、导语、金句折行后，最后一行不得只有 1 个汉字或「1 个汉字 + 标点」，中文至少 3 字、英文至少 3 词，词不能从中间拆开。放不下就改写或加 `<br>`，不靠缩小字号。
- **无图不留空框。** 原文没有图就不造 Image Placeholder、假手机、假聊天。把 split 改成双栏文字或单栏，用真实内容填满。
- **不给派生槽位手写 hex。** 改颜色只改 DNA 的 `bg` / `fg` / `accent`，然后重跑门禁。发丝线只用 `--c-hairline`，不在使用处写 `color-mix()`，写死的透明度在浅纸上会消失。
- **动效不加花。** 翻页只有两种：相邻页横移 0.55s，跨页淡出瞬移淡入。内容入场按页 class 分四类，位移不超过 20px，不旋转、不弹跳、不 3D、不随机。`prefers-reduced-motion` 下直接切页。

---

## FAQ

**能导出 PPTX 或 PDF 吗？**
产出是浏览器里的 HTML。要 PDF 就用浏览器打印成 16:9 横版，亮纸的 6 套（`butter-ink` / `butter-blue` / `orange-olive` / `yellow-purple` / `lilac-plum` / `newspaper-front`）为打印场景准备。不生成 PPTX。

**能改字号、加一套自己的配色吗？**
字号和页配方是锁死的，改了整套间距体系会垮。配色可以加：在 `dnas/` 下新建一个 json，只写 `bg` / `fg` / `accent`，跑一遍 `check_contrast.py`，过 7.0 就能用。个别槽位要手动指定，把它写进 `colors` 并加入 `pin` 数组。

**发出去的 deck 依赖网络吗？**
不依赖。字体和 GSAP 都在 deck 自己的 `assets/` 里，file:// 双击打开、断网、整个目录拷给别人都正常。

---

致谢：感谢所有给版式挑过毛病的人。

License: 见 LICENSE
