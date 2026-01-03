from dataclasses import dataclass
import numpy as np
from typing import Any

@dataclass
class SolverResult:
    """标准化的求解结果。"""
    variables: np.ndarray
    energy: float
    metadata: dict[str, Any] | None = None