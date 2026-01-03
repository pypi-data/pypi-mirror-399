"""
Haze-Library: High-Performance Quantitative Trading Indicators
==============================================================

Rust-powered technical indicators for Python with 200+ indicators.

Usage:
------
    # Direct function calls
    from haze_library import py_sma, py_rsi, py_macd

    sma = py_sma(close_prices, 20)
    rsi = py_rsi(close_prices, 14)

    # DataFrame accessor (recommended)
    import pandas as pd
    import haze_library

    df = pd.read_csv('ohlcv.csv')
    df['sma_20'] = df.haze.sma(20)
    df['rsi_14'] = df.haze.rsi(14)
    upper, middle, lower = df.haze.bollinger_bands(20, 2.0)

    # Series accessor
    df['close'].haze.sma(20)
    df['close'].haze.rsi(14)

Performance:
-----------
    - 5-10x faster than pure Python implementations
    - 4.8-6.3x faster than TA-Lib for most indicators
    - High numerical precision using f64
"""

__version__ = "1.1.3"
__author__ = "kwannz"

import inspect
from typing import Any, Callable

# Import Rust extension
try:
    from .haze_library import *
except ImportError:
    import warnings
    warnings.warn(
        "Could not import Rust extension module. "
        "Please ensure the package is properly installed."
    )

# -----------------------------------------------------------------------------
# Clean API aliases (no `py_` prefix)
# -----------------------------------------------------------------------------

_KW_ALIASES: dict[str, str] = {
    "close": "values",
    "std_dev": "std_multiplier",
    "std": "std_multiplier",
    "fast": "fast_period",
    "slow": "slow_period",
    "signal": "signal_period",
    "long": "long_period",
    "short": "short_period",
}


def _make_clean_wrapper(
    py_func: Callable[..., Any], *, clean_name: str
) -> Callable[..., Any]:
    signature = inspect.signature(py_func)
    parameter_names = set(signature.parameters)

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        for alias_name, real_name in _KW_ALIASES.items():
            if (
                alias_name in kwargs
                and alias_name not in parameter_names
                and real_name in parameter_names
                and real_name not in kwargs
            ):
                kwargs[real_name] = kwargs.pop(alias_name)
        return py_func(*args, **kwargs)

    wrapper.__name__ = clean_name
    wrapper.__qualname__ = clean_name
    wrapper.__doc__ = getattr(py_func, "__doc__", None)
    return wrapper


def _install_clean_api_aliases() -> dict[str, str]:
    mapping: dict[str, str] = {}

    for name, obj in list(globals().items()):
        if not name.startswith("py_"):
            continue

        clean_name = name[3:]
        if clean_name in globals():
            mapping[name] = clean_name
            continue

        if callable(obj):
            globals()[clean_name] = _make_clean_wrapper(obj, clean_name=clean_name)
        else:
            globals()[clean_name] = obj
        mapping[name] = clean_name

    return mapping


# Mapping from legacy `py_*` function names to clean names. Used for tooling/tests.
_PY_PREFIX_ALIASES = _install_clean_api_aliases()

# Register pandas accessor (import triggers side-effect registration)
try:
    from . import accessor as _accessor  # noqa: F401 - side-effect import
    from .accessor import TechnicalAnalysisAccessor, SeriesTechnicalAnalysisAccessor
except ImportError:
    # pandas not available
    TechnicalAnalysisAccessor = None
    SeriesTechnicalAnalysisAccessor = None

# NumPy compatibility layer (no-prefix functions returning np.ndarray)
try:
    from . import numpy_compat as np_ta
except ImportError:
    np_ta = None

# AI indicator helpers
from .ai_indicators import adaptive_rsi, ensemble_signal, ml_supertrend

# LT (Long-Term) indicator - 10 SFG indicators combination
from .lt_indicators import lt_indicator

# Streaming/incremental calculators
try:
    from .streaming import (
        IncrementalSMA,
        IncrementalEMA,
        IncrementalRSI,
        IncrementalATR,
        IncrementalMACD,
        IncrementalBollingerBands,
        IncrementalStochastic,
        IncrementalSuperTrend,
        IncrementalAdaptiveRSI,
        IncrementalEnsembleSignal,
        IncrementalMLSuperTrend,
        CCXTStreamProcessor,
        get_available_streaming_indicators,
        create_indicator,
    )
    # Also expose as stream_ta module alias for convenience
    from . import streaming as stream_ta
except ImportError:
    # Streaming module not available
    stream_ta = None

# Exception types
from .exceptions import (
    HazeError,
    InvalidPeriodError,
    InsufficientDataError,
    ColumnNotFoundError,
    InvalidParameterError,
    ComputationError,
)

# Convenience re-exports for common indicators

# ==================== Public API Exports ====================

# 核心导出（手动维护，保持分类和文档）
_CORE_EXPORTS = [
    # Version metadata
    "__version__",

    # Rust data structures
    "OhlcvFrame",

    # Pandas accessors
    "TechnicalAnalysisAccessor",
    "SeriesTechnicalAnalysisAccessor",

    # Module aliases
    "np_ta",        # NumPy compatibility layer
    "stream_ta",    # Streaming indicators module

    # Streaming/incremental calculators
    "IncrementalSMA",
    "IncrementalEMA",
    "IncrementalRSI",
    "IncrementalATR",
    "IncrementalMACD",
    "IncrementalBollingerBands",
    "IncrementalStochastic",
    "IncrementalSuperTrend",
    "IncrementalAdaptiveRSI",
    "IncrementalEnsembleSignal",
    "IncrementalMLSuperTrend",
    "CCXTStreamProcessor",
    "get_available_streaming_indicators",
    "create_indicator",

    # AI-enhanced indicators (Python wrappers)
    "adaptive_rsi",
    "ensemble_signal",
    "ml_supertrend",

    # LT indicator (10 SFG combination)
    "lt_indicator",

    # Exception types
    "HazeError",
    "InvalidPeriodError",
    "InsufficientDataError",
    "ColumnNotFoundError",
    "InvalidParameterError",
    "ComputationError",
]

# 动态收集所有指标函数（py_* 和 clean API）
# 这些函数由 Rust 扩展提供，通过 _install_clean_api_aliases() 创建别名
_INDICATOR_EXPORTS = []

# 收集所有 py_* 函数（Rust 原生导出）
for _name in sorted(globals().keys()):
    if _name.startswith("py_") and callable(globals().get(_name)):
        _INDICATOR_EXPORTS.append(_name)

# 收集所有 clean API 别名（无 py_ 前缀）
for _clean_name in sorted(_PY_PREFIX_ALIASES.values()):
    if _clean_name in globals() and callable(globals()[_clean_name]):
        _INDICATOR_EXPORTS.append(_clean_name)

# 合并所有导出
__all__ = _CORE_EXPORTS + _INDICATOR_EXPORTS

# 清理临时变量，避免污染命名空间
del _name, _clean_name
