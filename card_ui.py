"""결과 카드(PNG) 만들기: 결과를 한 장짜리 그림으로 보여 주고 내려받게 해요.

그림은 사용자의 브라우저 안(canvas)에서 직접 그려서, 서버에 한글 글꼴 파일이 없어도 돼요.
카드에는 이름·학번 같은 개인정보를 넣지 않아요(시민증 닉네임만 선택적으로).
"""
import json
import time

import streamlit.components.v1 as components

try:
    from mascot_ui import _pose_data  # 깡지 그림(있으면 카드에 넣어요)
except Exception:  # 그림이 없어도 카드는 만들어져요.
    _pose_data = None


def show_result_card(card, filename, height=620):
    """card 예시:
    {"color": "#0F766E", "place": "할머니 댁", "game": "할머니 폰 지키기",
     "emoji": "🛡️", "title": "든든한 손주", "subtitle": "송금 차단!",
     "stats": [("판단이 맞은 연락", "7 / 7"), ...],
     "sections": [("💡 기억할 점", ["…", "…", "…"])],
     "nickname": "도토리탐정"(선택), "mascot": "trophy"(선택)}
    """
    data = dict(card)
    data["date"] = time.strftime("%Y.%m.%d")
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
<div style="font-family:'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;text-align:center;">
  <canvas id="c" style="max-width:100%;max-height:520px;width:auto;height:auto;border-radius:18px;box-shadow:0 6px 18px rgba(0,0,0,.15);"></canvas>
  <div style="margin-top:10px;">
    <button id="save" style="background:#20483F;color:#fff;border:0;border-radius:14px;padding:12px 22px;
      font-size:16px;font-weight:800;cursor:pointer;font-family:inherit;">🖼️ 결과 카드 저장 (사진)</button>
  </div>
  <div id="msg" style="font-size:12px;color:#52616B;margin-top:6px;">저장한 사진은 친구에게 보내거나 사진첩에 보관할 수 있어요.</div>
</div>
<script>
const D = __DATA__, FILE = __FILE__;
const W = 1080, P = 72, FONT = "'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif";
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
  let y = 0;
  const C = D.color || '#0F766E';
  // 위쪽 띠
  if (draw) { ctx.fillStyle = C; ctx.fillRect(0, 0, W, 150);
    ctx.fillStyle = '#fff'; ctx.font = font(900, 46); ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText('잠깐!', P, 62);
    ctx.font = font(700, 30); ctx.fillText('🌰 도토리시 · ' + (D.place || ''), P, 112);
    ctx.textAlign = 'right'; ctx.font = font(700, 28); ctx.fillText(D.game || '', W - P, 62); ctx.fillText(D.date, W - P, 108); }
  y = 200;
  // 결과
  if (draw) { ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.font = font(400, 120); ctx.fillText(D.emoji || '✨', W / 2, y + 110); }
  y += 150;
  for (const l of wrap(D.title || '', W - 2 * P, font(900, 64))) { if (draw) { ctx.fillStyle = '#20483F'; ctx.font = font(900, 64); ctx.textAlign = 'center'; ctx.fillText(l, W / 2, y + 60); } y += 80; }
  if (D.subtitle) {
    if (draw) { ctx.font = font(900, 40); const tw = ctx.measureText(D.subtitle).width + 60;
      ctx.save(); ctx.translate(W / 2, y + 38); ctx.rotate(-0.05); rr(-tw / 2, -36, tw, 72, 14, 'rgba(255,255,255,.7)', '#D7263D');
      ctx.fillStyle = '#D7263D'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(D.subtitle, 0, 2); ctx.restore(); ctx.textBaseline = 'alphabetic'; }
    y += 110;
  }
  if (D.nickname) { if (draw) { ctx.fillStyle = '#6B4A1E'; ctx.font = font(800, 32); ctx.textAlign = 'center'; ctx.fillText('🪪 시민 ' + D.nickname, W / 2, y + 30); } y += 60; }
  // 숫자 칸
  const stats = D.stats || [];
  if (stats.length) {
    const cols = Math.min(stats.length, 2), gw = (W - 2 * P - 24 * (cols - 1)) / cols, gh = 130;
    stats.forEach((s, i) => {
      const cx = P + (i % cols) * (gw + 24), cy = y + Math.floor(i / cols) * (gh + 20);
      if (draw) { rr(cx, cy, gw, gh, 24, '#F4F8F6', '#D7E2DD');
        ctx.textAlign = 'center'; ctx.fillStyle = '#52616B'; ctx.font = font(700, 28); ctx.fillText(s[0], cx + gw / 2, cy + 48);
        ctx.fillStyle = '#20483F'; ctx.font = font(900, 44); ctx.fillText(s[1], cx + gw / 2, cy + 104); }
    });
    y += Math.ceil(stats.length / cols) * (gh + 20) + 20;
  }
  // 글 묶음
  for (const [head, lines] of (D.sections || [])) {
    const inner = W - 2 * P - 64;
    const wrapped = lines.map(t => wrap(t, inner - 40, font(700, 32)));
    const boxH = 90 + wrapped.reduce((a, w) => a + w.length * 46 + 14, 0) + 10;
    if (draw) { rr(P, y, W - 2 * P, boxH, 28, '#FFF8E6', '#E2C98A');
      ctx.textAlign = 'left'; ctx.fillStyle = '#6B4A1E'; ctx.font = font(900, 36); ctx.fillText(head, P + 32, y + 60); }
    let ly = y + 100;
    wrapped.forEach(w => { w.forEach((l, k) => { if (draw) { ctx.fillStyle = '#1F2D29'; ctx.font = font(700, 32);
      if (k === 0) ctx.fillText('•', P + 36, ly + 8); ctx.fillText(l, P + 72, ly + 8); } ly += 46; }); ly += 14; });
    y += boxH + 28;
  }
  // 아래쪽
  y += 10;
  const footH = img ? 200 : 110;
  if (draw) {
    if (img) {
      // 깡지 그림의 흰 배경이 카드 바탕색에 묻히도록 곱하기로 그려요.
      const ih = 180, iw = img.width * ih / img.height;
      ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(img, W - P - iw, y, iw, ih); ctx.globalCompositeOperation = 'source-over';
    }
    const note = D.note || ['교육용 가상 체험 결과예요.', '실제 피해는 112 · 118에 먼저 연락하세요.'];
    ctx.textAlign = 'left'; ctx.fillStyle = '#20483F'; ctx.font = font(900, 34); ctx.fillText('멈추고, 확인하고, 판단하기', P, y + 60);
    ctx.fillStyle = '#6B7280'; ctx.font = font(600, 24);
    note.forEach((line, i) => ctx.fillText(line, P, y + 102 + i * 34));
  }
  return y + footH;
}
function render(img){
  ctx.font = font(700, 32);
  const H = Math.ceil(layout(false, img));
  cv.width = W; cv.height = H;
  ctx.fillStyle = '#FFFEF8'; ctx.fillRect(0, 0, W, H);
  layout(true, img);
}
function start(){
  if (D.mascot) { const img = new Image(); img.onload = () => render(img); img.onerror = () => render(null); img.src = D.mascot; }
  else render(null);
}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(start);
document.getElementById('save').onclick = () => {
  cv.toBlob(b => {
    const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = FILE;
    document.body.appendChild(a); a.click(); a.remove();
    document.getElementById('msg').textContent = '저장했어요! 사진첩이나 다운로드 폴더에서 확인하세요.';
  }, 'image/png');
};
</script>
"""
