# CLAUDE.md

작업을 시작하기 전에 **[docs/인수인계.md](docs/인수인계.md)**를 먼저 읽으세요. 프로젝트 설명, 현재 상태, 다음 할 일, 실제로 겪은 함정이 모두 정리돼 있어요.

- 실행: `streamlit run app/main.py` (저장소 맨 위에서) · 테스트: `.venv/Scripts/python -m pytest tests`
- Windows + Git Bash에서는 한글 출력 때문에 `PYTHONUTF8=1`을 붙여 실행하세요
- 기록은 `docs/`, 코드는 `app/` (`frontend/` 화면, `backend/` 기능). 작업이 끝나면 `docs/개발일지.md` 맨 위에 기록을 추가하세요
- `.streamlit/secrets.toml`(기상청 키)은 절대 커밋하거나 출력하지 마세요
- 사용자와는 한국어로 대화합니다
