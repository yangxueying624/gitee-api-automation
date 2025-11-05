# 仓库相关测试用例
import pytest
from api.repo_api import create_gitee_repo,get_gitee_repo_info,delete_gitee_repo
import time
from utils.log import logger

# 测试仓库创建 ——> 查询 ——> 删除的完整流程
def test_repo_full_flow():
    """
    time.time()是Python内置模块的time函数，作用是返回 “当前时间距离1970年1月1日00:00:00（世界标准时间）的秒数”
    如：1730700000.123456
    整数部分：从 1970 年到现在的总秒数（比如 1730700000）
    小数部分：不足 1 秒的毫秒 / 微秒（比如 0.123456，代表 123 毫秒）

    int()把浮点数转成整数，只保留前面的总秒数，去掉小数部分。
    """
    repo_name=f"test-repo-{int(time.time())}"
    repo_desc="测试仓库全流程（创建——>查询——>删除）"

    # 创建仓库
    repo_full_name=create_gitee_repo(repo_name,repo_desc)
    assert repo_full_name is not None,"❌ 仓库创建失败，终止测试"
    time.sleep(2)

    # 查询仓库信息
    repo_info=get_gitee_repo_info(repo_full_name)
    assert repo_info is not None,"❌ 仓库信息查询失败"
    assert repo_info["name"]==repo_name, f"❌ 仓库名不匹配！预期{repo_name}，实际{repo_info['name']}"

    # 删除仓库
    desult_result=delete_gitee_repo(repo_full_name)
    assert desult_result is True,"❌ 仓库删除失败"
    logger.info(f"✅ 仓库 {repo_full_name} 已成功删除")

    logger.info("🎉 仓库全流程测试通过！")