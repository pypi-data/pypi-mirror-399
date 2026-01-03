from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple

class BaseModel(ABC):
    """
    所有问题模型的抽象基础类别。
    新增了通用的输入预处理方法。
    """
    def _preprocess_inputs(
        self,
        quadratic_term: np.ndarray,
        linear_term: np.ndarray | None = None,
        variable_name: str = "Q"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        对二次型问题（Quadratic Model）的输入进行通用的验证和标准化。

        Args:
            quadratic_term (np.ndarray): 二次项矩阵 (Q 或 J)。
            linear_term (np.ndarray, optional): 一次项向量 (h)。
            variable_name (str): 用于错误讯息的变数名称 ('Q' 或 'J')。

        Returns:
            一个元组，包含处理过的 (二次项矩阵, 一次项向量)。
        """
        # 1. 类型和维度验证
        if not isinstance(quadratic_term, np.ndarray) or quadratic_term.ndim != 2 or quadratic_term.shape[0] != quadratic_term.shape[1]:
            raise ValueError(f"{variable_name} 必须是一个二维方阵。")

        n = quadratic_term.shape[0]
        processed_q_term = quadratic_term.astype(np.float32, copy=True)

        if linear_term is not None:
            if not isinstance(linear_term, np.ndarray) or linear_term.ndim != 1 or linear_term.shape[0] != n:
                raise ValueError(f"h 必须是一个长度为 {n} 的一维向量。")
            processed_l_term = linear_term.astype(np.float32, copy=True)
        else:
            processed_l_term = np.zeros(n, dtype=np.float32)
        
        # 2. 对称化二次项矩阵
        symmetrized_q_term = (processed_q_term + processed_q_term.T) / 2.0
        
        return symmetrized_q_term, processed_l_term

    @property
    @abstractmethod
    def num_variables(self) -> int:
        pass