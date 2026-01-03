# src/ising_optimizer/utils/converters.py
import numpy as np
from ..models.quboModel import QUBOModel
from ..models.isingModel import IsingModel

def to_ising(model: QUBOModel) -> IsingModel:
    """将一个【已标准化的】QUBOModel 物件转换为 IsingModel。"""
    Q_prime = model.Q
    
    J = Q_prime / 4.0
    
    # 【修正】h 的计算公式，加上负号
    h = np.sum(Q_prime, axis=1) / 2.0
    
    np.fill_diagonal(J, 0)
    
    return IsingModel(J=J, h=h)