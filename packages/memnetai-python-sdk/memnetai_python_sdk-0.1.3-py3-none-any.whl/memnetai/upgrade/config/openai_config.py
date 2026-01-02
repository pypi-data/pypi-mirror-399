from memnetai.upgrade.config.config import Config


class OpenAIConfig(Config):
    """
    OpenAI LLM配置类
    """
    def __init__(self, memnetai_api_key: str, memory_agent_name: str, base_url: str,
                 model_name: str, api_key: str,namespace: str = "default", memnetai_base_url: str = "https://api.memnetai.com/api", temperature: float = 0.7, max_tokens: int = 500,
                 window_size: int = 32):
            """
            初始化OpenAI配置
            :param memnetai_base_url: MemNetAI API基础URL
            :param memnetai_api_key: MemNetAI API密钥
            :param memory_agent_name: 记忆智能体名称
            :param namespace: 命名空间，用于隔离不同应用的记忆
            :param base_url: OpenAI API基础URL
            :param model_name: OpenAI模型名称
            :param api_key: OpenAI API密钥
            :param temperature: OpenAI模型的温度参数
            :param max_tokens: OpenAI模型的最大令牌数
            :param window_size: 对话窗口大小，默认值为32,不得小于32
            """
            super().__init__(memnetai_base_url=memnetai_base_url, memnetai_api_key=memnetai_api_key, memory_agent_name=memory_agent_name, namespace=namespace, window_size=window_size)
            self.base_url = base_url
            self.model_name = model_name
            self.api_key = api_key
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.class_name = "openai"
