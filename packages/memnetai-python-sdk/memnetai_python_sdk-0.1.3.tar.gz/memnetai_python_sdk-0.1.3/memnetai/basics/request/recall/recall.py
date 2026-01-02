from typing import Dict, Optional, Any, List
from memnetai.basics.request.MemNetAIClient import MemNetAIClient


def recall_api_request(
        url: str,
        api_key: str,
        memory_agent_name: str,
        query: str,
        namespace: str = "default",
        character: str = "用户",
        recall_deep: int = 1,
        is_include_linked_new_memories_from_invalid: int = 0,
        is_using_associative_thinking: int = 1,
        is_using_common_sense_database: int = 1,
        is_using_global_common_sense_database: int = 1,
        is_using_memory_agent_common_sense_database: int = 0,
        common_sense_database_id_list: Optional[List[str]] = None,
        is_returning_detailed_memory_info: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    通用API请求发送函数，参数可配置，返回接口响应数据（字典格式）
    :param url: 接口地址
    :param api_key: 接口密钥，如"your_api_key_here"
    :param memory_agent_name: 记忆体名称,存在则使用，不存在则创建
    :param query: 用户当前所说的话，如"你好"
    :param namespace: 命名空间，默认值为空字符串
    :param character: 角色或字符ID，用于指定消息所属的角色或字符，默认值为"用户"
    :param recall_deep: 回忆深度，默认值为1
    :param is_include_linked_new_memories_from_invalid: 是否使用非有效性记忆关联的新记忆，默认值为0
    :param is_using_associative_thinking: 是否使用关联思考，默认值为1
    :param is_using_common_sense_database: 是否使用常识数据库，默认值为1
    :param is_using_global_common_sense_database: 是否使用全局常识数据库，默认值为1
    :param is_using_memory_agent_common_sense_database: 是否使用记忆体 Agent 常识数据库，默认值为1
    :param common_sense_database_id_list: 常识数据库 ID 列表，默认值为None
    :param is_returning_detailed_memory_info: 是否返回详细记忆信息，默认值为0
    :return: 接口响应字典（包含状态码、响应体等），异常时返回None
    """
    # 使用统一客户端
    client = MemNetAIClient(base_url=url, api_key=api_key)

    return client.recall(
        memory_agent_name=memory_agent_name,
        query=query,
        character=character,
        recall_deep=recall_deep,
        is_include_linked_new_memories_from_invalid=is_include_linked_new_memories_from_invalid,
        is_using_associative_thinking=is_using_associative_thinking,
        is_using_common_sense_database=is_using_common_sense_database,
        is_using_global_common_sense_database=is_using_global_common_sense_database,
        is_using_memory_agent_common_sense_database=is_using_memory_agent_common_sense_database,
        common_sense_database_id_list=common_sense_database_id_list,
        is_returning_detailed_memory_info=is_returning_detailed_memory_info,
        namespace=namespace
    )