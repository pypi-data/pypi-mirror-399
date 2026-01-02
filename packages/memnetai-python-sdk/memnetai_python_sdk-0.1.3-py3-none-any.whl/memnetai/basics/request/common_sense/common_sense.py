from typing import Dict, Optional, Any
from memnetai.basics.request.MemNetAIClient import MemNetAIClient


def commonsense_api_request(
        url: str,
        api_key: str,
        common_sense_database_id: str,
        common_sense_text: str,
        async_mode: int,
) -> Optional[Dict[str, Any]]:
    """
    通用API请求发送函数，参数可配置，返回接口响应数据（字典格式）
    :param url: 接口地址
    :param api_key: 接口密钥，如"your_api_key_here"
    :param common_sense_database_id: 常识记忆库id
    :param common_sense_text: 常识库文本内容
    :param async_mode: 异步模式，默认值为1
    :return: 接口响应字典（包含状态码、响应体等），异常时返回None
    """
    # 使用统一客户端
    client = MemNetAIClient(base_url=url, api_key=api_key)

    return client.common_sense(
        common_sense_database_id=common_sense_database_id,
        common_sense_text=common_sense_text,
        async_mode=async_mode
    )
