"""지연 예측 모델 불러오기, 편명 조회, 예측, 예측 근거 설명.

2주차 Colab에서 저장한 파일을 그대로 쓴다.
- models/지연예측_모델.joblib : Pipeline(원-핫 인코더 + XGBoost) + 사용 변수 + 판정 기준
- models/편명_조회표.csv      : 편명 → 항공사·도착지·구분·운항횟수·편명지연율·평소출발시
- models/시간대별_지연비율.csv : 0~23시 평균 지연 비율
- models/월별_평균날씨.csv     : 날씨 예보를 못 불러올 때 쓰는 월평균
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from backend.airports import code_of
from backend.model_loader import load_bundle

MODEL_DIR = Path(__file__).resolve().parent / "models"

# 화면에 보여줄 단계 (디자인 기준): 15% 미만 낮음 / 15~35% 보통 / 35% 이상 높음
LOW, HIGH = 0.15, 0.35


def level_of(prob: float) -> str:
    if prob < LOW:
        return "낮음"
    if prob < HIGH:
        return "보통"
    return "높음"


def normalize_flight(no: str) -> str:
    return "".join(str(no).split()).upper()


class Predictor:
    def __init__(self, model_dir: Path = MODEL_DIR, model_file: str = "지연예측_모델.joblib"):
        bundle = load_bundle(model_dir / model_file)
        self.pipeline = bundle["pipeline"]
        self.cat_cols = list(bundle["cat_cols"])
        self.num_cols = list(bundle["num_cols"])
        self.threshold = float(bundle["threshold"])
        self.prior = float(bundle["prior"])          # 학습 데이터 평균 지연 비율 (약 0.211)

        self.lookup = pd.read_csv(model_dir / "편명_조회표.csv").set_index("편명")
        hourly = pd.read_csv(model_dir / "시간대별_지연비율.csv")
        self.hourly = dict(zip(hourly["시"].astype(int), hourly["지연비율"].astype(float)))
        self.monthly_weather = pd.read_csv(model_dir / "월별_평균날씨.csv").set_index("월")

    # ---------- 조회 ----------
    def find_flight(self, flight_no: str) -> dict | None:
        no = normalize_flight(flight_no)
        if no not in self.lookup.index:
            return None
        r = self.lookup.loc[no]
        return {
            "편명": no,
            "항공사": r["항공사"],
            "도착지": r["도착지"],
            "도착코드": code_of(r["도착지"]),
            "구분": r["구분"],
            "운항횟수": int(r["운항횟수"]),
            "편명지연율": float(r["편명지연율"]),
            "평소출발시": int(r["평소출발시"]),
            "평소출발시각": r["평소출발시각"],
        }

    def destinations(self, min_flights: int = 30) -> list[str]:
        """여객편 도착지를 운항이 많은 순서로."""
        p = self.lookup[(self.lookup["구분"] == "여객") & (self.lookup["운항횟수"] >= min_flights)]
        return p.groupby("도착지")["운항횟수"].sum().sort_values(ascending=False).index.tolist()

    def flights_to(self, dest: str, min_flights: int = 30) -> pd.DataFrame:
        p = self.lookup[(self.lookup["도착지"] == dest) & (self.lookup["구분"] == "여객")
                        & (self.lookup["운항횟수"] >= min_flights)]
        return p.reset_index().sort_values("평소출발시각")

    def monthly_average_weather(self, month: int) -> dict:
        r = self.monthly_weather.loc[month]
        return {"풍속": float(r["풍속"]), "기온": float(r["기온"]), "강수량": float(r["강수량"])}

    # ---------- 예측 ----------
    def _row(self, info: dict, dep: datetime, weather: dict) -> dict:
        return {
            "항공사": info["항공사"], "도착지": info["도착지"], "구분": info["구분"],
            "시": dep.hour, "요일": dep.weekday(), "월": dep.month,
            "풍속": float(weather["풍속"]), "기온": float(weather["기온"]), "강수량": float(weather["강수량"]),
            "편명지연율": info["편명지연율"],
        }

    def predict_rows(self, rows: list[dict]) -> list[float]:
        X = pd.DataFrame(rows)[self.cat_cols + self.num_cols]
        return [float(p) for p in self.pipeline.predict_proba(X)[:, 1]]

    def predict(self, flight_no: str, dep: datetime, weather: dict) -> dict | None:
        info = self.find_flight(flight_no)
        if info is None:
            return None
        prob = self.predict_rows([self._row(info, dep, weather)])[0]
        return {
            "flight": info,
            "dep": dep,
            "weather": weather,
            "prob": prob,
            "level": level_of(prob),
            "delayed": prob >= self.threshold,
            "hour_rate": self.hourly.get(dep.hour, self.prior),
            "factors": self.explain(info, dep, weather),
            "message": self.message(prob),
        }

    def compare(self, dest: str, dep_date, weather_by_hour: dict[int, dict]) -> list[dict]:
        """같은 목적지 편들을 평소 출발 시각으로 예측해서 낮은 순서로 정렬."""
        flights = self.flights_to(dest)
        if flights.empty:
            return []
        infos, rows = [], []
        for _, f in flights.iterrows():
            info = self.find_flight(f["편명"])
            hh, mm = map(int, info["평소출발시각"].split(":"))
            dep = datetime(dep_date.year, dep_date.month, dep_date.day, hh, mm)
            w = weather_by_hour.get(dep.hour)
            avg_weather = w is None                      # 예보에 없는 시간대 → 이 달 평균 날씨로 계산
            if avg_weather:
                w = self.monthly_average_weather(dep.month)
            infos.append((info, dep, avg_weather))
            rows.append(self._row(info, dep, w))
        probs = self.predict_rows(rows)
        out = [{"flight": i, "dep": d, "prob": p, "level": level_of(p), "avg_weather": a}
               for (i, d, a), p in zip(infos, probs)]
        return sorted(out, key=lambda r: r["prob"])

    # ---------- 설명 ----------
    def explain(self, info: dict, dep: datetime, weather: dict) -> list[dict]:
        """'이렇게 예측했어요' 카드에 들어갈 3줄. effect: up / down / same"""
        avg = self.prior
        hr = self.hourly.get(dep.hour, avg)
        hour_effect = "up" if hr > avg + 0.03 else ("down" if hr < avg - 0.03 else "same")

        fr = info["편명지연율"]
        flight_effect = "up" if fr > avg + 0.03 else ("down" if fr < avg - 0.03 else "same")

        rain, wind = float(weather["강수량"]), float(weather["풍속"])
        if rain > 0 or wind >= 20:
            w_label = f"비 {rain:g}mm · 바람 {wind:.0f}KT" if rain > 0 else f"바람 강함 {wind:.0f}KT"
            w_effect = "up"
        else:
            w_label = "비 없음 · 바람 " + ("약함" if wind < 12 else "보통")
            w_effect = "same"

        return [
            {"label": f"{dep.hour}시대 출발 · 평균 {hr * 100:.1f}%", "effect": hour_effect},
            {"label": f"{info['편명']} 과거 지연율 {fr * 100:.1f}%", "effect": flight_effect},
            {"label": w_label, "effect": w_effect},
        ]

    def message(self, prob: float) -> dict:
        avg = self.prior
        lvl = level_of(prob)
        if lvl == "낮음":
            return {"title": "제시간에 출발할 가능성이 높아요", "sub": f"평균 {avg * 100:.1f}%보다 낮아요", "tip": ""}
        if lvl == "보통":
            near = abs(prob - avg) < 0.05
            sub = f"평균 {avg * 100:.1f}%와 비슷해요" if near else f"평균 {avg * 100:.1f}%보다 조금 {'높아요' if prob > avg else '낮아요'}"
            return {"title": "평소보다 크게 늦어지진 않을 것 같아요", "sub": sub, "tip": ""}
        times = prob / avg
        return {"title": "출발이 늦어질 가능성이 높아요",
                "sub": f"평균 {avg * 100:.1f}%의 {times:.1f}배",
                "tip": "공항에는 평소대로 가되, 도착 후 일정은 여유 있게 잡으세요."}
