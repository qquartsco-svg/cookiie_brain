"""DEPRECATED — from analysis.brain_analyzer import BrainAnalyzer 를 사용하세요."""
import warnings as _w
_w.warn("brain_analyzer.py (최상위)는 deprecated. 'from analysis.brain_analyzer import BrainAnalyzer'를 사용하세요.", DeprecationWarning, stacklevel=2)
from analysis.brain_analyzer import BrainAnalyzer  # noqa: F401
__all__ = ["BrainAnalyzer"]
