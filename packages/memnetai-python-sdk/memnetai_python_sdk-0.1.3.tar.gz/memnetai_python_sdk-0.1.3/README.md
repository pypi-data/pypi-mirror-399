from pyexpat.errors import messagesfrom pyexpat.errors import messages

# MemNet AI Python SDK

MemNet AI Python SDK 提供了与MemNet AI API交互的Python接口，包括基础请求客户端和增强功能。

## 功能特性

- 基础API请求客户端
- 记忆管理功能
- 思考功能
- 梦境功能
- 常识功能
- 增强版客户端（带LLM集成）

## 安装

```bash
pip install memnetai-python-sdk
```

## 快速开始

### 基础客户端使用

```python
# 初始化客户端
client = MemNetAIClient(
    base_url="https://api.memnet.ai",
    api_key="your_api_key"
)

messages = [
    message(role="user", content="什么是人工智能？", character="default")
]

# 1. 记忆
response = client.memories(
    memory_agent_name="default",
    messages=messages
)
print("回忆结果:", response)

# 2. 回忆
response = client.recall(
    memory_agent_name="default",
    query="什么是人工智能？",
)
print("回忆结果:", response)

# 3. 思考功能
response = client.think(
    memory_agent_name="default",
)
print("思考结果:", response)

# 4. 梦境功能
response = client.dream(
    memory_agent_name="default",
)
print("梦境结果:", response)

# 5. 常识功能
response = client.common_sense(
    common_sense_database_id="default",
    common_sense_text="科学",
)
print("常识结果:", response)
```

### 增强版客户端使用

```python
from memnetai.upgrade import MemNetAIClientPlus
from memnetai.upgrade.config.openai_config import OpenAIConfig


def test_memnetaiclientplus():
    # 配置OpenAI参数
    openai_config = OpenAIConfig(
        memnetai_base_url="https://api.memnet.ai",
        memnetai_api_key="your_memnet_api_key",
        memory_agent_name="default",
        base_url="https://api.openai.com/v1",
        api_key="your_openai_api_key",
        model_name="gpt-3.5-turbo",
    )

    # 初始化增强版客户端
    client_plus = MemNetAIClientPlus(config=openai_config)

    # 智能对话（自动记忆和回忆）
    try:
        while True:
            if not client_plus.input():  # 用户输入了退出命令
                break
            response = client_plus.chat()
            print(f"AI回复: {response}")
    except KeyboardInterrupt:
        print("\n正在关闭程序...")
    finally:
        client_plus.close()


if __name__ == "__main__":
    test_memnetaiclientplus()
```

## API 文档

### 基础客户端 API

#### 记忆管理
- `recall()`: 根据查询检索记忆
- `memories_create()`: 创建新记忆
- `memories_detail()`: 获取记忆详情
- `memories_progress()`: 获取记忆处理进度
- `memories_all()`: 获取所有记忆
- `memories_delete()`: 删除记忆

#### 思考功能
- `think()`: 触发AI思考过程
- `think_detail()`: 获取思考详情
- `think_all()`: 获取所有思考任务
- `think_delete()`: 删除思考任务

#### 梦境功能
- `dream()`: 创建梦境任务
- `dream_detail()`: 获取梦境详情
- `dream_all()`: 获取所有梦境任务
- `dream_delete()`: 删除梦境任务

#### 常识功能
- `common_sense()`: 查询常识数据库
- `common_sense_detail()`: 获取常识详情
- `common_sense_progress()`: 获取常识处理进度
- `common_sense_all()`: 获取所有常识任务
- `common_sense_delete()`: 删除常识任务

### 增强版客户端 API

#### 智能对话
- `chat()`: 智能对话（自动记忆和回忆）
- `input()`: 用户输入（触发对话）
- `close()`: 关闭客户端连接

#### 配置参数
- `OpenAIConfig`: OpenAI配置参数，包含模型、温度、最大令牌等
