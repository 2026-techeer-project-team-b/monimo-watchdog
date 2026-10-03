import sys
from pathlib import Path

# Lambda 는 src/ 의 내용물을 zip 루트에 풀어 올리므로 그때와 같은 import 모양으로 맞춘다
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
