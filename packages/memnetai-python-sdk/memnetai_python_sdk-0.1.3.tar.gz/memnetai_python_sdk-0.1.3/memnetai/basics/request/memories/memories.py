from typing import Dict, Optional, Any, List
from memnetai.basics.request.MemNetAIClient import MemNetAIClient
from memnetai.basics.request.message.message import Message


def memories_api_request(
        url: str,
        api_key: str,
        memory_agent_name: str,
        messages: Optional[List[Message]],
        namespace: str = "default",
        language: str = "zh-CN",
        is_third_person: int = 0,
        metadata: str = "",
        async_mode: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    通用API请求发送函数，参数可配置，返回接口响应数据（字典格式）
    :param url: 接口地址
    :param api_key: 接口密钥，如"your_api_key_here"
    :param memory_agent_name: 记忆体名称,存在则使用，不存在则创建
    :param messages: 对话上下文消息内容，可选，默认值为空列表
    :param namespace: 命名空间，默认值为空字符串
    :param language: 记忆摘要预期语言,默认中文
    :param is_third_person: 0:不启用第三人称（摘要以第一人称“我”进行讲述） 1:启用第三人称（摘要以“记忆体名：”进行讲述），默认为0
    :param metadata: 元数据,与当前记忆有关的各种其他信息可以记录在这里面，回忆时会携带
    :param async_mode: 是否启用异步记忆,0:不启用异步记忆，记忆完成才会返回响应 1:启动异步记忆，请求后立马响应，稍后完成记忆 默认为0
    :return: 接口响应字典（包含状态码、响应体等），异常时返回None
    """
    # 使用统一客户端
    client = MemNetAIClient(base_url=url, api_key=api_key)

    if not messages:
        messages = []

    return client.memories(
        memory_agent_name=memory_agent_name,
        messages=messages,
        language=language,
        is_third_person=is_third_person,
        metadata=metadata,
        async_mode=async_mode,
        namespace=namespace
    )