import pytest
from utils.log import logger
import allure

if __name__=="__main__":
    logger.info("开始执行Gitee自动化测试用例！")
    """
    pytest.main()是pytest框架提供的“命令行入口函数”,作用是“代替你在命令行里敲pytest命令，[]里装的就是 “要在命令行里写的参数”
    """
    pytest.main([
        "testcases/",
        "-v",
        "--alluredir=allure-results"
    ])
    logger.info("Gitee自动化测试用例执行完成！")