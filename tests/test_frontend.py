"""화면 테스트: 페이지마다 오류 없이 그려지는지 (Streamlit AppTest, 날씨 API 키 없이)."""
from datetime import time

import pytest
from streamlit.testing.v1 import AppTest

from conftest import ROOT

MAIN = str(ROOT / "app" / "main.py")


def run(page: str | None = None, **state) -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=60)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    if page:
        at.switch_page(page).run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("page", [None, "frontend/pages/compare.py", "frontend/pages/history.py",
                                  "frontend/pages/login.py", "frontend/pages/signup.py"])
def test_page_renders(page):
    run(page)


def search(flight_no: str) -> AppTest:
    at = run()
    at.text_input(key="flight_no").input(flight_no)
    at.time_input(key="dep_time").set_value(time(10, 0))
    next(b for b in at.button if b.label == "지연 확률 확인").click().run()
    assert not at.exception, at.exception
    return at


def test_search_known_flight_shows_result():
    at = search("KE705")
    assert at.session_state["view"] == "result"
    assert at.session_state["result"]["flight"]["편명"] == "KE705"


def test_search_unknown_flight_shows_notfound():
    assert search("ZZ9999").session_state["view"] == "notfound"
