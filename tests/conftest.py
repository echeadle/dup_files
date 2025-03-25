import sys
from pathlib import Path

# Add src/ to sys.path for test imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
