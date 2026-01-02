from typing import Dict, Optional, Any
from memnetai.basics.request.MemNetAIClient import MemNetAIClient


def think_detail_request(
        url: str,
        api_key: str = "",
) -> Optional[Dict[str, Any]]:
    """
    通用API请求发送函数，参数可配置，返回接口响应数据（字典格式）
    :param url: 接口地址
    :param api_key: 接口密钥，如"your_api_key_here"
    :return: 接口响应字典（包含状态码、响应体等），异常时返回None
    """
    # 使用统一客户端
    client = MemNetAIClient(base_url=url, api_key=api_key)

    return client.think_detail()