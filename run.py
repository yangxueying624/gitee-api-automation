import pytest
from utils.log import logger
# import allure

if __name__ == "__main__":
    logger.info("开始执行Gitee自动化测试用例！")
    # pytest.main()是pytest框架提供的“命令行入口函数”,作用是“代替你在命令行里敲pytest命令，[]里装的就是 “要在命令行里写的参数”
    pytest.main(
        [
            "testcases/",  # 指定要运行的用例文件夹：只执行testcases目录下所有以test_开头的测试脚本
            "-v",  # 详细模式，显示所有测试用例的执行结果
            "--alluredir=allure-results",  # 生成Allure报告数据（放在allure-results文件夹）
            "--clean-alluredir",  # 每次执行前清空旧的报告数据，避免重复
        ]
    )
    logger.info("Gitee自动化测试用例执行完成！")
