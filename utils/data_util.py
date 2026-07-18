"""
数据读取工具模块：支持读取Excel / YAML / JSON三种格式的测试数据文件
pandas库：读取Excel文件（核心方法：pd.read_excel）
yaml库：读取YAML格式配置文件
json库：读取JSON格式配置文件
pathlib库：现代化路径处理工具（替代传统os.path路径操作）
"""

import pandas as pd
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any
from utils.log import logger

"""
补充知识点：df.to_dict(orient="xxx") 两种常用转换格式
1. df.to_dict("records") 等价 df.to_dict(orient="records")
   输出 List[Dict]，一行表格=一条独立用例字典，自动化数据驱动专用
   [{"用例ID":"TC001","repo_name":"xxx"},{"用例ID":"TC002","repo_name":"xxx"}]
2. df.to_dict("dict")
   输出 {列名: [整列所有数据]}，适合批量提取单列数据、统计分析
   {"用例ID":["TC001","TC002"],"repo_name":["xxx","xxx"]}
"""

# 定义全局常量DATA_DIR，表示测试数据文件夹路径
DATA_DIR: Path = Path(__file__).parent.parent / "data"
# 定义全局常量SUPPORTED_FORMATS，表示支持的测试数据文件格式
SUPPORTED_FORMATS: set={".xlsx",".yaml",".yml",".json"}


# 函数名以单下划线_开头：约定为内部私有函数，只允许当前文件内部调用，外部测试脚本不直接调用
def _read_excel(file_path: Path, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
    """
    读取Excel格式测试用例：
    :param file_path：Excel完整Path路径对象
    :param sheet_name: 工作表名称，默认"Sheet1"
    :return：标准用例列表 List[Dict[str, Any]]
    """

    # pandas第三方库仅支持字符串路径，Path对象必须强制str转换
    df=pd.read_excel(str(file_path),sheet_name=sheet_name,engine="openpyxl")
    data_list: List[Dict[str, Any]]=df.to_dict(orient="records")
    # file_path.name用于提取文件名+后缀，如repo_test_data.xlsx
    logger.info(f"读取Excel数据成功：{file_path.name},行数={len(data_list)}")
    return data_list


def _read_yaml(file_path: Path) -> List[Dict[str, Any]]:
    """
    读取YAML格式测试用例：

    yaml.safe_load()：将YAML文件解析为Python内存对象
    - YAML列表（以'-'开头的条目） -> 转换成Python list列表
    - YAML字典（key: value） -> 转换成Python dict字典

    :param file_path:YAML文件完整Path路径对象
    :return:标准用例列表 List[Dict[str, Any]]
    """
    # 内置open()可直接接收Path对象，无需转字符串
    with open(file_path,"r",encoding="utf-8") as f:
        data_list: List[Dict[str, Any]] = yaml.safe_load(f)
    # 校验解析结果顶层是否为列表
    if not isinstance(data_list,list):
        # type(data_list).__name__作用：返回该类型的纯文本字符串名称，如：<class 'list'>.__name__ → "list"
        logger.error(f"YAML格式错误：预期顶层为列表，实际类型是{type(data_list).__name__}")
        return []
    logger.info(f"读取YAML数据成功：{file_path.name},行数={len(data_list)}")
    return data_list


def _read_json(file_path: Path) -> List[Dict[str, Any]]:
    """
    读取JSON格式测试用例

    json.load()：将JSON文件解析为Python内存对象
    与json.loads()的区别：
    - json.load(文件对象f)：直接从打开的文件读取数据
    - json.loads(字符串)：解析一段JSON格式的文本字符串

    :param file_path:JSON文件完整路径
    :return:由多个字典组成的列表
    """
    with open(file_path,"r",encoding="utf-8") as f:
        data_list: List[Dict[str, Any]]=json.load(f)
    if not isinstance(data_list,list):
        logger.error(f"JSON格式错误：预期顶层为列表，实际类型是{type(data_list).__name__}")
        return []
    logger.info(f"读取JSON数据成功：{file_path.name},行数={len(data_list)}")
    return data_list


def read_test_data(file_name: str,sheet_name: str="Sheet1") -> List[Dict[str, Any]]:
    """
     【公共统一入口】策略模式，自动识别文件后缀分发读取逻辑
    什么叫策略模式？
    把多种独立算法 / 业务逻辑分别封装成独立函数，通过统一入口调用

    :param file_name: data目录下的用例文件名
    :param sheet_name: Excel工作表名称（仅.xlsx文件生效）
    :return: 标准用例列表；文件缺失/格式不支持/读取异常均返回空列表[]
    """
    file_path: Path=DATA_DIR / file_name
    # .suffix是Path内置属性，用来提取文件后缀，如repo.yaml提取.yaml
    suffix: str=file_path.suffix.lower()
    if not file_path.exists():
        logger.error(f"数据文件不存在:{file_path}")
        return []
    if suffix not in SUPPORTED_FORMATS:
        logger.error(f"不支持该格式文件: {suffix},只支持:{SUPPORTED_FORMATS}")
        return []

    try:
        if suffix == ".xlsx":
            return _read_excel(file_path, sheet_name)
        elif suffix in (".yaml",".yml"):
            return _read_yaml(file_path)
        elif suffix == ".json":
            return _read_json(file_path)
        return []
    except Exception as e:
        logger.error(f"读取数据文件异常[{file_name}]:{str(e)}")
        return []


def read_excel_data(file_name: str,sheet_name="Sheet1") -> List[Dict[str, Any]]:
    """
    向下兼容封装函数，底层实际调用统一读取入口 read_test_data
    历史项目中原本调用 read_excel_data()的旧代码无需修改，可以正常运行
    """
    return read_test_data(file_name, sheet_name)







