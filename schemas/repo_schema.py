"""
仓库接口的 JSON Schema 定义
JSON Schema是什么？
    用一个字典来描述“数据应该长什么样”，包括：
    - type：字段类型（string/integer/boolean/object/array）
    - require：哪些字段必须存在
    - properties：每个字段的具体规则
jsonschema.validate()的行为：
    - 数据符合 Schema → 静默通过，不返回任何内容
    - 数据不符合 Schema → 抛出ValidationError异常
"""

# 导入类型注解
from typing import Dict,Any

# GET /repos/{owner}/{repo} 返回的仓库详情 Schema
REPO_INFO_SCHEMA: Dict[str,Any]={
    "type":"object",
    "required":["id","full_name","name","owner","private"],
    "properties":{
        "id":{"type":"integer"},
        "full_name":{"type":"string"},
        "private": {"type": "boolean"},
        "name":{"type":"string"},
        "owner":{
            "type":"object",
            "required":["login","id"],
            "properties":{
                "login":{"type":"string"},
                "id":{"type":"integer"},
            },
        },
        "html_url":{"type":"string"},
        "created_at":{"type":"string"},
        "updated_at":{"type":"string"},
    },
}


# POST /user/repos 创建仓库返回的 Schema
CREATE_REPO_SCHEMA: Dict[str,Any]={
    "type":"object",
    "required":["id","full_name","name"],
    "properties":{
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "private": {"type": "boolean"},
    },
}


# GET /user/repos 仓库列表返回的 Schema
REPO_LIST_SCHEMA: Dict[str, Any] = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "full_name", "name"],
        "properties": {
            "id": {"type": "integer"},
            "full_name": {"type": "string"},
            "name": {"type": "string"},
        },
    },
}