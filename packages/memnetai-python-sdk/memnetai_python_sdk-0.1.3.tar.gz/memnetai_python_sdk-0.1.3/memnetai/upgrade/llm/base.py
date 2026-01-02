from abc import ABC, abstractmethod
from typing import Any, Generator

from loguru import logger


class LLMProviderBase(ABC):
    """
    LLM服务提供者的抽象基类
    
    该基类定义了所有LLM提供者必须实现的接口方法，以确保不同提供者之间的互操作性。

    子类必须实现所有标记为@abstractmethod的方法。

    具备工具调用的子类应当重写response_with_tool_calls方法
    """

    @abstractmethod
    def response(self, dialogue: list[dict[str, Any]]) -> Generator[str, None, None]:
        """
        LLM响应生成器，生成流式响应内容

        :param dialogue: 对话历史，格式为[{"role": "system|user|assistant", "content": "内容"}, ...]
        :return: 生成器，逐步产出LLM响应的文本片段
        :raises: 可能抛出各类异常，取决于具体实现
        """
        pass

    def response_no_stream(self, system_prompt: str, user_prompt: str) -> str:
        """
        非流式响应方法，返回完整的LLM回复
        
        将系统提示和用户提示组合成对话格式，获取完整响应
        
        :param system_prompt: 系统提示内容
        :param user_prompt: 用户提示内容  
        :return: LLM的完整响应文本
        """
        try:
            # 构造对话格式
            dialogue = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
            result = ""
            for part in self.response(dialogue):
                result += part
            return result

        except Exception as e:
            logger.error(f'在LLM响应生成过程中出现错误: {e}')
            return '【LLM服务响应异常】'

    def response_with_tool_calls(self,
                                 dialogue: list[dict[str, Any]],
                                 tools=None
                                 ) -> Generator[dict[str, Any], None, None]:
        """
        支持工具调用的响应生成器（流式处理）
        
        对于支持工具调用的提供者，应当重写此方法以提供特定实现。
        默认实现仅返回常规文本响应，包装为特定格式。

        :param dialogue: 对话历史，格式为[{"role": "system|user|assistant", "content": "内容"}, ...]
        :param tools: 可以使用的工具
        :return: 生成器，产出包含文本内容和工具调用的字典，格式为{'content': text, 'tool_calls': tool_calls}
                其中content可能为None或字符串，tool_calls可能为None或工具调用对象
        """
        # 对于不支持工具调用的提供者，直接返回常规响应
        try:
            for token in self.response(dialogue):
                yield {
                    'content': token,
                    'tool_calls': None
                }
        except Exception as err:
            yield {
                'content': f'大语言模型服务响应异常，请前往websocket后端查看系统日志',
                'tool_calls': None
            }
            logger.error(f'在工具调用响应过程中出现错误: {err}')

    def _call_api(self, api_name: str, **kwargs):
        """
        统一调用基础包API的方法
        :param api_name: API名称，如"recall_memory", "think"等
        :param kwargs: API参数
        :return: API响应结果
        """
        method = getattr(self.base_client, api_name, None)
        if not method:
            raise ValueError(f"基础包中不存在API: {api_name}")
        return method(**kwargs)

    @staticmethod
    def _manual_test(provider: 'LLMProviderBase'):
        """
        人工手动测试方法，传入子类对象，手动测试自己实现的提供者类（实现新的提供者后，请务必使用此方法进行测试）

        :param provider: 子类对象
        """
        # 测试非流式响应
        print('\n=== 测试非流式响应 ===')
        response = provider.response_no_stream(
            '你是一个专业的AI助手，请解释问题并提供帮助。',
            '什么是人工智能？'
        )
        print(f'回答: {response}')

        # 测试流式响应
        print('\n=== 测试流式响应 ===')
        _dialogue = [
            {'role': 'system', 'content': '你是一个专业的AI助手，请解释问题并提供帮助。'},
            {'role': 'user', 'content': 'Python是什么编程语言？'}
        ]

        print('回答: ', end='', flush=True)
        for text in provider.response(_dialogue):
            print(text, end='', flush=True)
        print('\n')

        # 测试工具调用
        print('\n=== 测试工具调用 ===')
        tool_dialogue = [
            {'role': 'system', 'content': '你是一个专业的AI助手，需要通过调用工具来解决问题。'},
            {'role': 'user', 'content': '北京今天的天气如何？'}
        ]

        _tools = [{
            'type': 'function',
            'function': {
                'name': 'get_weather',
                'description': '获取指定地点的天气信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'location': {
                            'type': 'string',
                            'description': '城市名称，如北京'
                        },
                        'unit': {
                            'type': 'string',
                            'enum': ['celsius', 'fahrenheit'],
                            'description': '温度单位'
                        }
                    },
                    'required': ['location']
                }
            }
        }]

        print('工具调用响应:')
        for result in provider.response_with_tool_calls(tool_dialogue, _tools):
            _content = result.get('content')
            tool_calls = result.get('tool_calls')

            if _content:
                print(f'内容: {_content}')

            if tool_calls:
                for tool_call in tool_calls:
                    print(f'工具调用: {tool_call.function.name}')
                    print(f'参数: {tool_call.function.arguments}')

        print('\n测试完成!')
