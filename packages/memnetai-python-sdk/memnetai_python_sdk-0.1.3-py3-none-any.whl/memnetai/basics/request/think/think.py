from typing import Dict, Optional, Any
from memnetai.basics.request.MemNetAIClient import MemNetAIClient


def think_api_request(
        url: str,
        api_key: str,
        memory_agent_name: str,
        namespace: str = "default",
        subject: str = "",
        async_mode: int = 1,
        is_auto: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    通用API请求发送函数，参数可配置，返回接口响应数据（字典格式）
    :param url: 接口地址
    :param api_key: 接口密钥，如"your_api_key_here"
    :param memory_agent_name: 记忆体名称,存在则使用，不存在则创建
    :param namespace: 命名空间，默认值为空字符串
    :param subject: 思考主题，默认值为空字符串
    :param async_mode: 异步模式，默认值为1
    :param is_auto: 是否自动思考，默认值为0
    :return: 接口响应字典（包含状态码、响应体等），异常时返回None
    """
    # 使用统一客户端
    client = MemNetAIClient(base_url=url, api_key=api_key)

    return client.think(
        memory_agent_name=memory_agent_name,
        subject=subject,
        async_mode=async_mode,
        is_auto=is_auto,
        namespace=namespace
    )