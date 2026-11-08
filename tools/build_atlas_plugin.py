"""Source-checkout entry point for the portable offline reference builder."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "fo-data-atlas" / "scripts"))
from build_references import *

if __name__ == "__main__":
    import runpy
    runpy.run_path(str(PACK / "scripts" / "build_references.py"), run_name="__main__")
