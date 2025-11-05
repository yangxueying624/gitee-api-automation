# 文件相关用例
import pytest
from api.repo_api import create_gitee_repo, delete_gitee_repo
from api.file_api import upload_file_to_repo, delete_gitee_file
import time
import os
from utils.log import logger

# 测试文件上传→删除的流程（依赖仓库）
def test_file_full_flow():
    # 创建一个临时仓库
    repo_name=f"test-repo-file-{int(time.time())}"
    repo_full_name=create_gitee_repo(repo_name,"测试文件上传删除")
    assert repo_full_name is not None, "❌ 仓库创建失败，无法测试文件"
    time.sleep(2)

    # 准备本地测试文件（如果没有，现在本地创建test.file.text）
    local_file=os.path.join(os.path.dirname(os.path.dirname(__file__)),"test_file.txt")
    # 检查test_file.txt是否存在，不存在则创建一个
    if not os.path.exists(local_file):
        # 用open(...,"w")创建文件
        with open(local_file,"w",encoding="utf-8") as f:
            f.write("这是测试文件，用于Gitee文件上传测试")
        logger.info(f"本地测试文件不存在，已自动创建{local_file}")


    # 上传文件到仓库
    upload_result=upload_file_to_repo(repo_full_name,local_file,"test_upload.txt")
    assert upload_result is True,"❌ 文件上传失败"

    # 删除刚上传的文件
    delete_file_result=delete_gitee_file(repo_full_name,"test_upload.txt")
    assert delete_file_result is True, "❌ 文件删除失败"

    # 删除临时仓库（清理环境）
    delete_repo_result=delete_gitee_repo(repo_full_name)
    assert delete_repo_result is True, "❌ 临时仓库删除失败"

    logger.info("🎉 文件上传删除流程测试通过！")