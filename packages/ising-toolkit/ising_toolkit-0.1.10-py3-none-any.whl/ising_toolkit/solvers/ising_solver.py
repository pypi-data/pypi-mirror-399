import json
import numpy as np
import os
import io
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union


from ising import IsingClient, IsingClientError, AuthenticationError, GeneralTaskCreateRequest
from .base_solver import BaseSolver
from ..models import IsingModel, QUBOModel, BaseModel
from datetime import datetime
from typing import Dict, Any, Union



class IsingSolver(BaseSolver):
    """
    远程伊辛求解器，用于封装与光电伊辛机 API 的所有网络通信。
    用户只需传入 API Key 和矩阵数据。
    """
    
    def __init__(self, api_key: str):
        """
        初始化远程求解器客户端。
        
        Args:
            api_key (str): 您的 API 密钥。
        """
        client_args: Dict[str, Any] = {'api_key': api_key}

            
        try:
            self._client = IsingClient(**client_args)
        except Exception as e:
            raise IsingClientError(f"初始化 IsingClient 失败: {str(e)}")


    def _prepare_and_upload_file(self, 
                                matrix_data: Union[List, np.ndarray], 
                                filename: str) -> str:
        """
        内部方法：将矩阵数据转换为 CSV 格式的字节流，上传文件并返回 fileUrl。
        服务器只接收 CSV 文件。
        
        Args:
            matrix_data: J 或 H 矩阵数据 (list 或 np.ndarray)。
            filename: 文件名的基础部分（例如 'J_matrix'）。
            
        Returns:
            str: 上传成功后服务器返回的文件 URL。
            
        Raises:
            IsingClientError: 序列化、文件操作或上传失败。
        """

        
        if matrix_data is None:
            return "" 

        # 1. 确保数据为 NumPy 数组
        try:
            # 强制转换为浮点型 NumPy 数组
            data_arr = np.array(matrix_data, dtype=np.float64)
        except Exception as e:
            raise IsingClientError(f"矩阵 '{filename}' 无法转换为数值数组，请检查数据内容: {str(e)}")

        # 2. 转换为 CSV 格式的字节流 (在内存中操作)
        try:
            # 使用 StringIO 模拟文件对象，将 NumPy 数组写入 CSV 格式
            csv_buffer = io.StringIO()
            
            # 使用 np.savetxt 写入 CSV。
            # delimiter=',' 确保是 CSV 格式，fmt='%f' 使用浮点数格式。
            # 如果是一维向量，它会按一列形式写入，这对于 H 向量也是可以的。
            np.savetxt(csv_buffer, data_arr, delimiter=',', fmt='%.18e')
            
            # 将 StringIO 的内容转换为 bytes
            csv_string = csv_buffer.getvalue()
            file_bytes = csv_string.encode('utf-8')
            original_filename = f"{filename}.csv"
            
        except Exception as e:
            raise IsingClientError(f"矩阵 '{filename}' 转换为 CSV 格式失败: {str(e)}")

        # 3. 调用客户端上传文件
        try:
            upload_result = self._client.upload_file(file_bytes, original_filename)
            # 假设上传成功响应结构是 {'code': 0, 'data': {'fileUrl': '...'}}
            file_url = upload_result['data']['fileUrl']
            return file_url
        except Exception as e:
            # 捕获并包装任何上传过程中发生的错误
            raise IsingClientError(f"文件 '{original_filename}' 上传失败: {str(e)}")


    def solve(self, 
              model: BaseModel, 
              name: str = "Remote SDK Task", 
            #   shots: Optional[int] = 5, 
              post_process: Optional[bool] = False,
             ) -> Dict[str, Any]:
        """
        提交一个通用的 Ising 任务到远程 API。
        自动处理：数据校验 -> 矩阵转 CSV -> 上传文件 -> 创建任务。
        
        Args:
            model: 包含 J 和 H 矩阵数据的模型对象。
            name (str): 任务名称。
            computer_type_id (int, optional): 计算机类型 ID (对应 API 的 computerTypeId)。
            shots (int, optional): 计算次数，默认 5。
            post_process (int, optional): 后处理类型。
        
        Returns:
            Dict[str, Any]: 返回一个简洁字典，包含 'success' 状态和 'taskId'。
            
        Raises:
            IsingClientError: 任何网络、认证、文件或 API 错误。
        """
        # if shots is None or shots <= 0:
        #     raise IsingClientError(f"shots 必须是正整数，但 got {shots}")
        if post_process is None:
            post_process = False
        if post_process not in [True, False]:
            raise IsingClientError(f"post_process 必须是布尔值，但 got {post_process}")

        
         # --- 1. 数据校验已在 IsingModel 内完成 ---
        
         # 使用 try-except 捕获所有可能的错误
        vartype = "binary"   if isinstance(model, QUBOModel) else "spin"
        try:

            # --- 2. J 矩阵处理和上传 (自动转换为 CSV 格式) ---
            J_file_url = self._prepare_and_upload_file(
                matrix_data=model.J if hasattr(model, 'J') else model.Q,
                filename="J_matrix"
            )
            
            # --- 3. H 向量处理和上传 (自动转换为 CSV 格式) ---
            H_file_url = self._prepare_and_upload_file(
                matrix_data=model.h, 
                filename="H_vector"
            )

            # --- 4. 创建任务请求 ---

      
            request = GeneralTaskCreateRequest(
                name=name,
                computerTypeId=1,
                inputJFile=J_file_url,
                inputHFile=H_file_url,
                questionType=1 if vartype == "binary" else 2,
                # caculateCount=shots,
                postProcess=1 if post_process else 0
            )
      
            # --- 5. 提交任务并处理响应 ---
            full_response = self._client.create_general_task(request)

            
            # --- 6. 提取关键信息并返回 ---
            if full_response.get('message') == 'success' and full_response.get('data'):
                task_id = full_response['data'].get('id')
                print(f"任务提交成功，任务 ID: {task_id},正在排队计算中...")
                # 只返回用户关心的信息
                return {
                    "success": True,
                    "taskId": task_id,
                    "message": "Task submitted successfully."
                }
            else:
                # 任务提交失败（例如 API 返回错误信息）
                error_msg = full_response.get('message', '未知 API 错误')
                raise IsingClientError(f"任务提交失败: {error_msg}")

        except (IsingClientError, AuthenticationError) as e:
            # 捕获并重新抛出任何客户端或认证错误
            raise e
        except Exception as e:
            # 捕获其他未预期的错误
            raise IsingClientError(f"远程任务提交失败: {str(e)}")
            
            
    # --- 任务管理和查询方法 (保持不变，已封装网络请求) ---

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务详情。
        """
        try:
            return self._client.get_task(task_id)
        except (IsingClientError, AuthenticationError) as e:
            raise e
        except Exception as e:
            raise IsingClientError(f"获取任务详情失败: {str(e)}")

   

    def get_task_list(self, page_no: int = 1, page_size: int = 10, formatted: bool = False) -> Union[Dict[str, Any], str]:
        """
        查询任务列表。

        Args:
            page_no (int): 页码，默认为 1。
            page_size (int): 每页数量，默认为 10。
            formatted (bool): 是否返回格式化后的可读字符串。默认 False 返回原始字典。

        Returns:
            Union[Dict[str, Any], str]: 
                - 若 formatted=False：返回原始 API 响应字典；
                - 若 formatted=True：返回美化后的 Markdown 格式字符串。
        """
        try:
            raw_response = self._client.get_task_list(page_no, page_size)
        except (IsingClientError, AuthenticationError) as e:
            raise e
        except Exception as e:
            raise IsingClientError(f"获取任务列表失败: {str(e)}")

        if not formatted:
            return raw_response

        # 否则进行格式化
        status_map = {0: "⏳ 运行中", 2: "✅ 已完成"}
        source_map = {1: "用户创建", 2: "模版任务"}

        lines = []
        total = raw_response["total"]
        page_no_val = raw_response["pageNo"]
        total_pages = raw_response["totalPages"]
        page_size_val = raw_response["pageSize"]

        lines.append(f"### 📋 任务历史记录（共 {total} 条，当前第 {page_no_val} / {total_pages} 页，每页 {page_size_val} 条）\n")
        lines.append("| ID | 任务名称 | 状态 | 创建时间（UTC） | 完成时间（UTC） | 耗时（秒） | 来源 |")
        lines.append("|----|--------|------|------------------|------------------|-----------|------|")

        for task in raw_response["records"]:
            tid = task["id"]
            name = task["name"]
            status = status_map.get(task["status"], f"未知({task['status']})")
            # 处理 ISO 8601 时间（兼容带 Z 或 ± 时区）
            create_time = (
                datetime.fromisoformat(task["createTime"].replace("Z", "+00:00"))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            if task["finishTime"]:
                finish_time = (
                    datetime.fromisoformat(task["finishTime"].replace("Z", "+00:00"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            else:
                finish_time = "—"
            duration = task["durations"] if task["durations"] is not None else "—"
            source = source_map.get(task["source"], f"未知({task['source']})")

            lines.append(f"| {tid} | {name} | {status} | {create_time} | {finish_time} | {duration} | {source} |")

        lines.append("\n> **状态说明**  \n> - `⏳ 运行中`：任务尚未完成（status = 0）  \n> - `✅ 已完成`：任务已成功结束（status = 2）")
        lines.append("\n> **来源说明**  \n> - `source = 1` → 用户创建  \n> - `source = 2` → 社区模板")

        return "\n".join(lines)
            
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取已完成任务的结果（高级封装）。
        """
        task_info = self._client.get_task(task_id)
        
        # 假设 API 响应中的 'status' 字段用于表示任务状态，'result' 包含结果数据
        if task_info.get('status') == 0:
            print(f"任务 {task_id} 正在排队计算中，请稍后重试")
        if task_info.get('status') == 2:
            # 理想情况下，这里应该下载和解析结果文件
            raw_result = task_info.get('result')
            result = {}
            result["variables"] = np.array(raw_result["spin_config"]).astype(int)
            result["energy"] = np.array(raw_result["energy"]).item()

            return result
        
        if task_info.get('status') == 3:
            raise IsingClientError(f"任务 {task_id} 执行失败。错误信息: {task_info.get('error_message')}")
            
        return None # 任务仍在运行或处于其他状态