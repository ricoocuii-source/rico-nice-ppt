---
name: rico-nice-ppt
description: >
  横版 16:9 单文件 HTML PPT。只有一套底盘（字号、页配方、密度、翻页全部锁死）。
  用户侧 7 个一级选项：5 个正反色对（ink / blue / olive / purple / plum，每对一暗一亮纸）
  + 2 个特殊（newspaper-front / risograph）。共 12 套，一套一种纸色。
  触发：rico-nice-ppt、报纸头版、riso、黄油蓝、钴蓝、橄榄橙、紫黄、丁香紫、HTML 演示文稿。
---

# rico-nice-ppt

只有一套底盘。选项分两级：先选 7 个里的一个（5 个色对 + 2 个特殊），选了色对再问暗纸还是亮纸。不要一次把 12 套摊开让人挑。

## 锁死

`chassis/deck.html`：`--sz-display: 7.1vw`、padding、28 个页配方、翻页引擎。不许改字号和页 class。纸面是实色 `--c-bg`，不要 WebGL。`.display` 行高 1.08（中文定版值，不回 0.96）。页眉页脚 label 细体 400（chassis 已定，别改回 600）。底盘默认皮 = risograph（直接打开母版即此观感，构建时被各 DNA 全量覆盖，token 替换按变量名匹配，不依赖默认值）。

**一套一种纸色。** 禁止同一份 HTML 里深浅翻纸、蓝黄翻页。底盘里的 `slide light` / `slide dark` 只保留 class，颜色全部走这一套的 `--c-bg` / `--c-fg`。

## 7 个一级选项，12 套

**5 个色对**：每对只有两个 hex，暗版拿深色当纸、浅色当字，亮版反过来。字色就是强调色，
纯双色，没有第三色。字体统一 Newsreader + 思源宋 / 正文 PingFang SC。

| 色对 id | 两个色 | 暗纸 slug | 亮纸 slug |
|---|---|---|---|
| `ink` | 墨 #181818 / 奶油 #fff9d8 | `ink` | `butter-ink` |
| `blue` | 钴蓝 #1d3784 / 沙 #e9dfb0 | `cobalt` | `butter-blue` |
| `olive` | 橄榄 #2b3321 / 橙 #f7b06d | `olive-orange` | `orange-olive` |
| `purple` | 紫 #46285e / 黄 #e6da77 | `purple-yellow` | `yellow-purple` |
| `plum` | 深紫 #1c1931 / 丁香 #c8b2e5 | `plum-lilac` | `lilac-plum` |

对比度是对称的，一对 hex 过了 7.0 两个方向都过，所以一对只维护两个色值。

**2 个特殊**：不成对，各一套。

| slug | 是什么 | 为什么不并进色对 |
|---|---|---|
| `newspaper-front` | 米纸 #f2eee4 + 黑字 + 报纸红 #9c1f25 强调 | 全体系唯一有第三色（强调 ≠ 字色）的，唯一的红 |
| `risograph` | 米纸 + 得意黑 + 荧光粉 #e8175a + 第二色蓝 #0060b1 | 唯一换字体 |


token：`dnas/<slug>.json`，一套一个文件。色对 → slug 的映射在 `scripts/build_deck.py` 的 `PAIRS`，
`python3 scripts/build_deck.py --list` 打印。

## 颜色只写三个

`dnas/<slug>.json` 的 `colors` 只声明 `bg` / `fg` / `accent` 三个源色，其余全部由
`scripts/tokens.py` 按对比度目标解出来，不手填：

| 槽位 | 用在哪 | 对纸色的对比度下限 |
|---|---|---|
| `--c-fg` | 标题、正文、bullet | 7.0 |
| `--c-fg-2` | 次级正文：dense 栏、flow / cycle / timeline 说明 | 4.9 |
| `--c-fg-3` | mono chrome：kicker、caption、坐标轴、stamp | 4.0 |
| `--c-accent-text` | 强调色用在 label / 正文字号时 | 4.6 |
| `--c-accent-fill` | 强调色做色块：bar、swatch、高亮块 | 3.0 |
| `--c-fill` | 图表里非高亮的柱子和扇区 | 3.2 |
| `--c-hairline` | 所有分割线、发丝线、面板竖线 | 2.1 |
| `--c-band-1..5` | 金字塔色带（带上还压着正文，所以封顶 1.55） | 1.55 → 1.17 |

要给某个槽位手动指定值，在 `colors` 里写上它并加进 `pin` 数组（例：risograph 的
`ink2` 第二色）。

生成前后都跑门禁，12 套一起过：

```bash
python3 scripts/check_contrast.py
```

## 内容语义 → 页配方（role 映射表）

出稿选页按这张表查，不凭感觉。备选列是候选机制的种子：拿不准时用首选和备选各出一版让人挑，不要自己猜偏好。

| role | 内容语义信号 | 首选 | 备选 |
|---|---|---|---|
| cover | 封面：标题 + 副题 + 日期 | cover | — |
| transition | 章节分隔、篇章卡 | chapter | statement |
| statement | 核心判断、论点、金句 | statement | quote |
| breakdown | 目录、结构拆解、要点清单 | list | dense |
| context | 背景铺陈、长段叙述 | editorial | split |
| metrics | 核心数字、KPI | stats | versus / scorecard |
| trend | 走势、时间序列 | trend | chart / vtimeline |
| ranking | 排名、多类目量级对比 | chart--hbar | chart |
| shift | 两期之间的位次 / 区间变化 | slope | dumbbell |
| comparison | 同比、对决、方案 A/B、表格 | compare | table / versus / quadrant |
| distribution | 占比、市占、梯队、漏斗 | pie | pyramid |
| process | 流程、路径、实施步骤 | diagram | cycle / vtimeline |
| case | 典型案例、证言、分屏叙事 | spotlight | split split--major / triptych |
| risks | 风险研判、关键问答 | list | compare |
| observation | 结论、展望、建议 | statement | stats |
| closing | 结尾、行动号召 | end | — |

无图内容不设 image role：按「无图不留空框」文字化，落 editorial / split / spotlight（右栏档案位）。

## 扩展构图

11 个扩展配方，颜色只走 token、字号只用现有 `--sz-*`，SVG 页共用 `.fig-*` 笔画类。样张：`skins/<slug>/seed.html`。

| class | 用途 | 要点 |
|---|---|---|
| `slide--split split--major` | 主次 2:1 双栏（案例、批注） | 副栏是 `.split-text:last-child`，自动带左发丝线 |
| `slide--chart chart--hbar` | 横向条形：排名 / 长标签 / 条目多 | `.hbar-rows` 网格；标签右对齐，条共用左边线 |
| `slide--trend` | 折线趋势 | svg viewBox `0 0 1060 560` + `preserveAspectRatio="xMidYMax meet"` 贴底；右注栏 `.fig-aside` |
| `slide--slope` | 两期位次变迁（斜率图） | 两根竖轴只有两档横轴；高亮线加 `.hi` |
| `slide--scorecard` | 离散五格评分，读等级不读量 | `.score-row` 网格；表头/合计行 2px 线，中间发丝线 |
| `slide--table` | 符号对比表（✓ / — / 短文本） | `.cmp-row`；推荐列表头 `.cmp-head.hi` 顶部 accent 线 |
| `slide--versus` | 两个大数字对决 | `.vs-num` 7vw 镜像对置；`.vs-strip` 三等分次级指标 |
| `slide--quadrant` | 四象限内容卡 | 十字线是 `.quad-grid` 伪元素；y 轴箭头必须包 `<b>↑</b>` 才正立 |
| `slide--spotlight` | 案例聚焦 | 1.3 : 0.7；右栏 `.spot-file` 档案行替代图片位；**h2 + 读数 + 说明必须包进 `.spot-head`**（组内 gap-sm；说明从属读数，自带 0.6vh 微距），与要点组之间才是 gap-lg |
| `slide--triptych` | 三联并置 | 帧沉底与叙事板共用底基线；发丝线在 `.trip-frame-num` 顶上；**每帧顶部必写一行 `.trip-frame-note`**（案例编号 · 主体 · 年份），左叙事板顶部也配一条（案例集 · 来源），咬掉天头留白 |
| `slide--dumbbell` | 两点一线区间变化 | svg 高按行数算（每行 140）；空心点=前值、实心点=今值 |

## 工作流

0. **首次触发必须先做智能推荐**：用户第一次用本 skill 并给出文章/材料时，不要直接开工，也不要把 12 套全摊开。先读完内容，判断它的类型和主题（行业报告 / 产品发布 / 数据复盘 / 深度长文 / 品牌叙事……），然后推荐 2-3 套视觉模板，**每套都给出具体理由**（为什么这个纸色、气质和字体配这篇内容），让用户从中选。用户点名了某套就跳过这步。示例口吻：「这是一篇偏财经的季度复盘，推荐：① 钴蓝暗纸——数字密集时深底金字最稳；② 报纸头版——社论气质配深读结论；③ 奶油墨亮纸——要打印分发就选它。选哪套？」
1. 用户没选也没点名时，问一级选项：5 个色对 + 2 个特殊里选哪个。选了色对再问暗纸还是亮纸。要出预览就同一标题出 3 个封面（不同色对各一个），打开浏览器让人选。
2. 内容按 role 映射表切页。不要只留一句导语：判断页、对照页、列表页要把报告里的数字和分项写进去。无图用双栏文字补密度，不留空。
   - **标题行右侧必须配平**：除叙事页（cover / chapter / statement / quote / end）外，h2 标题行右侧要有 caption 或关键读数，用 `.chart-header` 骨架（左 h2 + 右 `.caption.muted`），不许裸 h2 空着右半行。
   - **亲密性（全局间距分组）**：组内 `--gap-sm`（数字贴自己的说明、标题贴自己的导语），组间 `--gap-lg`（标题组 / 图表组 / 要点组之间），禁止一页里所有块用同一个间距均分。数据/对比类页的 `.slide-body` 已在 chassis 定为 `--gap-lg`，页内新写的组不要用 gap-md 糊平。
   - **同级大字要区分身份**：关键读数（`.fig-num` 类）不能和 h2 同字号同色摆在一起，会被读成标题第二行；spotlight 里已降到 h2 的 0.8 倍，新页照此办理。
   - **页眉统一（无页脚体系）**：除封面外每页都带页眉：左侧写本页 kicker（`<span class="label muted">分类 · 主题</span>`），右侧页码由翻页引擎自动注入（`NN / 总数`），**手写页码一律禁止**。页脚已废弃（CSS 全局隐藏），空间归内容区。
   - **标题距页眉横线固定**：页眉横线到标题的距离全 deck 统一为 chrome 的 `margin-bottom`（gap-md）。split / spotlight 的栏是顶对齐（不许 justify-content:center 让标题下坠）。**顶对齐版式有密度底线**：列内容至少填到版心高度的 3/4，不够就补真实材料（多一条 bullet、一段旁注、一行档案），补不出来就换配方，不许留半页空白。
   - **金色短横线已从体系移除**：任何页都不画 `.rule` / `.chapter-rule` 这类装饰短线；kicker 一律放页眉左侧，标题上方不加装饰元素。
3. 生成：

```bash
python3 scripts/build_deck.py --pair <id> --mode dark|light --out <dest>/index.html
# 特殊两套：
python3 scripts/build_deck.py --pair newspaper-front --out <dest>/index.html
# 直接点 slug 也行：
python3 scripts/build_deck.py --dna <slug> --out <dest>/index.html
# 12 份样张：
python3 scripts/build_deck.py --all
```

`--out` 会把 `assets/vendor/gsap.min.js` 和 `assets/fonts/*.woff2` 复制到 `<dest>/assets/`，
deck 目录自带依赖，file:// 双击打开、断网、整个目录挪走都能用。重复运行幂等，不要手动拷字体。
`--all` 给 12 套 skin 建的是 symlink（`assets/fonts`、`assets/vendor -> ../../../assets/vendor`），只用于样张。

样张：`skins/<slug>/seed.html`。

4. 打开网页看。硬刷新（Cmd+Shift+R）以免 HTML 缓存。
5. 生成后自检（12 套都要过）：`python3 scripts/check_contrast.py` 必须全绿；`build_deck.py`
   不能打出 `! <slug>: placeholder copy still visible`；源码里没有 `报告页`、`Image
   Placeholder`、`id="slide-counter"`、`slide-counter`、`#gl-bg`、`startDeckBG`、
   `webgl-bg.js`、`[Period]` 这类方括号占位；标题折行无孤字；markup 里没有手写页码和 `slide-foot`（页码由引擎注入页眉右上角）。
   翻页：`<dest>/assets/vendor/gsap.min.js` 存在，浏览器里 `<html>` 带 `gsap-enabled`，
   控制台 0 错误，翻页后无残留半透明元素。对照 `references/checklist.md`。

## 翻页动效（GSAP）

引擎在 `chassis/deck.html` 底部，一份代码管 12 套，不逐套改。GSAP 3.15.0 离线放在
`assets/vendor/gsap.min.js`，不用 CDN。

**渐进增强。** 页面先按纯 CSS 跑（`#deck` transform transition + `.is-active [data-anim]`
keyframes），检测到 `window.gsap` 才给 `<html>` 加 `gsap-enabled`，并只在这个状态关掉 CSS
transition 和 keyframes。vendor 丢了、被拦了，键盘 / 滚轮 / 触摸 / 圆点照常能翻，只是没有 GSAP 动效。

**翻页两种，固定不随机：**

| 操作 | 动效 |
|---|---|
| 相邻一页（方向键、滚轮、滑动） | deck 横移 0.55s `power3.inOut`，后退反向 |
| 跨页（圆点、Home、End） | 当前页淡出 0.16s，瞬移 deck，目标页淡入 0.2s，内容入场 0.17s 后起播，不飞过中间页 |

**内容入场按页 class 分四类，同一系统里的变化，不是每页一个特效：**

| 类 | 页 | 入场 |
|---|---|---|
| narrative | cover / chapter / statement / quote / end | y 20px + 淡入 |
| reading | list / editorial / dense / vtimeline | y 14px + 淡入 |
| data | stats / chart / pie / pyramid / cycle / trend / slope / scorecard / table / versus / quadrant / dumbbell | y 10px + scale 0.985 + 淡入 |
| split | split / compare / diagram / spotlight / triptych | x 18px + 淡入，跟翻页方向走 |

顺序用现有 `data-anim` + `data-delay`，DOM 顺序兜底，不改 18 页 markup。相邻翻页时入场延后
0.16s 起播，和横移后半段重叠，整页 ≈450ms 到位；后退时位移取反。结束后 `clearProps`，静止态
和纯 CSS 版逐像素一致。`prefers-reduced-motion: reduce` 下立即切页、内容直接可见。

**改参数只改 chassis 一处，然后 `--all` 重建；已交付的 deck 要同步引擎块（把 `<script src=
"assets/vendor/gsap.min.js">` 到 `</script>` 整段替换成 chassis 里的新版）。**

调试钩子：`window.__deck = { goTo(i, instant), getCurrent(), isAnimating(), isGsapEnabled() }`。

## 红线

- 不改 `--sz-*`、页 class、密度
- 不把选项乘开：色对只有 5 个，一对只有暗 / 亮两个方向，不加第三色、不加中间色；特殊只有 2 个
- **一套一种纸色：** 禁止同一份 deck 里穿插第二套底色（不要深浅翻页）
- 不恢复 80px 网格
- chrome 和 kicker 不是同一句话
- **页码只出现一次：** 由引擎写在页眉右上角（`.chrome-page`，封面除外），markup 里禁止手写任何页码，禁止 `#slide-counter`，禁止页脚。
- **发丝线只用 `--c-hairline`：** 不在使用处写 `color-mix()`，不用 `--c-border`，不用半透明叠加。12 套纸色不一样，写死的透明度在浅纸上会消失
- **小字不用 `--c-accent`：** label、caption、正文里的强调走 `--c-accent-text`；`--c-accent` 只留给 display / h1 / h2 / 大数字，色块走 `--c-accent-fill`
- **不给派生槽位手写 hex：** 改颜色只改 DNA 的 `bg` / `fg` / `accent`，然后重跑门禁
- **16:9 要填满，但别抻：** chart / pyramid / timeline / editorial 这类本来就有内容的页，容器给 `flex: 1` 撑满；stats / list / dense / compare 这类内容天生少的页，内容抱团居中，靠栏顶发丝线把留白框住。三条底线：
  - 不许 `margin-top: auto` 把说明甩到栏底——它会和自己的标题隔开小半页
  - 不许 `justify-content: space-between` 去铺稀疏内容——5 条单行 bullet 会被抻出 145px 的缝
  - 发丝线必须贴着它标注的内容——卡片拉满高、内容居中，会让 `border-top` 悬在半空
- 不要 WebGL 背景，纸面用实色 `--c-bg`
- **动效不加花：** 不旋转、不弹跳、不 3D 翻牌、不 blur、不随机、位移不超过 20px；不引 GSAP 插件，不改成 CDN；不给单页写独立特效
- **禁孤字换行：** 标题、导语、金句折行后，最后一行不得只有 1 个汉字，也不得是「1 个汉字 + 标点」。至少 3 个汉字，英文至少 3 个单词。词不能从中间拆开（如「公斤」拆成「公 / 斤」）。放不下就改写或加 `<br>`，不要靠缩小字号。
- **无图不留空框：** 原文没有图，就不要 Image Placeholder、「报告页」、假手机、假聊天。把 split 改成双栏文字或单栏，用真实内容填满。
