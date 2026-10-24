"""결과 카드(PNG) 만들기: 결과를 한 장짜리 그림으로 보여 주고 내려받게 해요.

그림은 사용자의 브라우저 안(canvas)에서 직접 그려서, 서버에 한글 글꼴 파일이 없어도 돼요.
카드에는 이름·학번 같은 개인정보를 넣지 않아요(시민증 닉네임만 선택적으로).
"""
import json
from datetime import datetime, timedelta, timezone

import streamlit.components.v1 as components

try:
    from mascot_ui import _pose_data  # 깡지 그림(있으면 카드에 넣어요)
except Exception:  # 그림이 없어도 카드는 만들어져요.
    _pose_data = None


def show_result_card(card, filename, height=540):
    """card 예시:
    {"color": "#0F766E", "place": "할머니 댁", "game": "할머니 폰 지키기",
     "emoji": "🛡️", "title": "든든한 손주", "subtitle": "송금 차단!",
     "stats": [("판단이 맞은 연락", "7 / 7"), ...],
     "sections": [("💡 기억할 점", ["…", "…", "…"])],
     "nickname": "도토리탐정"(선택), "mascot": "trophy"(선택)}
    """
    data = dict(card)
    data["date"] = datetime.now(timezone(timedelta(hours=9))).strftime("%Y.%m.%d")  # 한국 날짜
    pose = data.pop("mascot", None)
    if pose and _pose_data:
        try:
            data["mascot"] = "data:image/png;base64," + _pose_data(pose)
        except Exception:
            pass
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    components.html(
        TEMPLATE.replace("__DATA__", payload).replace("__FILE__", json.dumps(filename)),
        height=height,
    )


TEMPLATE = """
<div id="result-card-root" style="font-family:'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;text-align:center;">
  <canvas id="c" style="max-width:100%;max-height:440px;width:auto;height:auto;border-radius:18px;box-shadow:0 6px 18px rgba(0,0,0,.15);"></canvas>
  <div style="margin-top:10px;">
    <button id="save" style="background:#20483F;color:#fff;border:0;border-radius:14px;padding:12px 22px;
      font-size:16px;font-weight:800;cursor:pointer;font-family:inherit;">🖼️ 결과 카드 저장 (사진)</button>
  </div>
  <div id="msg" style="font-size:12px;color:#52616B;margin-top:6px;">저장한 사진은 친구에게 보내거나 사진첩에 보관할 수 있어요.</div>
</div>
<script>
const D = __DATA__, FILE = __FILE__;
const W = 1800, P = 64, FONT = "'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif";
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
function font(w, s){ return w + ' ' + s + 'px ' + FONT; }
function wrap(text, maxW, f){
  ctx.font = f; const out = []; let line = '';
  for (const word of String(text).split(' ')) {
    const tryLine = line ? line + ' ' + word : word;
    if (ctx.measureText(tryLine).width <= maxW) { line = tryLine; continue; }
    if (line) out.push(line);
    line = '';
    let piece = '';
    for (const ch of word) {
      if (ctx.measureText(piece + ch).width > maxW) { out.push(piece); piece = ch; } else piece += ch;
    }
    line = piece;
  }
  if (line) out.push(line);
  return out;
}
function rr(x, y, w, h, r, fill, stroke){
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 4; ctx.stroke(); }
}
function layout(draw, img){
  // 가로로 넓은 카드: 왼쪽에 결과·숫자, 오른쪽에 글 묶음을 나란히 놓아 위아래 빈 곳을 줄여요.
  const C = D.color || '#0F766E';
  const LW = 760, RX = P + LW + 56, RW = W - P - RX;
  if (draw) { ctx.fillStyle = C; ctx.fillRect(0, 0, W, 130);
    ctx.fillStyle = '#fff'; ctx.font = font(900, 46); ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText('잠깐!', P, 52);
    ctx.font = font(700, 30); ctx.fillText('🌰 도토리시 · ' + (D.place || ''), P, 100);
    ctx.textAlign = 'right'; ctx.font = font(700, 28); ctx.fillText(D.game || '', W - P, 52); ctx.fillText(D.date, W - P, 98); }
  const LC = P + LW / 2;
  // 왼쪽: 결과
  let y = 160;
  if (draw) { ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.font = font(400, 110); ctx.fillText(D.emoji || '✨', LC, y + 100); }
  y += 135;
  for (const l of wrap(D.title || '', LW, font(900, 60))) { if (draw) { ctx.fillStyle = '#20483F'; ctx.font = font(900, 60); ctx.textAlign = 'center'; ctx.fillText(l, LC, y + 56); } y += 76; }
  if (D.subtitle) {
    if (draw) { ctx.font = font(900, 40); const tw = ctx.measureText(D.subtitle).width + 60;
      ctx.save(); ctx.translate(LC, y + 38); ctx.rotate(-0.05); rr(-tw / 2, -36, tw, 72, 14, 'rgba(255,255,255,.7)', '#D7263D');
      ctx.fillStyle = '#D7263D'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(D.subtitle, 0, 2); ctx.restore(); ctx.textBaseline = 'alphabetic'; }
    y += 104;
  }
  if (D.nickname) { if (draw) { ctx.fillStyle = '#6B4A1E'; ctx.font = font(800, 32); ctx.textAlign = 'center'; ctx.fillText('🪪 시민 ' + D.nickname, LC, y + 30); } y += 56; }
  const stats = D.stats || [];
  if (stats.length) {
    const cols = Math.min(stats.length, 2), gw = (LW - 24 * (cols - 1)) / cols, gh = 120;
    stats.forEach((s, i) => {
      const cx = P + (i % cols) * (gw + 24), cy = y + Math.floor(i / cols) * (gh + 18);
      if (draw) { rr(cx, cy, gw, gh, 24, '#F4F8F6', '#D7E2DD');
        ctx.textAlign = 'center'; ctx.fillStyle = '#52616B'; ctx.font = font(700, 27); ctx.fillText(s[0], cx + gw / 2, cy + 44);
        ctx.fillStyle = '#20483F'; ctx.font = font(900, 42); ctx.fillText(s[1], cx + gw / 2, cy + 96); }
    });
    y += Math.ceil(stats.length / cols) * (gh + 18);
  }
  // 오른쪽: 글 묶음
  let ry = 160;
  for (const [head, lines] of (D.sections || [])) {
    const wrapped = lines.map(t => wrap(t, RW - 100, font(700, 31)));
    const boxH = 86 + wrapped.reduce((a, w) => a + w.length * 44 + 12, 0) + 10;
    if (draw) { rr(RX, ry, RW, boxH, 28, '#FFF8E6', '#E2C98A');
      ctx.textAlign = 'left'; ctx.fillStyle = '#6B4A1E'; ctx.font = font(900, 35); ctx.fillText(head, RX + 30, ry + 58); }
    let ly = ry + 96;
    wrapped.forEach(w => { w.forEach((l, k) => { if (draw) { ctx.fillStyle = '#1F2D29'; ctx.font = font(700, 31);
      if (k === 0) ctx.fillText('•', RX + 34, ly + 8); ctx.fillText(l, RX + 68, ly + 8); } ly += 44; }); ly += 12; });
    ry += boxH + 24;
  }
  // 아래쪽(가로 전체)
  y = Math.max(y + 30, ry + 6);
  const noteLines = D.note || ['교육용 가상 체험 결과예요.', '실제 피해는 112 · 118에 먼저 연락하세요.'];
  const footH = Math.max(img ? 180 : 150, 110 + noteLines.length * 34);
  if (draw) {
    ctx.fillStyle = '#E4E9DD'; ctx.fillRect(P, y, W - 2 * P, 3);
    if (img) {
      const ih = 150, iw = img.width * ih / img.height;
      ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(img, W - P - iw, y + 12, iw, ih); ctx.globalCompositeOperation = 'source-over';
    }
    const note = D.note || ['교육용 가상 체험 결과예요.', '실제 피해는 112 · 118에 먼저 연락하세요.'];
    ctx.textAlign = 'left'; ctx.fillStyle = '#20483F'; ctx.font = font(900, 34); ctx.fillText('멈추고, 확인하고, 판단하기', P, y + 62);
    ctx.fillStyle = '#6B7280'; ctx.font = font(600, 24);
    note.forEach((line, i) => ctx.fillText(line, P, y + 102 + i * 34));
  }
  return y + footH;
}
function fitFrame(){
  const h=Math.ceil(document.getElementById('result-card-root').getBoundingClientRect().height)+24;
  try { if(window.frameElement) window.frameElement.style.height=h+'px'; } catch(e){}
}
new ResizeObserver(fitFrame).observe(document.getElementById('result-card-root'));
window.addEventListener('resize',fitFrame);
function render(img){
  ctx.font = font(700, 32);
  const H = Math.ceil(layout(false, img));
  cv.width = W; cv.height = H;
  ctx.fillStyle = '#FFFEF8'; ctx.fillRect(0, 0, W, H);
  layout(true, img);
  requestAnimationFrame(fitFrame);
}
function start(){
  if (D.mascot) { const img = new Image(); img.onload = () => render(img); img.onerror = () => render(null); img.src = D.mascot; }
  else render(null);
}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(start);
document.getElementById('save').onclick = () => {
  cv.toBlob(b => {
    if(!b)return;
    const a = document.createElement('a'); const url=URL.createObjectURL(b); a.href=url; a.download=FILE;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000);
    document.getElementById('msg').textContent = '저장했어요! 사진첩이나 다운로드 폴더에서 확인하세요.';
  }, 'image/png');
};
</script>
"""
