from memnetai.basics.request.message.message import Message
from memnetai.upgrade.config.config import Config
from memnetai.upgrade.llm_init import create_instance
from memnetai.upgrade.memory_message_queue.memory_message_queue import MemoryMessageQueue


class MemNetAIClientPlus:
    def __init__(self, config: Config):
        self.message_queue = MemoryMessageQueue(config)
        self.llm_provider = create_instance(config.get("class_name"), config)
        self.memory_agent_name = config.memory_agent_name

    def chat(self) -> str:
        """
        与LLM进行对话

        :return: LLM的回复
        """
        # 获取生成器响应
        response_generator = self.llm_provider.response(self.message_queue.get_queue())

        # 将生成器的所有部分连接成完整字符串
        full_response = ""
        for part in response_generator:
            full_response += part

        # 将LLM的回复也添加到消息队列中
        ai_response = Message(role='assistant', content=full_response, character=self.memory_agent_name)
        self.message_queue.add_message(ai_response.to_dict())

        return full_response

    def input(self, message: str = None) -> bool:
        """
        输入用户消息到消息队列，如果没有提供消息，则从控制台获取

        :param message: 用户输入的消息（可选）
        :return: 是否继续运行（True为继续，False为退出）
        """
        if message is None:
            message = input("请输入用户消息（输入'exit'或'quit'退出）：")

        # 检查退出命令
        if message.lower() in ['exit', 'quit']:
            return False

        user_message = Message(role='user', content=message)
        self.message_queue.add_message(user_message.to_dict())
        return True

    def close(self) -> None:
        """
        清空消息队列
        """
        self.message_queue.clear()