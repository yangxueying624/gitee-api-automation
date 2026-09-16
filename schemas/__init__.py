# Schema 包初始化文件：导出所有 Schema 定义，方便外部直接import
from schemas.repo_schema import (
    REPO_INFO_SCHEMA,
    CREATE_REPO_SCHEMA,
    REPO_LIST_SCHEMA,
)

from schemas.user_schema import USER_INFO_SCHEMA


"""
这么做的好处：后面在测试用例里，不用写很长的导入路径，可以直接这样导入：from schemas import REPO_INFO_SCHEMA
而不是每次都写；from schemas.repo_schema import REPO_INFO_SCHEMA

一句话总结：`__init__.py` 的作用就是做统一出口，打包好所有 schema 给外面调用
"""