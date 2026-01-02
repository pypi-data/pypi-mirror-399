import copy
from typing import List, Dict, Any, Optional
from loguru import logger
from memnetai.basics.request.MemNetAIClient import MemNetAIClient
from memnetai.basics.request.message.message import Message
from memnetai.upgrade.config.config import Config

class MemoryMessageQueue:
    """
    记忆消息队列类，实现自动记忆和回忆功能

    参数:
        - config: Config类型，包含窗口大小和API配置
    """

    def __init__(self, config: Config):
        self.config = config
        self.memory_agent_name = config.memory_agent_name
        self.window_size = config.window_size

        # 初始化队列，仅包含对话消息（不含回忆内容）
        self.queue: List[Dict[str, str]] = []

        # 独立的回忆内容，不计入队列大小
        self.current_recall: Optional[Dict[str, str]] = None

        # 初始化基础包客户端
        self.base_client = MemNetAIClient(
            base_url=config.get('memnetai_base_url'),
            api_key=config.get('memnetai_api_key')
        )

        # 消息计数，用于判断是否需要调用记忆接口
        self.message_count = 0

        # 每16条消息请求一次记忆接口
        self.memory_threshold = 16

    def add_message(self, message: Dict[str, str]) -> None:
        """
        向队列中添加消息，并根据消息数量触发记忆和回忆

        参数:
            - message: 消息字典，包含role和content字段
        """
        # 添加消息到队列
        self.queue.append(message)
        self.message_count += 1

        # 保持队列大小不超过窗口大小
        if len(self.queue) > self.window_size:
            self.queue.pop(0)  # 移除最旧的消息

        # 每16条消息触发一次记忆保存
        if self.message_count % self.memory_threshold == 0:
            self._save_memory()

        # 如果是用户消息，触发一次回忆
        if message.get("role") == "user":
            self._recall_memory(message.get("content", ""))

    def _save_memory(self) -> None:
        """
        保存当前对话到记忆体
        """
        try:
            if not self.queue:
                return

            # 转换为Message对象列表
            message_objects = [
                Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    character=msg.get("character", "") or "用户"
                ) for msg in self.queue
            ]

            # 调用记忆接口保存消息
            logger.info(f"调用记忆接口保存{len(message_objects)}条消息")
            memory_result = self.base_client.memories(
                memory_agent_name=self.memory_agent_name,
                messages=message_objects,
                language="zh-CN",
                is_third_person=0,
                metadata="",
                async_mode=0,
                namespace=self.config.get('namespace')
            )

            if not memory_result or memory_result.get("status_code") != 200:
                logger.error("记忆接口调用失败")
                return

            logger.info("记忆保存成功")

        except Exception as e:
            logger.error(f"保存记忆时发生错误: {e}")

    def _recall_memory(self, query: str) -> None:
        """
        根据查询内容回忆相关内容，并更新当前回忆

        参数:
            - query: 用于回忆的查询内容
        """
        try:
            if not query:
                return

            # 调用回忆接口获取相关记忆
            logger.info(f"调用回忆接口，查询内容：{query}")
            recall_result = self.base_client.recall(
                memory_agent_name=self.memory_agent_name,
                query=query,
                character="用户",
                recall_deep=1,
                is_using_associative_thinking=1,
                is_using_common_sense_database=1,
                namespace=self.config.get('namespace')
            )

            if not recall_result or recall_result.get("status_code") != 200:
                logger.error("回忆接口调用失败")
                return

            # 处理回忆结果，更新当前回忆内容
            self._update_recall_content(recall_result)

        except Exception as e:
            logger.error(f"回忆记忆时发生错误: {e}")

    def _update_recall_content(self, recall_result: Dict[str, Any]) -> None:
        """
        更新当前的回忆内容

        参数:
            - recall_result: 回忆接口返回的结果
        """
        try:
            # 验证返回结果结构
            if not recall_result or "data" not in recall_result.get("response_json", {}):
                logger.warning(f"回忆结果为空或格式不正确，返回结果：{recall_result}")
                self.current_recall = None
                return

            data = recall_result["response_json"]["data"]

            # 获取各个记忆列表
            memory_prompt = data.get("memoryPrompt", "")

            # 构建回忆消息
            self.current_recall = {
                "role": "system",
                "content": f"{memory_prompt}",
                "character": "系统"
            }

            logger.info(f"回忆内容已更新")

        except Exception as e:
            logger.error(f"更新回忆内容时发生错误: {e}")

    def get_queue(self) -> List[Dict[str, str]]:
        """
        获取当前队列内容，包括回忆内容和对话消息

        返回:
            - 包含回忆内容和对话消息的完整队列
        """
        full_queue = []
        # 如果有回忆内容，添加到队头
        if self.current_recall:
            full_queue.append(copy.deepcopy(self.current_recall))
        # 添加所有对话消息
        full_queue.extend(copy.deepcopy(self.queue))
        full_queue[-1]["content"] += "(请严格参照系统提示词)"
        return full_queue

    def clear(self) -> None:
        """
        清空队列，清空前将剩余消息发送到记忆接口
        """
        try:
            # 在清空队列前保存剩余消息
            if self.queue:
                logger.info(f"清空队列前保存{len(self.queue)}条剩余消息")
                self._save_memory()
        except Exception as e:
            logger.error(f"清空队列前保存消息时发生错误: {e}")
        finally:
            # 清空队列和计数
            self.queue = []
            self.message_count = 0
            # 不清空当前回忆，保留最新的回忆内容

    def get_current_recall(self) -> Optional[str]:
        """
        获取当前的回忆内容

        返回:
            - 当前的回忆内容，如果不存在则返回None
        """
        if self.current_recall:
            return self.current_recall.get("content", None)
        return None

    def get_dialogue_queue(self) -> List[Dict[str, str]]:
        """
        获取纯对话消息队列（不包含回忆内容）

        返回:
            - 仅包含对话消息的队列
        """
        return self.queue.copy()