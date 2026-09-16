/**
 * rico-nice-ppt → Figma 载荷提取器（浏览器端，零依赖）
 *
 * 用法：不是 node 脚本。把整个文件内容贴进浏览器的 JS 执行工具里跑
 * （Claude 内置浏览器 javascript_tool / Chrome DevTools Console 都行）。
 * 前提：页面已按 1920×1080 视口打开（resize_window width 1920 height 1080）。
 *
 * 干什么：把 #deck 里的每一页（默认前 3 页，改 SLIDE_RANGE）按真实渲染几何读出来，
 * 返回一份 JSON。Agent 拿它喂给 scripts/figma_build.js 的模板，用 use_figma 重建成
 * 原生可编辑图层（Frame + Text），不是贴图。
 *
 * 为什么先冻结动效：翻页引擎的 GSAP 入场会让 [data-anim] 元素停在 opacity 0 /
 * translateY 的中间态，直接量会量到位移后的坐标。这里先把它们钉到终态再量。
 *
 * 覆盖范围（与 chassis 当前用到的视觉一一对应）：
 *  - 容器：背景实色、四边 border（发丝线）、圆角、opacity、overflow:hidden
 *  - 文字：逐段 font-family / weight / size / italic / color / letter-spacing /
 *          line-height / uppercase；行内 <em> <small> <span> <br> 合成同一文本图层的分段
 *  - 忽略：伪元素、渐变、阴影、transform。chassis 目前不用这些；出现了会写进 unresolved
 *
 * 已知取值差异：
 *  - 字体在 file:// 下可能加载失败，浏览器用回退字体测宽。位置由 vw/vh 决定，不受影响；
 *    单行短标签的宽度会有偏差，figma_build.js 里对短标签用自动宽度兜底
 *  - 页码 .chrome-page 是引擎运行时注入的值，量到什么就是什么
 */
(async () => {
  const SLIDE_RANGE = [0, 3]; // [起, 止) 页索引，改这里
  const INLINE = ['EM', 'SMALL', 'SPAN', 'B', 'STRONG', 'I', 'BR', 'SUP', 'SUB'];

  await new Promise(r => setTimeout(r, 1200));
  // 冻结入场动效到终态
  document.querySelectorAll('[data-anim]').forEach(e => {
    e.style.transform = 'none'; e.style.opacity = '1';
    e.style.clipPath = 'none'; e.style.visibility = 'visible';
  });
  try { if (window.gsap) gsap.globalTimeline.clear(); } catch (_) {}
  await new Promise(r => setTimeout(r, 300));

  const cs = e => getComputedStyle(e);
  const R = v => Math.round(v * 100) / 100;
  const hex = s => {
    const m = s && s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    if (p.length > 3 && p[3] === 0) return null;
    return '#' + p.slice(0, 3).map(x => Math.round(x).toString(16).padStart(2, '0')).join('')
      + (p.length > 3 && p[3] < 1 ? '|' + p[3] : '');
  };
  const fam = ff => ff.split(',')[0].replace(/"/g, '').trim();
  const styleOf = s => ({
    ff: fam(s.fontFamily), fw: s.fontWeight, fs: R(parseFloat(s.fontSize)),
    it: s.fontStyle === 'italic', c: hex(s.color),
    ls: s.letterSpacing === 'normal' ? 0 : R(parseFloat(s.letterSpacing)),
    lh: s.lineHeight === 'normal' ? 0 : R(parseFloat(s.lineHeight)),
    up: s.textTransform === 'uppercase',
  });
  const segs = el => {
    const out = [];
    const walk = (n, inh) => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3) { const t = c.textContent.replace(/\s+/g, ' '); if (t.trim()) out.push({ t, ...inh }); }
        else if (c.nodeType === 1) {
          if (c.tagName === 'BR') { out.push({ t: '\n', ...inh }); continue; }
          walk(c, styleOf(cs(c)));
        }
      }
    };
    walk(el, styleOf(cs(el)));
    if (out.length) { out[0].t = out[0].t.replace(/^\s+/, ''); out[out.length - 1].t = out[out.length - 1].t.replace(/\s+$/, ''); }
    return out;
  };
  const isTextLeaf = el =>
    [...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim()) ||
    ([...el.children].length > 0 && [...el.children].every(c => INLINE.includes(c.tagName) && cs(c).display === 'inline') && el.textContent.trim());

  const unresolved = [];
  const slides = [...document.querySelectorAll('#deck > section.slide')].slice(SLIDE_RANGE[0], SLIDE_RANGE[1]);
  if (!slides.length) throw new Error('没找到 #deck > section.slide，这不是本 skill 的 deck HTML');

  const pages = slides.map((sl, si) => {
    const sr = sl.getBoundingClientRect();
    const nodes = [];
    const visit = (el, parent) => {
      const s = cs(el);
      if (s.display === 'none' || s.visibility === 'hidden') return;
      const r = el.getBoundingClientRect();
      const id = nodes.length;
      const n = { id, p: parent, name: (el.className || el.tagName).toString().replace(' is-active', '').trim(),
        x: R(r.left - sr.left), y: R(r.top - sr.top), w: R(r.width), h: R(r.height) };
      const bg = hex(s.backgroundColor); if (bg) n.bg = bg;
      const bw = [s.borderTopWidth, s.borderRightWidth, s.borderBottomWidth, s.borderLeftWidth].map(parseFloat);
      if (bw.some(x => x > 0)) {
        n.bw = bw;
        // 取第一条非零边的颜色（chassis 的发丝线四边同色）
        const cols = [s.borderTopColor, s.borderRightColor, s.borderBottomColor, s.borderLeftColor];
        n.bc = hex(cols[bw.findIndex(x => x > 0)]);
      }
      if (parseFloat(s.borderTopLeftRadius)) n.rad = parseFloat(s.borderTopLeftRadius);
      if (parseFloat(s.opacity) < 1) n.op = parseFloat(s.opacity);
      if (s.overflow === 'hidden') n.clip = 1;
      if (['center', 'right', 'end'].includes(s.textAlign)) n.ta = s.textAlign;
      if (s.backgroundImage !== 'none') unresolved.push({ page: si, name: n.name, what: 'background-image', value: s.backgroundImage.slice(0, 80) });
      if (s.boxShadow !== 'none') unresolved.push({ page: si, name: n.name, what: 'box-shadow', value: s.boxShadow.slice(0, 80) });
      if (s.transform !== 'none' && !el.hasAttribute('data-anim')) unresolved.push({ page: si, name: n.name, what: 'transform', value: s.transform.slice(0, 80) });
      for (const which of ['::before', '::after']) {
        const ps = getComputedStyle(el, which);
        if (ps.content !== 'none' && ps.content !== 'normal' && ps.display !== 'none')
          unresolved.push({ page: si, name: n.name, what: which, value: `${ps.content} ${ps.width}x${ps.height} ${ps.backgroundColor}` });
      }
      if (isTextLeaf(el)) n.text = segs(el);
      nodes.push(n);
      if (!n.text) for (const c of el.children) visit(c, id);
    };
    visit(sl, null);
    return { index: si, w: R(sr.width), h: R(sr.height), nodes };
  });

  const fonts = [...new Set(pages.flatMap(p => p.nodes.flatMap(n => (n.text || []).map(s => s.ff))))];
  return JSON.stringify({ viewport: { w: innerWidth, h: innerHeight }, fonts, unresolved, pages });
})();
