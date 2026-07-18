import pytest
import time
from typing import Generator
from api.repo_api import GiteeRepoClient
from api.file_api import GiteeFileClient


# scope="session" 会话级，整个测试全程只执行1次，生成的对象全局缓存复用
@pytest.fixture(scope="session")
def repo_client() -> GiteeRepoClient:
    return GiteeRepoClient()


# scope="function" 函数级，测试函数声明该夹具为参数时，会在测试函数运行前执行一次；搭配 autouse=True 时，所有测试函数自动执行
@pytest.fixture
def created_repo(repo_client: GiteeRepoClient) -> Generator[str, None, None]:
    """
    Generator [str, None, None] 三段参数含义（固定格式）：
    语法：Generator[产出值类型, 传入send的值类型, 函数最终return返回类型]
    第一个 str：yield full_name 抛出出去的值是字符串（仓库名称）
    第二个 None：我们代码里不用 generator.send() 向夹具传数据，填 None
    第三个 None：夹具函数走完所有代码后没有最终 return 值，填 None
    """
    repo_name = f"auto-fixture-test-{int(time.time())}"
    full_name = repo_client.create_repo(repo_name, "自动化测试临时仓库")

    yield full_name

    if full_name:
        repo_client.delete_repo(full_name)


@pytest.fixture(scope="session")
def file_client() -> GiteeFileClient:
    return GiteeFileClient()


@pytest.fixture
def upload_file(
    file_client: GiteeFileClient, created_repo: str
) -> Generator[str, None, None]:
    repo_full_name = created_repo
    local_path = "test_file.txt"
    remote_path = "test_upload.txt"
    file_client.upload_file(repo_full_name, local_path, remote_path)

    yield remote_path

    file_client.delete_file(repo_full_name, remote_path)
