"""
LLM（大语言模型）提供者工厂
"""

import importlib
import os
import sys

from memnetai.upgrade.llm.base import LLMProviderBase
from memnetai.upgrade.config.config import Config


# 添加项目根目录到Python路径，以保证任何情况下都能正常导入对应的provider
def get_project_dir():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


project_root = get_project_dir()
sys.path.insert(0, project_root)


def create_instance(class_name: str, config: Config) -> LLMProviderBase:
    """
    根据提供者的类型名和具体提供者的配置字典来创建LLM提供者实例（工厂）

    :param class_name: LLM提供者的具体种类名
    :param config: LLM提供者所需要的配置对象
    :return: LLM基类类型的提供者实例
    """

    # 创建LLM实例
    provider_path = os.path.join(project_root, 'upgrade', 'llm', class_name, f'{class_name}_provider.py')
    if os.path.exists(provider_path):
        lib_name = f'upgrade.llm.{class_name}.{class_name}_provider'
        if lib_name not in sys.modules:
            sys.modules[lib_name] = importlib.import_module(lib_name)
        return sys.modules[lib_name].LLMProvider(config)

    raise ValueError(f'不支持的LLM类型: {class_name}，请检查该配置的type是否设置正确')
