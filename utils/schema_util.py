"""
Schema 检验工具模块
jsonschema.validate()的工作原理：
    - 传入 data（实际数据）和 schema（规则定义）
    - 匹配通过 → 静默，什么都不返回
    - 匹配失败 → 抛出 ValidationError，包含详细错误信息
"""

from typing import Dict,Any
from jsonschema import validate,ValidationError
from utils.log import logger

def validate_schema(
        data: Any,
        schema: Dict[str,Any],
        context: str="",
) -> bool:
    """
    校验数据是否符合 JSON Schema 定义

     :param data: API 返回的实际响应数据
     :param schema: JSON Schema 规则字典
     :param context: 描述信息，用于日志定位（如 "create_repo 返回"）
     :return: 校验通过返回 True，失败返回 False
    """
    try:
        validate(instance=data, schema=schema)
        logger.info(f"[schema] 校验通过：{context}")
        return True
    except ValidationError as e:
        # e.absolute_path：定位到具体哪个字段出了问题
        # e.message：具体错误描述
        logger.error(
            f"[schema] 校验失败：{context} | "
            f"字段路径={list(e.absolute_path)} | 错误信息={e.message}"
        )
        return False