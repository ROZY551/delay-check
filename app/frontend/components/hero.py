"""홈 맨 위 자동 슬라이드 (4초마다 넘어가고 '1 / 7' 표시, 끝나면 처음으로).

애니메이션: 장이 바뀔 때 서서히 겹쳐 바뀌고(크로스페이드), 배경이 천천히 확대되고,
비행기가 날아 들어오고, 글자가 차례로 올라온다. 구름·별·비·활주로 불빛도 움직인다.

Streamlit에는 슬라이드 기능이 없어서 HTML+JS 조각으로 넣는다.
실제 사진을 쓰려면 SLIDES의 'photo'에 이미지 주소를 넣으면 그림 대신 사진이 깔린다.
"""
from __future__ import annotations

import json

# 학습 데이터에서 따로 계산해 둔 숫자 (models/ 파일에 없는 값). 데이터를 바꾸면 여기만 고치면 된다.
# 시간대별 숫자는 models/시간대별_지연비율.csv에서 자동으로 계산한다 (hero_html 참고).
DATA_PERIOD = "2025.9 ~ 2026.9"
STATS = {
    "최다월": 10, "최다월_비율": 28.4, "최소월": 5, "최소월_비율": 13.8,
    "비_비율": 29.7, "맑음_비율": 20.6, "편수": 237_575,
}
S = STATS

SLIDES = [   # 3·4번째 장의 제목·설명은 hero_html()이 시간대 데이터로 채운다
    {"tag": "딜레이 체크", "title": "출발 전에,\n지연 가능성부터 확인하세요", "sub": "편명과 출발 시각만 넣으면 AI가 지연 확률을 알려드려요.",
     "sky": "#0B2545", "mid": "#123764", "low": "#1B4A80", "ground": "#08192F", "sun": "#FFB81C", "sunY": 340, "stars": True},
    {"tag": "이번 달 체크", "title": f"{S['최다월']}월은 1년 중\n지연이 가장 잦은 달이에요", "sub": f"{S['최다월']}월 평균 지연 비율 {S['최다월_비율']}% · 가장 적은 {S['최소월']}월은 {S['최소월_비율']}%",
     "sky": "#6B2E17", "mid": "#8F3F1E", "low": "#B85527", "ground": "#2A120A", "sun": "#FFD166", "sunY": 330},
    {"tag": "출발 시간 TIP", "title": "", "sub": "",
     "sky": "#245C99", "mid": "#3D78B5", "low": "#6F9FD0", "ground": "#14304F", "sun": "#FFE08A", "sunY": 300, "clouds": True},
    {"tag": "출발 시간 TIP", "title": "", "sub": "",
     "sky": "#071629", "mid": "#0C2340", "low": "#12305A", "ground": "#040E1C", "sun": "#E6ECF5", "sunY": 120, "stars": True},
    {"tag": "날씨 TIP", "title": "비 오는 시간에는\n지연이 더 많아져요", "sub": f"비 올 때 지연 비율 {S['비_비율']}% · 비가 안 올 때 {S['맑음_비율']}%",
     "sky": "#2E3F55", "mid": "#3B4F69", "low": "#4A607D", "ground": "#1A2533", "sun": "", "rain": True, "clouds": True},
    {"tag": "실시간 반영", "title": "출발 시각의 날씨까지\n예보로 반영해요", "sub": "기상청 단기예보의 풍속·기온·강수량을 자동으로 불러와요.",
     "sky": "#1A56B8", "mid": "#2F6BCB", "low": "#5A8DDB", "ground": "#0F2D5C", "sun": "#FFD166", "sunY": 280, "clouds": True},
    {"tag": "학습 데이터", "title": f"{S['편수']:,}편의 운항 기록으로\n학습했어요", "sub": f"인천공항 출발편 {DATA_PERIOD}",
     "sky": "#0B2545", "mid": "#0F2E55", "low": "#163D6E", "ground": "#08192F", "sun": "#FFB81C", "sunY": 372, "stars": True},
]

TEMPLATE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&family=JetBrains+Mono:wght@700&display=swap">
<style>
body{margin:0;font-family:'Noto Sans KR',sans-serif}
.hero{position:relative;height:470px;border-radius:24px;overflow:hidden;background:#0B2545}
/* 슬라이드 7장을 겹쳐 두고, 보이는 장만 서서히 나타난다 (크로스페이드) */
.slide{position:absolute;inset:0;opacity:0;transition:opacity .9s ease;pointer-events:none}
.slide.on{opacity:1}
svg.bg{position:absolute;inset:0;width:100%;height:100%}
/* 배경이 천천히 확대된다 (켄 번스 효과) */
.slide .zoom{transform-origin:600px 300px}
.slide.on .zoom{animation:kenburns 6s ease-out both}
@keyframes kenburns{from{transform:scale(1.08)}to{transform:scale(1)}}
/* 비행기: 오른쪽 아래에서 날아 들어온 뒤 위아래로 살짝 흔들린다 */
.plane{transform-box:fill-box;transform-origin:center}
.slide.on .plane-move{animation:flyin 1.6s cubic-bezier(.2,.8,.2,1) both}
.slide.on .plane{animation:bob 3s ease-in-out 1.6s infinite}
@keyframes flyin{from{transform:translate(260px,120px);opacity:0}to{transform:translate(0,0);opacity:1}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
/* 구름은 옆으로 흘러가고, 별은 반짝이고, 비는 내린다 */
.cloud{animation:drift 14s linear infinite alternate}
.cloud.c2{animation-duration:20s;animation-direction:alternate-reverse}
@keyframes drift{from{transform:translateX(-50px)}to{transform:translateX(50px)}}
.star{animation:twinkle 2.4s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:.25}50%{opacity:1}}
.drop{animation:fall .9s linear infinite}
@keyframes fall{from{transform:translate(0,-60px);opacity:0}20%{opacity:.8}to{transform:translate(-24px,120px);opacity:0}}
/* 해·달이 은은하게 빛난다 */
.sun{animation:glow 4s ease-in-out infinite}
@keyframes glow{0%,100%{opacity:1}50%{opacity:.82}}
/* 활주로 불빛이 앞에서 뒤로 차례로 깜빡인다 */
.lamp{animation:blink 1.5s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:.35}30%{opacity:1}}
/* 글자: 태그 → 제목 → 설명 순서로 아래에서 올라온다 */
.text{position:absolute;left:0;top:0;bottom:0;padding:44px 52px 130px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;gap:14px;max-width:680px;color:#fff}
.text > *{opacity:0;transform:translateY(22px)}
.text.in > *{animation:up .7s cubic-bezier(.2,.8,.2,1) forwards}
.text.in > :nth-child(2){animation-delay:.12s}
.text.in > :nth-child(3){animation-delay:.26s}
@keyframes up{to{opacity:1;transform:none}}
.tag{align-self:flex-start;border:1.5px solid #fff;border-radius:999px;padding:5px 16px;font-size:15px;font-weight:700}
h1{margin:0;font-size:46px;line-height:1.24;font-weight:900;letter-spacing:-.03em;white-space:pre-line}
p{margin:0;font-size:18px;line-height:1.55;color:#EEF2F8}
/* 아래 조작 버튼 + 4초 진행 막대 */
.ctrl{position:absolute;left:50%;bottom:112px;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;background:rgba(8,25,47,.6);border-radius:999px;padding:4px 8px;color:#fff;overflow:hidden}
.row{display:flex;align-items:center;gap:4px}
.ctrl button{width:36px;height:36px;border:none;border-radius:50%;background:transparent;color:#fff;font-size:18px;cursor:pointer;transition:background .2s,transform .2s}
.ctrl button:hover{background:rgba(255,255,255,.16);transform:scale(1.12)}
.ctrl button:active{transform:scale(.92)}
.num{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;min-width:52px;text-align:center;display:inline-block}
.num.pop{animation:pop .45s ease}
@keyframes pop{40%{transform:scale(1.25);color:#FFB81C}}
.bar{position:absolute;left:0;bottom:0;height:3px;width:100%;background:#FFB81C;transform-origin:left;transform:scaleX(0)}
.bar.run{animation:prog 4s linear forwards}
.bar.hold{animation-play-state:paused}
@keyframes prog{to{transform:scaleX(1)}}
@media (max-width:640px){h1{font-size:30px}.text{padding:28px 24px 130px}}
/* 움직임을 줄이도록 설정한 사람에게는 애니메이션을 끈다 */
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.text > *{opacity:1;transform:none}}
</style></head><body>
<div class="hero" id="hero">
<div id="slides"></div>
<div class="text" id="text"><span class="tag" id="tag"></span><h1 id="title"></h1><p id="sub"></p></div>
<div class="ctrl"><div class="row"><button id="prev" aria-label="이전 슬라이드">‹</button><span class="num" id="num"></span>
<button id="next" aria-label="다음 슬라이드">›</button><button id="pause" aria-label="자동 넘김 멈춤">❚❚</button></div><span class="bar" id="bar"></span></div>
</div>
<script>
const S = __SLIDES__;
let i = 0, paused = false, timer = null;
function scene(s){
  let g = `<rect width="1200" height="480" fill="${s.sky}"/><rect y="200" width="1200" height="160" fill="${s.mid}"/><rect y="282" width="1200" height="78" fill="${s.low}"/>`;
  if (s.stars) g += [[120,60],[260,120],[610,44],[720,100],[1080,70],[1160,160],[470,150],[900,40]].map((p,k)=>`<circle class="star" style="animation-delay:${(k*0.37).toFixed(2)}s" cx="${p[0]}" cy="${p[1]}" r="1.8" fill="#DDE5F0"/>`).join('');
  if (s.sun) g += `<circle class="sun" cx="930" cy="${s.sunY}" r="74" fill="${s.sun}"/>`;
  if (s.clouds) g += `<g fill="#fff" opacity=".9"><g class="cloud"><ellipse cx="760" cy="120" rx="90" ry="26"/><ellipse cx="820" cy="102" rx="60" ry="30"/></g><g class="cloud c2"><ellipse cx="1040" cy="190" rx="110" ry="28"/></g></g>`;
  g += `<path d="M0 346 L0 310 L140 310 L140 298 L360 298 L380 280 L560 280 L580 298 L700 298 L700 314 L1010 314 L1010 260 L1020 248 L1040 248 L1050 260 L1050 314 L1200 314 L1200 346 Z" fill="${s.ground}"/><rect y="346" width="1200" height="134" fill="${s.ground}"/>`;
  g += `<polygon points="380,480 820,480 650,346 550,346" fill="#ffffff" opacity=".07"/>`;
  g += [[556,354,2],[538,372,2.4],[514,396,3],[480,428,3.6],[438,466,4.2],[644,354,2],[662,372,2.4],[686,396,3],[720,428,3.6],[762,466,4.2]].map((p,k)=>`<circle class="lamp" style="animation-delay:${((4-k%5)*0.18).toFixed(2)}s" cx="${p[0]}" cy="${p[1]}" r="${p[2]}" fill="#FFB81C"/>`).join('');
  g += `<g class="plane-move"><g class="plane"><g transform="translate(820 150) rotate(-14) scale(1.1)" fill="#F4F6FA"><path d="M0 22 C0 16 8 13 30 13 L150 13 C172 13 184 18 188 24 C184 30 172 33 150 33 L30 33 C8 33 0 28 0 22 Z"/><path d="M78 22 L124 22 L84 74 L66 74 Z"/><path d="M150 14 L170 -18 L182 -18 L176 16 Z"/></g></g></g>`;
  if (s.rain) g += `<g stroke="#C9D6EA" stroke-width="2" stroke-linecap="round" opacity=".75">` + [80,200,330,450,560,660,760,870,980,1090,140,390,610,820,1030].map((x,k)=>`<line class="drop" style="animation-delay:${((k*0.13)%0.9).toFixed(2)}s" x1="${x}" y1="${30+(k%3)*60}" x2="${x-12}" y2="${66+(k%3)*60}"/>`).join('') + `</g>`;
  if (s.photo) g = `<image href="${s.photo}" width="1200" height="480" preserveAspectRatio="xMidYMid slice"/><rect width="1200" height="480" fill="#08192F" opacity=".45"/>`;
  return `<g class="zoom">${g}</g>`;
}
const box = document.getElementById('slides');
box.innerHTML = S.map(s => `<div class="slide"><svg class="bg" viewBox="0 0 1200 480" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${scene(s)}</svg></div>`).join('');
const slides = box.children, text = document.getElementById('text'), num = document.getElementById('num'), bar = document.getElementById('bar');
function restart(el, cls){ el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); }
function show(){
  const s = S[i];
  [...slides].forEach((el, k) => el.classList.toggle('on', k === i));
  document.getElementById('tag').textContent = s.tag;
  document.getElementById('title').textContent = s.title;
  document.getElementById('sub').textContent = s.sub;
  num.textContent = (i+1) + ' / ' + S.length;
  restart(text, 'in'); restart(num, 'pop'); restart(bar, 'run');
  bar.classList.toggle('hold', paused);
}
function go(step){ i = (i + step + S.length) % S.length; show(); }
bar.addEventListener('animationend', () => { if (!paused) go(1); });   // 진행 막대가 다 차면 다음 장
document.getElementById('prev').onclick = () => go(-1);
document.getElementById('next').onclick = () => go(1);
document.getElementById('pause').onclick = (e) => { paused = !paused; e.currentTarget.textContent = paused ? '▶' : '❚❚';
  e.currentTarget.setAttribute('aria-label', paused ? '자동 넘김 재생' : '자동 넘김 멈춤'); bar.classList.toggle('hold', paused); };
if (matchMedia('(prefers-reduced-motion: reduce)').matches) setInterval(() => { if (!paused) go(1); }, 4000);
show();
</script></body></html>"""


def hour_kr(h: int) -> str:
    """5 → '새벽 5시', 19 → '저녁 7시'"""
    if h < 6:
        return f"새벽 {h}시"
    if h < 12:
        return f"오전 {h}시"
    if h == 12:
        return "낮 12시"
    return f"{'오후' if h < 18 else '저녁' if h < 21 else '밤'} {h - 12}시"


def hero_html(hourly: dict[int, float]) -> str:
    """시간대 슬라이드 2장(3·4번째)은 시간대별 지연 비율 파일에서 숫자를 계산해 넣는다."""
    slides = [dict(s) for s in SLIDES]
    day = {h: v for h, v in hourly.items() if 6 <= h <= 21}          # 이용이 많은 낮 시간대 중 가장 적은 때
    lo, hi = min(day, key=day.get), max(hourly, key=hourly.get)
    slides[2].update(title=f"{hour_kr(lo)}대 출발편은\n지연이 가장 적은 편이에요",
                     sub=f"{hour_kr(lo)}대 평균 지연 비율 {hourly[lo]*100:.1f}%")
    slides[3].update(title=f"{hour_kr(hi)}대 출발편은\n10편 중 {round(hourly[hi]*10)}편꼴로 지연돼요",
                     sub=f"{hour_kr(hi)}대 평균 지연 비율 {hourly[hi]*100:.1f}%로 하루 중 가장 높아요.")
    return TEMPLATE.replace("__SLIDES__", json.dumps(slides, ensure_ascii=False))
