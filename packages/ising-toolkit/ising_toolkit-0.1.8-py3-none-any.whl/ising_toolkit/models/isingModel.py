# src/my_solver/models/ising.py
import numpy as np
from dataclasses import dataclass, field
from .base import BaseModel
from typing import List

@dataclass(init=False)
class IsingModel(BaseModel):
    J: np.ndarray | List[List[float]]
    h: np.ndarray | List[float] | None = field(default=None)
    aux_spin_index: int | None = field(default=None)
    
    # 增加这两个属性来保存原始输入，以便正确计算能量
    J_raw: np.ndarray 
    h_raw: np.ndarray | None

    def __init__(self, J: np.ndarray | List[List[float]], h: np.ndarray | List[float] | None = None):
        """
        明确的构造函数，接收 J 和可选的 h。
        """
        # 保存原始输入，以便 api.py 能计算正确的原始能量
        self.J_raw = np.array(J) if isinstance(J, list) else J
        self.h_raw = np.array(h) if isinstance(h, list) else h
        
        # 步骤 1: 调用父类的通用预处理方法
        symmetrized_J, processed_h = self._preprocess_inputs(self.J_raw, self.h_raw, "J")
        n = symmetrized_J.shape[0]

        # 步骤 2: 检查是否需要引入辅助自旋
        if np.any(processed_h):
            print("检测到非零一次项 h，正在引入辅助自旋...")
            self.J = np.zeros((n + 1, n + 1), dtype=np.float64)
            self.J[:n, :n] = symmetrized_J
            
            couplings_to_aux = processed_h / 2.0
            self.J[:n, n] = couplings_to_aux
            self.J[n, :n] = couplings_to_aux

            self.h = np.zeros(n + 1, dtype=np.float64)
            self.aux_spin_index = n
        else:
            self.J = symmetrized_J
            self.h = processed_h
            self.aux_spin_index = None
        
        print("IsingModel 已成功建立并通过预处理。")

    @property
    def num_variables(self) -> int:
        return self.J.shape[0]

    def calculate_energy(self, spins: np.ndarray) -> float:
        return float(spins.T @ self.J @ spins + self.h.T @ spins)