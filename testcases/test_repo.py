import pytest
import time
from typing import Dict, Any
from api.repo_api import GiteeRepoClient
from utils.log import logger
from utils.data_util import read_excel_data

"""
"test_data"：字符串类型，是 “参数名”，表示下面的测试函数会接收一个名为 test_data 的参数
read_excel_data("repo_test_data.xlsx"):是 “参数值列表”，即 test_data 会依次接收的值
"""


@pytest.mark.parametrize("test_data", read_excel_data("repo_test_data.xlsx"))
def test_repo_create_data_driven(
    test_data: Dict[str, Any], repo_client: GiteeRepoClient
) -> None:
    """
    数据驱动测试：创建仓库场景（正常+异常）
    :param test_data: 从Excel读取的单条测试数据字典
    :param repo_client: Session级fixture注入的仓库客户端实例
    """
    case_id: str = test_data["用例ID"]
    # repalce替换逻辑：有则替换，无则不变
    repo_name: str = test_data["repo_name"].replace("{time}", str(int(time.time())))
    repo_desc: str = test_data["repo_desc"]
    expected_status: int = test_data["expected_status"]
    expected_msg: str = test_data["expected_msg"]
    logger.info(f"执行用例：{case_id}，测试场景：{repo_desc}")

    repo_full_name = repo_client.create_repo(repo_name, repo_desc)
    if expected_status == 201:
        assert (
            repo_full_name is not None
        ), f"{case_id}失败：{expected_msg}，实际创建失败"
        time.sleep(2)

        repo_info = repo_client.get_repo_info(repo_full_name)
        assert repo_info is not None, f"{case_id}失败：查询仓库信息失败"

        repo_client.delete_repo(repo_full_name)
    else:
        assert (
            repo_full_name is None
        ), f"{case_id}失败：预期{expected_msg}，实际创建成功"

    logger.info(f"用例{case_id}执行通过！")

    """
    time.time()是Python内置模块的time函数，作用是返回 “当前时间距离1970年1月1日00:00:00（世界标准时间）的秒数”
    如：1730700000.123456
    整数部分：从 1970 年到现在的总秒数（比如 1730700000）
    小数部分：不足 1 秒的毫秒 / 微秒（比如 0.123456，代表 123 毫秒）

    int()把浮点数转成整数，只保留前面的总秒数，去掉小数部分。
    """