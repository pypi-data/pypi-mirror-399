import sys
from pathlib import Path

from diff_1c.core import run

sys.path.insert(0, Path(__file__).parent.parent)

if __name__ == "__main__":
    run()
