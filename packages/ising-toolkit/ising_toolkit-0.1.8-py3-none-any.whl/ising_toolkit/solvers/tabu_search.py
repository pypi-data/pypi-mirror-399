import numpy as np
import torch
from .base_solver import BaseSolver
from ..models.isingModel import IsingModel

class TabuSolver(BaseSolver):
    """
    一个精简高效的、使用多副本并行计算的禁忌搜索求解器。

    该版本聚焦于核心性能，保留了禁忌搜索最关键的组件，同时移除了
    复杂的辅助策略，以实现更快的求解速度。

    保留的核心特性:
    - 多副本并行 (Agents): 通过并行搜索提供基础的多样性。
    - 禁忌列表 (Tabu List): 防止搜索过程陷入短期循环。
    - 渴望准则 (Aspiration Criterion): 允许在能找到历史最优解时“破禁”。
    """
    def __init__(
        self,
        max_iter: int = 10000,
        agents: int = 128,
        tabu_tenure: int = 20, # 禁忌步长，一个移动被禁忌的迭代次数
        device: str | None = None
    ):
        """
        Args:
            max_iter (int): 最大迭代次数。
            agents (int): 并行运行的搜索副本数量。
            tabu_tenure (int): 固定的禁忌步长。
            device (str, optional): 计算设备 ('cuda' 或 'cpu')。
        """
        self.max_iter = max_iter
        self.agents = agents
        self.tabu_tenure = tabu_tenure
        
        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Lean TabuSolver initialized on device: '{self.device}'")

    def solve(self, ising_model: IsingModel, initial_state: np.ndarray | None = None) -> np.ndarray:
        # 步骤 1: 准备资料
        J = torch.from_numpy(ising_model.J).to(self.device, dtype=torch.float32)
        n_spins = ising_model.num_variables
        aux_idx = ising_model.aux_spin_index

        # 步骤 2: 初始化
        # 混合初始化逻辑
        if initial_state is not None:
            if initial_state.shape != (n_spins,):
                raise ValueError(f"initial_state 维度 {initial_state.shape} 与模型维度 ({n_spins},) 不符。")
            
            num_seeded = self.agents // 2
            num_random = self.agents - num_seeded
            base_spins = torch.from_numpy(initial_state).to(self.device, dtype=torch.float32)
            seeded_spins = base_spins.unsqueeze(1).expand(-1, num_seeded)
            random_spins = torch.randint(0, 2, (n_spins, num_random), device=self.device, dtype=torch.float32) * 2 - 1
            spins = torch.cat([seeded_spins, random_spins], dim=1)
        else:
            spins = torch.randint(0, 2, (n_spins, self.agents), device=self.device, dtype=torch.float32) * 2 - 1
        
        if aux_idx is not None:
            spins[aux_idx, :] = 1.0
            
        # 初始化禁忌列表 (N, K)
        tabu_list = torch.zeros_like(spins, dtype=torch.int32)
        
        # 计算初始能量并保存为当前最优解
        energies = torch.einsum('ik,ij,jk->k', spins, J, spins)
        best_energies_so_far = energies.clone()
        best_spins_so_far = spins.clone()

        # 步骤 3: 核心迭代 (已精简)
        for t in range(1, self.max_iter + 1):
            # 计算翻转每个自旋带来的能量变化 delta_E
            # 这是主要的计算开销，无法避免
            delta_E = -2 * spins * torch.matmul(J, spins)

            # 应用渴望准则：如果一个移动能得到历史最优解，就忽略其禁忌状态
            aspiration_mask = (energies + delta_E) < best_energies_so_far
            
            # 应用禁忌规则：被禁忌且不满足渴望准则的移动，其delta_E设为无穷大
            tabu_mask = (tabu_list > t) & ~aspiration_mask
            delta_E[tabu_mask] = float('inf')
            
            if aux_idx is not None: # 确保辅助自旋不被翻转
                delta_E[aux_idx, :] = float('inf')

            # 为每个副本找到能量下降最多的非禁忌移动
            best_move_indices = torch.argmin(delta_E, dim=0)
            best_delta_E = torch.gather(delta_E, 0, best_move_indices.unsqueeze(0)).squeeze(0)

            # 执行移动：翻转选中的自旋
            updates = -2 * torch.gather(spins, 0, best_move_indices.unsqueeze(0)).squeeze(0)
            spins.scatter_add_(0, best_move_indices.unsqueeze(0), updates.unsqueeze(0))

            # 更新禁忌列表：将刚刚执行的移动加入禁忌
            new_tenure = t + self.tabu_tenure
            tabu_list.scatter_(0, best_move_indices.unsqueeze(0), new_tenure)

            # 更新当前能量
            energies += best_delta_E
            
            # 检查是否找到了新的最优解（对每个副本独立进行）
            new_best_mask = energies < best_energies_so_far
            if torch.any(new_best_mask):
                best_energies_so_far[new_best_mask] = energies[new_best_mask]
                best_spins_so_far[:, new_best_mask] = spins[:, new_best_mask]
        
        # 步骤 4: 从所有副本找到的最好结果中，选出全局最优解
        overall_best_idx = torch.argmin(best_energies_so_far)
        overall_best_spins = best_spins_so_far[:, overall_best_idx]
        result = {}
        result["spins"] = overall_best_spins.cpu().numpy().astype(int)
        result["energy"] = best_energies_so_far[overall_best_idx].item()
        
        return result