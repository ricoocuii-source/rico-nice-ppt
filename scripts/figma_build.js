/**
 * rico-nice-ppt → Figma 建图模板（use_figma 代码，零依赖）
 *
 * 用法：不是 node 脚本。每页调一次 use_figma，把本文件内容作为 code 传入，
 * 只替换开头三个占位：
 *   __DATA__        figma_extract.js 输出里 pages[i].nodes 的 JSON
 *   __SLIDE_INDEX__ 这页在目标区里的序号（0,1,2…），决定横向摆放位置
 *   __TARGET_ID__   用户给的 Section / Frame 的 node id（形如 '1043:3401'）
 *
 * 产物：一页一个 1920×1080 Frame，按原 DOM 层级嵌套普通 Frame（绝对定位，不用 AutoLayout），
 * 文字用 setRange* 还原混排（大小号、<br> 换行、<em>）。发丝线走单边 stroke。
 *
 * 字体映射（Figma 里查过的可用性，换过要告诉用户）：
 *   PingFang SC → Noto Sans SC（Figma 没有苹方）
 *   其余 Newsreader / Noto Serif SC / IBM Plex Mono 原样；字重 700→Bold 600→SemiBold 500→Medium 其余 Regular
 *   Noto Sans SC 没有 SemiBold，600 降到 Medium
 *
 * 文本框规则（顺序不能反，反了文本框会塌）：
 *   先 fontName → characters → 逐段 setRange* → textAutoResize → resize(w)
 *   多行 / 宽块：HEIGHT（固定宽自动高）
 *   单行短标签（无换行且宽 < 300）：WIDTH_AND_HEIGHT（自动宽），右对齐的按右边缘锚定；
 *   原因是 file:// 下浏览器可能用回退字体测宽，量到的宽度偏窄，固定宽会让标签换行
 */
const DATA = __DATA__;
const SLIDE_INDEX = __SLIDE_INDEX__;
const TARGET_ID = '__TARGET_ID__';

const target = await figma.getNodeByIdAsync(TARGET_ID);
if (!target) throw new Error('目标节点不存在: ' + TARGET_ID);
const GAP = 160, OX = 80 + SLIDE_INDEX * (1920 + GAP), OY = 80;

const hex = h => { const s = h.split('|'); const v = s[0]; return {
  color: { r: parseInt(v.slice(1, 3), 16) / 255, g: parseInt(v.slice(3, 5), 16) / 255, b: parseInt(v.slice(5, 7), 16) / 255 },
  opacity: s[1] ? parseFloat(s[1]) : 1 }; };
const styleOf = (ff, fw, it) => {
  let family = ff; if (ff === 'PingFang SC') family = 'Noto Sans SC';
  const w = parseInt(fw);
  let st = w >= 700 ? 'Bold' : w >= 600 ? 'SemiBold' : w >= 500 ? 'Medium' : 'Regular';
  if (family === 'Noto Sans SC' && st === 'SemiBold') st = 'Medium';
  if (it) st = st === 'Regular' ? 'Italic' : st + ' Italic';
  return { family, style: st };
};

const need = new Set();
for (const n of DATA) if (n.text) for (const s of n.text) need.add(JSON.stringify(styleOf(s.ff, s.fw, s.it)));
for (const f of need) await figma.loadFontAsync(JSON.parse(f));

const made = {}; const ids = []; const report = [];
for (const n of DATA) {
  const isRoot = n.p === null;
  const parent = isRoot ? target : made[n.p];
  const px = isRoot ? 0 : DATA[n.p].x, py = isRoot ? 0 : DATA[n.p].y;
  let node;
  if (n.text) {
    node = figma.createText(); parent.appendChild(node);
    const first = n.text[0]; node.fontName = styleOf(first.ff, first.fw, first.it);
    node.characters = n.text.map(s => s.t).join('');
    let pos = 0;
    for (const s of n.text) {
      const end = pos + s.t.length;
      if (end > pos) {
        node.setRangeFontName(pos, end, styleOf(s.ff, s.fw, s.it));
        node.setRangeFontSize(pos, end, s.fs);
        node.setRangeFills(pos, end, [{ type: 'SOLID', ...hex(s.c) }]);
        node.setRangeLetterSpacing(pos, end, { unit: 'PIXELS', value: s.ls });
        node.setRangeLineHeight(pos, end, s.lh ? { unit: 'PIXELS', value: s.lh } : { unit: 'AUTO' });
        if (s.up) node.setRangeTextCase(pos, end, 'UPPER');
      }
      pos = end;
    }
    if (n.ta === 'center') node.textAlignHorizontal = 'CENTER';
    else if (n.ta === 'right' || n.ta === 'end') node.textAlignHorizontal = 'RIGHT';
    const single = !node.characters.includes('\n') && n.w < 300;
    if (single) {
      node.textAutoResize = 'WIDTH_AND_HEIGHT';
    } else {
      node.textAutoResize = 'HEIGHT';
      node.resize(n.w, n.h);
      node.textAutoResize = 'HEIGHT'; // resize 会把它打回 NONE，再设一次
    }
    node.x = n.x - px + (isRoot ? OX : 0); node.y = n.y - py + (isRoot ? OY : 0);
    if (single && node.textAlignHorizontal === 'RIGHT') node.x = (n.x - px) + n.w - node.width;
    report.push({ t: node.characters.slice(0, 10), htmlH: n.h, figH: Math.round(node.height * 100) / 100 });
  } else {
    node = figma.createFrame(); node.name = n.name; parent.appendChild(node);
    node.resize(n.w, n.h);
    node.fills = n.bg ? [{ type: 'SOLID', ...hex(n.bg) }] : [];
    node.clipsContent = !!n.clip;
    if (n.bw) {
      node.strokes = [{ type: 'SOLID', ...hex(n.bc) }]; node.strokeAlign = 'INSIDE';
      node.strokeTopWeight = n.bw[0]; node.strokeRightWeight = n.bw[1];
      node.strokeBottomWeight = n.bw[2]; node.strokeLeftWeight = n.bw[3];
    }
    if (n.rad) node.cornerRadius = n.rad;
    node.x = n.x - px + (isRoot ? OX : 0); node.y = n.y - py + (isRoot ? OY : 0);
  }
  if (n.op) node.opacity = n.op;
  made[n.id] = node; ids.push(node.id);
}
await made[0].screenshot({ scale: 0.5 });
return { createdNodeIds: ids, rootId: made[0].id, textReport: report };
