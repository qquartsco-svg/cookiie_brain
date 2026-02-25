"""Backward-compatibility re-export.

이 파일은 경로 변경 이전 코드 호환용이다.
실제 구현은 analysis/brain_analyzer.py에 있다.

    from brain_analyzer import BrainAnalyzer   # 옛 경로 (호환)
    from analysis.brain_analyzer import BrainAnalyzer  # 새 경로 (권장)
"""

from analysis.brain_analyzer import BrainAnalyzer  # noqa: F401

__all__ = ["BrainAnalyzer"]
