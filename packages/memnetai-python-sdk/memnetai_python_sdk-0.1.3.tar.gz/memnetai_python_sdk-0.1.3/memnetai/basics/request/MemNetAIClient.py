import json
from typing import Dict, Optional, Any, List

import requests

from memnetai.basics.request.message.message import Message


class MemNetAIClient:
    """
    MemNet AI API 客户端
    统一处理所有API请求，提供一致的接口调用方式
    """

    def __init__(self, api_key: str, base_url: str = "https://api.memnet.ai"):
        """
        初始化客户端
        :param base_url: API基础地址
        :param api_key: API密钥
        """
        self.base_url = base_url.rstrip("/")  # 确保URL不以斜杠结尾
        self.api_key = api_key

    def _send_request(self, endpoint: str, method: str = "POST", data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        内部方法：发送API请求
        :param endpoint: API端点（如/v1/memories）
        :param method: 请求方法（默认POST）
        :param data: 请求数据
        :return: 响应结果字典，异常时返回None
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}"
        }

        request_kwargs = {}
        response = None

        try:
            # 构造请求参数
            request_kwargs = {
                "url": url,
                "headers": headers,
                "timeout": (5, 200),  # 连接超时5秒，读取超时200秒
                "verify": True
            }

            # 根据请求方法添加数据
            if method == "POST" or method == "PUT" or method == "PATCH":
                request_kwargs["json"] = data
            elif method == "GET" or method == "DELETE":
                request_kwargs["params"] = data

            # 发送请求
            response = requests.request(method, **request_kwargs)
            response.raise_for_status()

            # 解析响应
            result = {
                "status_code": response.status_code,
                "response_json": response.json(),
                "response_headers": dict(response.headers)
            }
            print(f"{method} 请求成功！状态码：{result['status_code']}")
            return result

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 错误：{e}，状态码：{response.status_code if 'response' in locals() else '未知'}")
            if 'response' in locals() and response:
                print(f"响应内容：{response.text}")
                print(f"响应头：{dict(response.headers)}")
        except requests.exceptions.ConnectionError:
            print("网络错误：无法连接到目标服务器")
        except requests.exceptions.Timeout:
            print(f"请求超时：超过 {request_kwargs['timeout']} 秒未响应" if 'request_kwargs' in locals() else "请求超时")
        except json.JSONDecodeError:
            print("解析错误：接口返回非合法 JSON 数据")
            if 'response' in locals() and response:
                print(f"原始响应内容：{response.text}")
        except Exception as e:
            print(f"未知异常：{e}")
            import traceback
            traceback.print_exc()
        return None

    def memories(self, memory_agent_name: Optional[str], namespace: str, messages: List[Message],
                     language: str = "zh-CN", is_third_person: int = 0, metadata: str = "",
                     async_mode: int = 0) -> Optional[Dict[str, Any]]:
        """
        发送消息到记忆体
        :param memory_agent_name: 记忆体名称
        :param messages: 消息列表
        :param language: 记忆摘要预期语言（默认中文）
        :param is_third_person: 是否使用第三人称（默认0-不使用）
        :param metadata: 元数据
        :param async_mode: 是否启用异步记忆（默认0-不启用）
        :param namespace: 命名空间，默认值为空字符串
        :return: 响应结果
        """
        messages_dict = [msg.to_dict() for msg in messages]
        data = {
            "memoryAgentName": memory_agent_name,
            "messages": messages_dict,
            "namespace": namespace,
            "language": language,
            "isThirdPerson": is_third_person,
            "metadata": metadata,
            "asyncMode": async_mode
        }
        return self._send_request("/v1/memories", "POST", data)

    def recall(self, memory_agent_name: Optional[str], namespace: str, query: str, character: str = "用户",
                      recall_deep: int = 1, is_include_linked_new_memories_from_invalid: int = 0,
                      is_using_associative_thinking: int = 1, is_using_common_sense_database: int = 1,
                      is_using_global_common_sense_database: int = 1, is_using_memory_agent_common_sense_database: int = 0,
                      common_sense_database_id_list: Optional[List[str]] = None,
                      is_returning_detailed_memory_info: int = 0) -> Optional[Dict[str, Any]]:
        """
        回忆记忆
        :param query: 查询内容
        :param memory_agent_name: 记忆体名称（可选）
        :param namespace: 命名空间，默认值为空字符串
        :param character: 角色（默认"用户"）
        :param recall_deep: 回忆深度（默认1）
        :param is_include_linked_new_memories_from_invalid: 是否包含无效记忆关联的新记忆（默认0）
        :param is_using_associative_thinking: 是否使用关联思考（默认1）
        :param is_using_common_sense_database: 是否使用常识数据库（默认1）
        :param is_using_global_common_sense_database: 是否使用全局常识数据库（默认1）
        :param is_using_memory_agent_common_sense_database: 是否使用记忆体常识数据库（默认0）
        :param common_sense_database_id_list: 常识数据库ID列表（可选）
        :param is_returning_detailed_memory_info: 是否返回详细记忆信息（默认0）
        :return: 响应结果
        """
        data = {
            "memoryAgentName": memory_agent_name,
            "query": query,
            "namespace": namespace,
            "character": character,
            "recallDeep": recall_deep,
            "isIncludeLinkedNewMemoriesFromInvalid": is_include_linked_new_memories_from_invalid,
            "isUsingAssociativeThinking": is_using_associative_thinking,
            "isUsingCommonSenseDatabase": is_using_common_sense_database,
            "isUsingGlobalCommonSenseDatabase": is_using_global_common_sense_database,
            "isUsingMemoryAgentCommonSenseDatabase": is_using_memory_agent_common_sense_database,
            "commonSenseDatabaseIdList": common_sense_database_id_list,
            "isReturningDetailedMemoryInfo": is_returning_detailed_memory_info,
        }
        return self._send_request("/v1/recall", "POST", data)  # 假设回忆API端点是/memories/recall

    def think(self, memory_agent_name: Optional[str], namespace: str, subject: str = "",
              async_mode: int = 1, is_auto: int = 0) -> Optional[Dict[str, Any]]:
        """
        思考
        :param memory_agent_name: 记忆体名称
        :param namespace: 命名空间，默认值为空字符串
        :param subject: 思考主题,不进行自定义将会从历史记忆中随机抽取主题
        :param async_mode: 异步模式（默认1）
        :param is_auto: 是否自动思考（默认0）
        :return: 响应结果
        """
        data = {
            "memoryAgentName": memory_agent_name,
            "namespace": namespace,
            "subject": subject,
            "asyncMode": async_mode,
            "isAuto": is_auto,
        }
        return self._send_request("/v1/think", "POST", data)  # 假设思考API端点是/think

    def dream(self, memory_agent_name: Optional[str],namespace: str, subject: str = "",
              async_mode: int = 1, is_auto: int = 0) -> Optional[Dict[str, Any]]:
        """
        做梦
        :param memory_agent_name: 记忆体名称
        :param namespace: 命名空间，默认值为空字符串
        :param subject: 做梦主题,不进行自定义将会从历史记忆中随机抽取主题
        :param async_mode: 异步模式（默认1）
        :param is_auto: 是否自动做梦（默认0）
        :return: 响应结果
        """
        data = {
            "memoryAgentName": memory_agent_name,
            "namespace": namespace,
            "subject": subject,
            "asyncMode": async_mode,
            "isAuto": is_auto,
        }
        return self._send_request("/v1/dream", "POST", data)  # 假设做梦API端点是/dream

    def common_sense(self, common_sense_database_id: str, common_sense_text: str,
                    async_mode: int = 1) -> Optional[Dict[str, Any]]:
        """
        常识
        :param common_sense_database_id: 常识记忆库id（可选）
        :param common_sense_text: 常识库文本内容（可选）
        :param async_mode: 异步模式（默认1）
        :return: 响应结果
        """
        data = {
            "commonSenseDatabaseId": common_sense_database_id,
            "commonSenseText": common_sense_text,
            "asyncMode": async_mode,
        }
        return self._send_request("/v1/common-sense", "POST", data)  # 假设常识API端点是/commonsense

    def memories_detail(self, task_id: str = ""):
        """
        获取记忆详情
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/memories/task/detail", "GET", data)
        pass

    def memories_progress(self, task_id: str = ""):
        """
        获取记忆进度
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/memories/task/progress", "GET", data)
        pass

    def memories_all(self):
        """
        获取所有记忆
        :return: 响应结果
        """
        return self._send_request("/memories/task/all", "GET")
        pass

    def memories_delete(self, task_id: str = ""):
        """
        删除所有记忆
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/memories/task/delete", "DELETE", data)
        pass

    def think_detail(self, task_id: str = ""):
        """
        获取思考详情
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/think/task/detail", "GET", data)
        pass

    def think_all(self):
        """
        获取所有思考
        :return: 响应结果
        """
        return self._send_request("/think/task/all", "GET")
        pass

    def think_delete(self, task_id: str = ""):
        """
        删除所有思考
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/think/task/delete", "DELETE", data)
        pass

    def dream_detail(self, task_id: str = ""):
        """
        获取做梦详情
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/dream/task/detail", "GET", data)
        pass

    def dream_delete(self, task_id: str = ""):
        """
        删除所有做梦
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/dream/task/delete", "DELETE", data)
        pass

    def dream_all(self):
        """
        获取所有做梦
        :return: 响应结果
        """
        return self._send_request("/dream/task/all", "GET")
        pass

    def common_sense_all(self):
        """
        获取所有常识
        :return: 响应结果
        """
        return self._send_request("/common-sense/task/all", "GET")
        pass

    def common_sense_delete(self, task_id: str = ""):
        """
        删除所有常识
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/common-sense/task/delete", "DELETE", data)
        pass

    def common_sense_detail(self, task_id: str = ""):
        """
        获取常识详情
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/common-sense/task/detail", "GET", data)
        pass

    def common_sense_progress(self, task_id: str = ""):
        """
        获取常识进度
        :param task_id: 任务ID，如"your_task_id_here"
        :return: 响应结果
        """
        data = {
            "taskId": task_id,
        }
        return self._send_request("/common-sense/task/progress", "GET", data)
        pass
