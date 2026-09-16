"""
用户接口的 JSON Schema 定义
用于校验 Gitee 获取用户信息接口返回的数据契约
"""
from typing import Dict, Any

# GET /user 返回的用户信息 Schema
USER_INFO_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["id", "login", "name"],
    "properties": {
        "id": {"type": "integer"},
        "login": {"type": "string"},
        "name": {"type": "string"},
        "avatar_url": {"type": "string"},
        # email 和 bio 有可能是空（null），既可以是字符串也可以是null
        "email": {"type": ["string", "null"]},
        "bio": {"type": ["string", "null"]},
        "created_at": {"type": "string"},
    },
}