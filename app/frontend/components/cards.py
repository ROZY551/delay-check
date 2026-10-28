"""결과·비교·기록 화면의 HTML 카드. 디자인 캔버스(결과 C 스타일)를 옮긴 것."""
from __future__ import annotations

from html import escape

WD = "월화수목금토일"
LEVEL_STYLE = {   # 단계별 색: 큰 숫자 / 배지 배경 / 배지 글자 / 막대
    "낮음": {"num": "#7FB2FF", "chip_bg": "#4C8DF6", "chip_fg": "#FFFFFF", "bar": "#1D74E8", "soft": "#E3ECFB", "soft_fg": "#1D4FA8"},
    "보통": {"num": "#FFB81C", "chip_bg": "#FFB81C", "chip_fg": "#0B2545", "bar": "#F2A900", "soft": "#FFF3D1", "soft_fg": "#7A4500"},
    "높음": {"num": "#FF8A57", "chip_bg": "#F0743E", "chip_fg": "#1A0A02", "bar": "#E8590C", "soft": "#FBE3D6", "soft_fg": "#8A2C0D"},
}
EFFECT = {"up": ("지연 ↑", "#9A3412", "#FBE7DC"), "down": ("지연 ↓", "#1D4FA8", "#E3ECFB"), "same": ("영향 적음", "#4A5568", "#EEF1F6")}


def date_kr(dt) -> str:
    return f"{dt.month}월 {dt.day}일 ({WD[dt.weekday()]})"


def route_html(f: dict, size: int = 40, color: str = "#FFFFFF", sub: str = "#B9C6DA") -> str:
    dest = f["도착코드"] or ""
    dest_html = (f'<span class="mono" style="font-size:{size}px;font-weight:800;color:{color}">{dest}</span>'
                 f'<span style="font-size:17px;color:{sub}">{escape(f["도착지"])}</span>') if dest else \
                (f'<span style="font-size:{int(size*0.8)}px;font-weight:900;color:{color}">{escape(f["도착지"])}</span>')
    return (f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">'
            f'<span class="mono" style="font-size:{size}px;font-weight:800;color:{color}">ICN</span>'
            f'<span style="color:#FFB81C;font-size:{int(size*0.6)}px">✈</span>{dest_html}</div>')


def summary_card(r: dict) -> str:
    """결과 맨 위 남색 요약 카드: 항공편 + 큰 지연 확률 + 한 줄 안내 + 단계 막대"""
    f, s, msg = r["flight"], LEVEL_STYLE[r["level"]], r["message"]
    pct = round(r["prob"] * 100)
    tip = f'<p style="margin:4px 0 0;font-size:16px;font-weight:700;color:#FFC9AE">{msg["tip"]}</p>' if msg["tip"] else ""
    return f"""
<section class="dc-summary" style="background:#0B2545;color:#fff;border-radius:24px;box-shadow:0 14px 32px rgba(11,37,69,.22);padding:28px 36px;display:flex;flex-wrap:wrap;align-items:center;gap:20px 36px">
  <div style="flex:999 1 420px;display:flex;flex-direction:column;gap:10px">
    <span style="font-size:16px;color:#B9C6DA"><b style="color:#fff">{escape(f['항공사'])} <span class="mono">{f['편명']}</span></b> · {f['구분']}</span>
    {route_html(f)}
    <span style="font-size:17px;color:#DDE5F0">{date_kr(r['dep'])} <b class="mono" style="color:#fff">{r['dep']:%H:%M}</b> 출발</span>
  </div>
  <div style="flex:1 1 280px;display:flex;flex-direction:column;gap:6px;border-left:1px solid #23406B;padding-left:32px">
    <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px;color:#B9C6DA">지연 확률</span>
      <span class="dc-chip" style="background:{s['chip_bg']};color:{s['chip_fg']};border-radius:999px;padding:4px 12px;font-size:15px;font-weight:900">{r['level']}</span></div>
    <span class="mono" style="font-size:96px;font-weight:800;line-height:1;color:{s['num']}" aria-label="{pct}%"><span class="dc-count" style="--to:{pct}" aria-hidden="true"></span><span style="font-size:44px" aria-hidden="true">%</span></span>
  </div>
  <div style="flex:1 1 100%;display:flex;align-items:center;flex-wrap:wrap;gap:14px 32px;border-top:1px solid #23406B;padding-top:18px">
    <div style="flex:999 1 360px"><p style="margin:0;font-size:20px;font-weight:800">{msg['title']} <span style="font-weight:400;font-size:16px;color:#B9C6DA">· {msg['sub']}</span></p>{tip}</div>
    <div style="flex:1 1 280px;display:flex;flex-direction:column;gap:6px">
      <div class="dc-scale" style="position:relative;height:10px;display:flex">
        <span style="width:15%;background:#4C8DF6;border-radius:5px 0 0 5px"></span><span style="width:20%;background:#FFB81C"></span>
        <span style="width:65%;background:#F0743E;border-radius:0 5px 5px 0"></span>
        <span class="dc-marker" style="position:absolute;left:calc({min(pct, 100)}% - 10px);top:-5px;width:20px;height:20px;border-radius:50%;background:#fff;border:4px solid #0B2545;box-sizing:border-box"></span>
      </div>
      <div style="display:flex;font-size:13px;color:#B9C6DA"><span style="width:15%">낮음</span><span style="width:20%">보통</span><span style="width:65%;text-align:right">높음</span></div>
    </div>
  </div>
</section>"""


def _title(text: str, bg: str, icon: str, stroke: str = "#FFFFFF") -> str:
    anim = ICON_ANIM.get(icon, "")
    return (f'<h3 style="margin:0 0 12px;display:flex;align-items:center;gap:8px;font-size:18px;font-weight:800;color:#0F1B2D">'
            f'<span class="{anim}" style="width:34px;height:34px;border-radius:9px;background:{bg};display:flex;align-items:center;justify-content:center">'
            f'<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{icon}</svg></span>{text}</h3>')


ICON_SUN = '<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6L19 19M5 19l1.4-1.4M17.6 6.4L19 5"></path>'
ICON_RAIN = '<path d="M7 15a5 5 0 1 1 .9-9.9A6 6 0 0 1 19 7a4 4 0 0 1-1 8z"></path><path d="M8 18l-1 3M12 18l-1 3M16 18l-1 3"></path>'
ICON_BULB = '<path d="M9 18h6"></path><path d="M10 22h4"></path><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"></path>'
ICON_BARS = '<path d="M4 20V10"></path><path d="M10 20V4"></path><path d="M16 20v-7"></path><path d="M22 20H2"></path>'
ICON_ANIM = {ICON_SUN: "dc-ic-sun", ICON_RAIN: "dc-ic-rain", ICON_BULB: "dc-ic-bulb", ICON_BARS: "dc-ic-bars"}   # 아이콘마다 다른 움직임 (ui/style.py)


def weather_card(w: dict) -> str:
    rain = w["강수량"] > 0
    hot = lambda cond: "#FBE3D6" if cond else "#EEF2F7"
    note = f"{w.get('출처', '')} · {w.get('발표', '')} 발표" if w.get("출처") != "월평균" else "예보를 불러오지 못해 이 달의 평균 날씨로 계산했어요"
    return f"""<div class="card">{_title('출발 시각 날씨', '#1D74E8', ICON_RAIN if rain else ICON_SUN)}
<b style="font-size:20px">{escape(w.get('설명', ''))}</b>
<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;text-align:center;margin:12px 0">
  <div style="background:{hot(w['풍속'] >= 20)};border-radius:10px;padding:10px 4px"><span style="display:block;font-size:13px;color:#4A5568">풍속</span><b class="mono" style="font-size:20px">{w['풍속']:.0f}KT</b></div>
  <div style="background:#EEF2F7;border-radius:10px;padding:10px 4px"><span style="display:block;font-size:13px;color:#4A5568">기온</span><b class="mono" style="font-size:20px">{w['기온']:.0f}℃</b></div>
  <div style="background:{hot(rain)};border-radius:10px;padding:10px 4px"><span style="display:block;font-size:13px;color:#4A5568">강수</span><b class="mono" style="font-size:20px">{w['강수량']:g}mm</b></div>
</div><span style="font-size:13px;color:#4A5568">{note}</span></div>"""


def factors_card(factors: list[dict]) -> str:
    rows = ""
    for i, fc in enumerate(factors):
        label, fg, bg = EFFECT[fc["effect"]]
        border = "border-bottom:1px solid #EEF1F6;" if i < len(factors) - 1 else ""
        rows += (f'<div class="dc-row" style="animation-delay:{0.3 + i * 0.12:.2f}s;display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 0;{border}">'
                 f'<span style="font-size:16px">{escape(fc["label"])}</span>'
                 f'<span style="font-size:14px;font-weight:800;color:{fg};background:{bg};border-radius:6px;padding:3px 9px;white-space:nowrap">{label}</span></div>')
    return f'<div class="card">{_title("이렇게 예측했어요", "#F2A900", ICON_BULB, "#0B2545")}{rows}</div>'


def chart_title(hour: int, hour_rate: float, avg: float) -> str:
    return (_title("다른 시간대와 비교", "#0E9384", ICON_BARS)
            + f'<span style="font-size:15px;color:#4A5568">{hour}시대 <b style="color:#0F1B2D">{hour_rate*100:.1f}%</b> · 전체 평균 {avg*100:.1f}%</span>')


def recommend_banner(best: dict, dest: str, day, n: int, weather_text: str) -> str:
    f = best["flight"]
    return f"""<section class="dc-up" style="background:#0B2545;color:#fff;border-radius:20px;padding:22px 28px;display:flex;flex-wrap:wrap;align-items:center;gap:14px 28px">
<span class="dc-star" style="background:#FFB81C;color:#0B2545;border-radius:999px;padding:6px 14px;font-size:15px;font-weight:900">★ 가장 덜 늦는 편</span>
<span style="font-size:20px;font-weight:800"><span class="mono" style="color:#FFB81C">{f['편명']}</span> {escape(f['항공사'])} · {best['dep']:%H:%M} 출발 · 지연 확률 <span class="mono" style="color:#FFB81C">{round(best['prob']*100)}%</span></span>
<span style="margin-left:auto;font-size:15px;color:#B9C6DA">{date_kr(day)} {escape(dest)}행 {n}편 · {escape(weather_text)}</span></section>"""


def compare_row(rank: int, item: dict) -> str:
    f, s = item["flight"], LEVEL_STYLE[item["level"]]
    pct = round(item["prob"] * 100)
    bg = "#FFF8E6" if rank == 1 else "#FFFFFF"
    delay = min(rank, 12) * 0.06
    avg_tag = '<span style="font-size:12px;color:#8A9BB5">평균 날씨</span>' if item.get("avg_weather") else ""
    return f"""<div class="dc-cmp-row" style="animation-delay:{delay:.2f}s;display:grid;grid-template-columns:44px 1.5fr .8fr 1fr 2fr .8fr;align-items:center;gap:12px;min-height:60px;padding:0 20px;border-top:1px solid #EEF1F6;background:{bg}">
<span class="mono" style="font-size:17px;font-weight:800;color:#4A5568">{rank}</span>
<span style="display:flex;flex-direction:column"><b class="mono" style="font-size:19px;color:#0B2545">{f['편명']}</b><span style="font-size:14px;color:#4A5568">{escape(f['항공사'])}</span></span>
<span style="display:flex;flex-direction:column"><span class="mono" style="font-size:18px;font-weight:700">{item['dep']:%H:%M}</span>{avg_tag}</span>
<span style="font-size:16px;color:#2D3748">{f['편명지연율']*100:.1f}%</span>
<span style="display:flex;align-items:center;gap:12px"><span style="flex:1;height:12px;border-radius:6px;background:#EEF2F7;overflow:hidden"><span class="dc-fill" style="animation-delay:{delay + 0.2:.2f}s;display:block;height:100%;width:{min(pct*2, 100)}%;background:{s['bar']};border-radius:6px"></span></span><b class="mono" style="font-size:20px;min-width:48px;text-align:right">{pct}%</b></span>
<span><span style="display:inline-block;border-radius:999px;padding:4px 12px;font-size:14px;font-weight:800;background:{s['soft']};color:{s['soft_fg']}">{item['level']}</span></span>
</div>"""


COMPARE_HEAD = """<div style="display:grid;grid-template-columns:44px 1.5fr .8fr 1fr 2fr .8fr;gap:12px;padding:14px 20px;background:#EEF2F7;font-size:14px;font-weight:700;color:#4A5568;border-radius:18px 18px 0 0">
<span>순위</span><span>편명 · 항공사</span><span>평소 출발</span><span>과거 지연율</span><span>예상 지연 확률</span><span>예측 상태</span></div>"""


def history_card(h: dict) -> str:
    from datetime import datetime
    dep = datetime.fromisoformat(h["dep_at"])
    made = datetime.fromisoformat(h["created_at"])
    s = LEVEL_STYLE[h["level"]]
    dest = f'<span class="mono" style="font-size:18px;font-weight:700">ICN → {h["dest_code"]}</span>' if h["dest_code"] else \
           '<span class="mono" style="font-size:18px;font-weight:700">ICN →</span>'
    return f"""<div class="dc-hist" style="display:flex;flex-wrap:wrap;align-items:center;gap:10px 28px">
<div style="flex:999 1 380px;display:flex;flex-direction:column;gap:6px">
  <span style="font-size:14px;color:#4A5568">{made:%m.%d %H:%M} 조회</span>
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap"><b class="mono" style="font-size:22px;color:#0B2545">{h['flight_no']}</b>
  <span style="font-size:15px;color:#4A5568">{escape(h['airline'] or '')}</span>{dest}<span style="font-size:15px;color:#4A5568">{escape(h['dest'] or '')}</span></div>
  <span style="font-size:16px;color:#1C2B40">{date_kr(dep)} {dep:%H:%M} 출발</span>
</div>
<div style="display:flex;align-items:center;gap:14px"><b class="mono" style="font-size:40px;line-height:1;color:{s['soft_fg']}">{round(h['prob']*100)}%</b>
<span style="border-radius:999px;padding:5px 12px;font-size:14px;font-weight:800;background:{s['soft']};color:{s['soft_fg']}">{h['level']}</span></div></div>"""
