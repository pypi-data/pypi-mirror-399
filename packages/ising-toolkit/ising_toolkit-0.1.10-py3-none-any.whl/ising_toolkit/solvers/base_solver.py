from abc import ABC, abstractmethod
import numpy as np
# 注意：我们在这里汇入 IsingModel 以强化型别提示
from ..models.isingModel import IsingModel

class BaseSolver(ABC):
    """求解器基础类别，定义了低阶计算介面。"""
    @abstractmethod
    def solve(self, ising_model: IsingModel) -> np.ndarray:
        """
        低阶计算方法。只接收一个标准化的 IsingModel。
        
        Args:
            ising_model (IsingModel): 一个经过完全预处理的 Ising 模型。
            initial_spins (np.ndarray, optional): 初始自旋状态，形状为 (N, K)，其中 N 是自旋数量，K 是副本数量。
        
        Returns:
            np.ndarray: 包含所有自旋（包括辅助自旋）的原始计算结果。
        """
        pass