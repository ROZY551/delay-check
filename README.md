# 딜레이 체크 (DELAY CHECK)

**배포 주소: https://delay-check.streamlit.app**

인천공항 출발 항공편의 **편명 + 출발 날짜 + 출발 시각**을 넣으면, 과거 운항 기록과 기상청 예보로 **지연 확률**을 알려주는 Streamlit 웹앱이에요.

## 폴더 구조

```
delay-check/
├─ app/                        ← 개발 (실행 코드)
│   ├─ main.py                 실행 파일: 페이지 연결
│   ├─ frontend/               화면
│   │   ├─ pages/              home(홈·결과·없는 편명) · compare · history · login · signup
│   │   └─ components/         style(CSS·머리글) · cards(HTML 카드) · charts · hero(슬라이드)
│   └─ backend/                화면과 상관없는 기능
│       ├─ services.py         화면이 부르는 창구: 모델·DB 준비, 날씨 캐시, 예측 실행
│       ├─ predictor.py        편명 조회 · 예측 · 편 비교 · 예측 근거
│       ├─ model_loader.py     모델 파일 불러오기 (Windows에서도 열리게)
│       ├─ weather.py          기상청 단기예보 API
│       ├─ auth.py             회원가입·로그인·조회 기록 (SQLite)
│       ├─ airports.py         도착지 → 공항 코드
│       ├─ models/             2주차 Colab에서 만든 모델·조회표
│       └─ data/               회원·기록 DB가 자동으로 생기는 곳
├─ tests/                      백엔드·화면 자동 테스트
├─ docs/                       ← 기록 (개발일지, 실행 방법, 동작 규칙·한계)
├─ .streamlit/                 색 테마, API 키 예시
└─ requirements.txt
```

화면(`frontend`)은 `backend.services`와 `backend`의 함수만 부르고, `backend`는 Streamlit 화면 코드를 모릅니다.

## 빠른 실행

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```

API 키 설정, Streamlit Cloud 배포, 테스트는 [docs/실행_방법.md](docs/실행_방법.md)를 보세요.

## 문서

- [docs/인수인계.md](docs/인수인계.md): **처음 보는 사람은 여기부터.** 현재 상태, 동작 흐름, 다음 할 일, 함정
- [docs/개발일지.md](docs/개발일지.md): 날짜별 작업 기록
- [docs/실행_방법.md](docs/실행_방법.md): 설치·실행·배포·테스트, 라이브러리 버전 주의
- [docs/동작_규칙과_한계.md](docs/동작_규칙과_한계.md): 화면 동작 규칙, 모델 한계 (결과보고서용)
