"""모델 파일(joblib) 불러오기 — 다른 운영체제에서 저장한 XGBoost 모델도 열리게 한다.

XGBoost 3.4는 모델 안에 난수 상태(rng_state)를 글자로 같이 저장하는데,
이 글자 형식이 운영체제마다 다르다 (Colab·Linux: 10진수 625개 / Windows: 16진수 624개).
그래서 Colab에서 저장한 모델을 Windows에서 열면 'input stream corrupted' 오류가 난다.
예측에는 난수가 쓰이지 않으므로, 열리지 않을 때만 rng_state를 이 PC 형식으로 바꿔 다시 연다.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import joblib
import numpy as np
import xgboost as xgb
import xgboost.core as xgb_core

_RNG_KEY = b"L" + struct.pack(">q", len(b"rng_state")) + b"rng_state"   # UBJSON 키 'rng_state'


def _local_rng_state() -> bytes:
    """이 PC의 XGBoost가 쓰는 형식의 rng_state (아주 작은 모델을 만들어 꺼낸다)."""
    tiny = xgb.train({}, xgb.DMatrix(np.zeros((2, 1)), label=[0, 1]), num_boost_round=1)
    return json.loads(tiny.save_config())["learner"]["generic_param"]["rng_state"].encode()


def _swap_rng_state(buf: bytes, new_state: bytes) -> bytes:
    i = buf.find(_RNG_KEY)
    if i < 0:
        raise ValueError("rng_state not found")
    start = i + len(_RNG_KEY)                    # 그 뒤: 'S' 'L' 8바이트 길이 + 글자
    if buf[start:start + 2] != b"SL":
        raise ValueError("unexpected rng_state encoding")
    n = struct.unpack(">q", buf[start + 2:start + 10])[0]
    return buf[:start] + b"SL" + struct.pack(">q", len(new_state)) + new_state + buf[start + 10 + n:]


def load_bundle(path: Path) -> dict:
    original = xgb_core.Booster.__setstate__
    local_state: list[bytes] = []

    def setstate(self, state):
        try:
            original(self, dict(state))
        except xgb_core.XGBoostError:
            if not local_state:
                local_state.append(_local_rng_state())
            fixed = dict(state, handle=bytearray(_swap_rng_state(bytes(state["handle"]), local_state[0])))
            original(self, fixed)

    xgb_core.Booster.__setstate__ = setstate
    try:
        return joblib.load(path)
    finally:
        xgb_core.Booster.__setstate__ = original
