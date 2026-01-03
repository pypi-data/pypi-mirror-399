import numpy as np
# 保持原始的相对导入不变
from .base_solver import BaseSolver
from ..models.isingModel import IsingModel

class SimulatedAnnealingSolver(BaseSolver):
    """
    一个使用多副本并行计算的模拟退火（Simulated Annealing）求解器。
    """
    def __init__(
        self,
        agents: int = 128,
        initial_temp: float = 10.0,
        final_temp: float = 0.1,
        cooling_rate: float = 0.99,
        steps_per_temp: int = 100,
    ):
        """
        Args:
            agents (int): 并行运行的搜索副本数量。
            initial_temp (float): 初始温度。
            final_temp (float): 最终温度，当温度低于此值时停止。
            cooling_rate (float): 降温速率 (几何降温)。
            steps_per_temp (int): 在每个温度下迭代的步数。
            device (str, optional): [已忽略] 此 NumPy 版本总是在 CPU 上运行。
        """
        self.agents = agents
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
        self.steps_per_temp = steps_per_temp
        


    def solve(self, ising_model: IsingModel, initial_state: np.ndarray | None = None) -> np.ndarray:
        # 步骤 1: 准备资料
        # J 已经是 numpy 数组，确保一下类型
        J = ising_model.J
        n_spins = ising_model.num_variables
        aux_idx = ising_model.aux_spin_index

        # 步骤 2: 初始化
        # 初始化所有副本的自旋状态 (N, K)
        if initial_state is not None:
            if initial_state.shape != (n_spins,):
                raise ValueError(f"initial_state 维度 {initial_state.shape} 与模型维度 ({n_spins},) 不符。")

            num_seeded = self.agents // 2
            num_random = self.agents - num_seeded

            base_spins = initial_state.astype(np.float32)
            # 使用 np.tile 复制 (N, 1) -> (N, K_seeded)
            seeded_spins = np.tile(base_spins[:, np.newaxis], (1, num_seeded))
            
            # 使用 np.random.randint 生成随机自旋
            random_spins = np.random.randint(0, 2, size=(n_spins, num_random)) * 2 - 1

            spins = np.concatenate([seeded_spins, random_spins], axis=1)
        else:
            spins = np.random.randint(0, 2, size=(n_spins, self.agents)) * 2 - 1
        
        if aux_idx is not None:
            spins[aux_idx, :] = 1.0
            
        # 计算当前能量 (使用 np.einsum)
        current_energies = np.einsum('ik,ij,jk->k', spins, J, spins)
        
        # 初始化全局最优解
        best_energy_so_far = np.min(current_energies)
        best_spins_so_far = spins[:, np.argmin(current_energies)].copy()

        # 步骤 3: 核心循环 - 模拟退火过程
        T = self.initial_temp
        while T > self.final_temp:
            # 在当前温度下进行多次迭代
            for _ in range(self.steps_per_temp):
                # 为每个副本随机选择一个自旋进行翻转
                flip_indices = np.random.randint(0, n_spins, size=(self.agents,))
                
                # 计算翻转带来的能量变化 delta_E
                # J_rows (K, N), spins (N, K) -> einsum -> (K,)
                J_rows = J[flip_indices, :]
                interaction_energies = np.einsum('ki,ik->k', J_rows, spins)
                
                # 获取要翻转的自旋的当前值
                # [spins[flip_indices[0], 0], spins[flip_indices[1], 1], ...]
                spins_to_flip = spins[flip_indices, np.arange(self.agents)]
                J_diag = J[flip_indices, flip_indices]
                delta_E = 4.0 * J_diag - 4.0 * spins_to_flip * interaction_energies
                
                # 梅特罗波利斯接受准则
                acceptance_prob = np.exp(-delta_E / T)
                # 使用 np.random.rand 生成 [0, 1) 的随机数
                should_accept = (delta_E < 0) | (np.random.rand(self.agents) < acceptance_prob)
                
                # 更新被接受的副本的自旋状态
                if np.any(should_accept):
                    # 获取需要更新的副本的索引 (NumPy advanced indexing)
                    accepted_indices = np.where(should_accept)[0]
                    
                    # 获取这些副本中要翻转的自旋的索引
                    spins_to_flip_indices = flip_indices[accepted_indices]
                    
                    # 执行翻转 (NumPy a[idx_arr1, idx_arr2] 就地修改)
                    spins[spins_to_flip_indices, accepted_indices] *= -1
                    
                    # 更新这些副本的能量
                    current_energies[accepted_indices] += delta_E[accepted_indices]
                
                    # 检查是否找到了新的全局最优解
                    min_current_energy = np.min(current_energies)
                    if min_current_energy < best_energy_so_far:
                        best_energy_so_far = min_current_energy
                        best_spins_so_far = spins[:, np.argmin(current_energies)].copy()

            # 降温
            T *= self.cooling_rate
        
        # 已经是 numpy array，直接返回
        result = {}
        result["variables"] = best_spins_so_far.astype(int)
        result["energy"] = best_energy_so_far.item()

        return result
