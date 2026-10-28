"""테스트가 app/ 안의 backend·frontend를 import할 수 있게 경로를 잡는다."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
