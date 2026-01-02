from typing import Dict

class Message:
    """
    消息类，包含role、content、character三个字符串字段
    支持序列化为JSON格式，用于接口请求体传递
    role: 消息角色，如"user"、"assistant"等
    content: 消息内容，如用户输入或模型回复
    character: 角色或字符ID，用于指定消息所属的角色或字符，默认值为"用户"
    """

    def __init__(self, role: str, content: str, character: str = "用户"):
        # 字段类型校验，确保传入均为字符串
        if not isinstance(role, str):
            raise TypeError(f"role必须是字符串类型，当前传入：{type(role).__name__}")
        if not isinstance(content, str):
            raise TypeError(f"content必须是字符串类型，当前传入：{type(content).__name__}")
        if not isinstance(character, str):
            raise TypeError(f"character必须是字符串类型，当前传入：{type(character).__name__}")

        self.role = role
        self.content = content
        self.character = character

    def to_dict(self) -> Dict[str, str]:
        """将类实例转换为字典（用于构造JSON请求体）"""
        return {
            "role": self.role,
            "content": self.content,
            "character": self.character
        }

    def __repr__(self) -> str:
        """类实例打印格式化，方便调试"""
        return f"Message(role='{self.role}', content='{self.content}', character='{self.character}')"