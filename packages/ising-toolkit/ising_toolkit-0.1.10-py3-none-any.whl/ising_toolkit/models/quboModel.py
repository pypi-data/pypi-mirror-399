# src/my_solver/models/qubo.py
import numpy as np
from dataclasses import dataclass
from .base import BaseModel

# 我们使用 dataclass 来自动生成 __repr__ 等方法，但通过 init=False 告诉它我们自己定义 __init__。
@dataclass(init=False)
class QUBOModel(BaseModel):
    Q: np.ndarray

    def __init__(self, Q: np.ndarray, h: np.ndarray | None = None):
        """
        明确的构造函数，接收 Q 和可选的 h。
        """
        # 步骤 1: 调用父类的通用预处理方法
        symmetrized_Q, processed_h = self._preprocess_inputs(Q, h, "Q")
        
        # 步骤 2: 执行 QUBO 特定的逻辑 -> 合并一次项
        final_Q = symmetrized_Q
        np.fill_diagonal(final_Q, np.diag(final_Q) + processed_h)
        
        # 步骤 3: 设置最终处理好的属性
        self.Q = final_Q
        self.h = processed_h
        print("QUBOModel 已成功建立并通过预处理。")

    @property
    def num_variables(self) -> int:
        return self.Q.shape[0]

    def calculate_energy(self, variables: np.ndarray) -> float:
        return float(variables.T @ self.Q @ variables)