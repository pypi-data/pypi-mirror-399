from loguru import logger
from openai import OpenAI

from memnetai.upgrade.config.config import Config
from memnetai.upgrade.config.openai_config import OpenAIConfig
from memnetai.upgrade.llm.base import LLMProviderBase


class LLMProvider(LLMProviderBase):
    def __init__(self, config: Config):
        """
        初始化OpenAI LLM提供者
        :param config: OpenAI配置类实例
        """
        self.base_url = config.get('base_url')
        self.model_name = config.get('model_name')
        self.api_key = config.get('api_key')
        self.temperature = config.get('temperature')
        self.max_tokens = config.get('max_tokens')

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def response(self, dialogue):
        """
        生成模型响应
        :param dialogue: 对话内容
        :return: 模型响应
        """

        try:
            responses = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            is_active = True
            for chunk in responses:
                try:
                    # 检查是否存在有效的choice且content不为空
                    delta = chunk.choices[0].delta if getattr(chunk, 'choices', None) else None
                    content = delta.content if hasattr(delta, 'content') else ''
                except IndexError:
                    content = ''
                if content:
                    # 处理标签跨多个chunk的情况
                    if '<think>' in content:
                        is_active = False
                        content = content.split('<think>')[0]
                        yield content
                    if '</think>' in content:
                        is_active = True
                        content = content.split('</think>')[-1]
                    if is_active:
                        yield content

        except Exception as err:
            logger.error(f'在LLM响应生成过程中出现错误: {err}')

    def response_with_tool_calls(self, dialogue, tools=None):
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools
            )

            for chunk in stream:
                yield {
                    'content': chunk.choices[0].delta.content,
                    'tool_calls': chunk.choices[0].delta.tool_calls
                }

        except Exception as err:
            logger.error(f'工具调用流式响应中出现了问题: {err}')
            yield {
                'content': f'OpenAI服务响应异常，请前往websocket后端查看系统日志',
                'tool_calls': None
            }


# 人工测试代码可用性
if __name__ == '__main__':
    # 定义测试配置
    configTest = OpenAIConfig(
        memnetai_base_url='',
        memnetai_api_key='',
        memory_agent_name='',
        base_url='',
        model_name='gpt-3.5-turbo',
        api_key='',
        temperature=0.7,
        max_tokens=500
    )

    # 创建LLM提供者实例
    provider = LLMProvider(configTest)

    # noinspection PyProtectedMember
    provider._manual_test(provider)
