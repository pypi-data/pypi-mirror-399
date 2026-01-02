# 在 config.py 文件中添加
class Config:
    """
    LLM配置基类，所有LLM配置类都应该继承此类
    """

    def __init__(self, memnetai_api_key: str, memory_agent_name: str, namespace: str = "default", memnetai_base_url: str = "https://api.memnetai.com/api", window_size: int = 32):
        """
        初始化配置
        :param memnetai_base_url: MemNet AI API基础URL
        :param memnetai_api_key: MemNet AI API密钥
        :param memory_agent_name: 记忆智能体名称
        :param namespace: 命名空间，用于隔离不同应用的记忆
        :param window_size: 对话窗口大小，默认值为32,不得小于32
        """
        self.memnetai_base_url = memnetai_base_url
        self.memnetai_api_key = memnetai_api_key
        self.memory_agent_name = memory_agent_name
        self.namespace = namespace
        if window_size < 32:
            raise ValueError("window_size must be at least 32")
        self.window_size = window_size

    def get(self, key: str):
        """
        获取配置项的值
        :param key: 配置项名称
        :return: 配置项的值
        """
        return getattr(self, key, None)

    def to_dict(self) -> dict:
        """
        将配置转换为字典格式
        :return: 包含所有配置项的字典
        """
        return self.__dict__
