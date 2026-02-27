"""Backward-compat shim — 실제 코드는 solar/core/evolution_engine.py"""
from .core.evolution_engine import *  # noqa: F401,F403
from .core.evolution_engine import EvolutionEngine, Body3D, SurfaceOcean
