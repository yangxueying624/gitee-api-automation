"""
Mock 测试模块：不依赖真实 API，用假数据测试客户端逻辑

requests-mock 的原理：
    拦截 requests 发出的 HTTP 请求，返回我们预设的假响应
    这样就能测试：
    - 成功场景（201/200）
    - 失败场景（400/404/500）
    - 网络异常（超时、连接拒绝）
    - 响应数据解析

Mock 测试的价值（面试话术）：
    1. 隔离外部依赖（不怕 API 宕机、限流）
    2. 覆盖极端场景（500、超时，真实环境很难复现）
    3. 运行速度快（没有真实网络请求）
    4. 结果确定（同样的输入永远得到同样的输出）
"""

import pytest
import requests_mock as rm
import requests
from api.repo_api import GiteeRepoClient
from schemas import REPO_INFO_SCHEMA
from utils.schema_util import validate_schema

@pytest.fixture
def mock_client() -> GiteeRepoClient:
    """创建一个用假 Token 的客户端，专门给 Mock 测试用"""
    return GiteeRepoClient(token="fake-test-token")


# ==================== 创建仓库 Mock 测试 ====================
class TestRepoCreateMock:
    """创建仓库相关的 Mock 测试"""

    def test_create_repo_success(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：服务器返回 201，创建成功"""
        fake_response = {
            "id": 12345,
            "full_name": "testuser/test-repo-001",
            "name": "test-repo-001",
            "description": "test desc",
            "private": False,
        }
        # 启动mock拦截器：缩进块内所有requests请求都会被拦截，不会访问真实Gitee服务
        with rm.Mocker() as m:
            # 设置匹配规则：当发起POST请求访问该URL时，不再请求真实服务器，直接返回预设fake_response，状态码201
            m.post(
                "https://gitee.com/api/v5/user/repos",
                json=fake_response,
                status_code=201,
            )
            result = mock_client.create_repo("test-repo-001", "test desc")
            assert result == "testuser/test-repo-001"


    def test_create_repo_duplicate_name(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：仓库名重复，服务器返回 400"""
        with rm.Mocker() as m:
            m.post(
                "https://gitee.com/api/v5/user/repos",
                json={"message": "Repository name already exists"},
                status_code=400,
            )
            result = mock_client.create_repo("existing-repo", "desc")
            assert result is None


    def test_create_repo_server_error(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：服务器内部错误，返回 500"""
        with rm.Mocker() as m:
            m.post(
                "https://gitee.com/api/v5/user/repos",
                json={"message": "Internal Server Error"},
                status_code=500,
            )
            result = mock_client.create_repo("test-repo-500", "desc")
            assert result is None


# ==================== 查询仓库 Mock 测试 ====================
class TestRepoGetMock:
    """查询仓库相关的 Mock 测试"""

    def test_get_repo_info_success(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：服务器返回 200 + 完整仓库信息"""
        fake_response = {
            "id": 12345,
            "full_name": "testuser/test-repo",
            "name": "test-repo",
            "owner": {"login": "testuser", "id": 999},
            "private": False,
            "description": "A test repository",
            "html_url": "https://gitee.com/testuser/test-repo",
            "created_at": "2025-01-01T00:00:00+08:00",
            "updated_at": "2025-06-01T12:00:00+08:00",
        }
        with rm.Mocker() as m:
            m.get(
                "https://gitee.com/api/v5/repos/testuser/test-repo",
                json=fake_response,
                status_code=200,
            )
            result = mock_client.get_repo_info("testuser/test-repo")
            assert result is not None
            assert result["name"] == "test-repo"
            # 对 Mock 数据也做 Schema 校验
            assert validate_schema(
                data=result,
                schema=REPO_INFO_SCHEMA,
                context="mock get_repo_info",
            )


    def test_get_repo_info_not_found(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：仓库不存在，返回 404"""
        with rm.Mocker() as m:
            m.get(
                "https://gitee.com/api/v5/repos/testuser/nonexistent",
                json={"message": "404 Not Found"},
                status_code=404,
            )
            result = mock_client.get_repo_info("testuser/nonexistent")
            assert result is None

    def test_get_repo_info_timeout(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：网络超时（exc 参数让 requests-mock 抛出异常而非返回响应）"""
        with rm.Mocker() as m:
            m.get(
                "https://gitee.com/api/v5/repos/testuser/test-repo",
                exc=requests.exceptions.Timeout,
            )
            result = mock_client.get_repo_info("testuser/test-repo")
            assert result is None


# ==================== 删除仓库 Mock 测试 ====================
class TestRepoDeleteMock:
    """删除仓库相关的 Mock 测试"""

    def test_delete_repo_success(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：服务器返回 204 No Content，删除成功"""
        with rm.Mocker() as m:
            m.delete(
                "https://gitee.com/api/v5/repos/testuser/test-repo",
                status_code=204,
            )
            result = mock_client.delete_repo("testuser/test-repo")
            assert result is True

    def test_delete_repo_forbidden(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：没有权限，返回 403 Forbidden"""
        with rm.Mocker() as m:
            m.delete(
                "https://gitee.com/api/v5/repos/other/repo",
                json={"message": "Forbidden"},
                status_code=403,
            )
            result = mock_client.delete_repo("other/repo")
            assert result is False


# ==================== 列表和更新 Mock 测试 ====================
class TestRepoListUpdateMock:
    """列表查询和更新仓库的 Mock 测试"""

    def test_list_repos_success(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：返回仓库列表"""
        fake_repos = [
            {"id": 1, "full_name": "user/repo-a", "name": "repo-a"},
            {"id": 2, "full_name": "user/repo-b", "name": "repo-b"},
        ]
        with rm.Mocker() as m:
            m.get(
                "https://gitee.com/api/v5/user/repos",
                json=fake_repos,
                status_code=200,
            )
            result = mock_client.list_user_repos()
            assert result is not None
            assert len(result) == 2
            assert result[0]["name"] == "repo-a"

    def test_list_repos_empty(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：用户没有任何仓库，返回空列表"""
        with rm.Mocker() as m:
            m.get(
                "https://gitee.com/api/v5/user/repos",
                json=[],
                status_code=200,
            )
            result = mock_client.list_user_repos()
            assert result == []

    def test_update_repo_success(self, mock_client: GiteeRepoClient) -> None:
        """模拟场景：更新仓库描述成功"""
        fake_response = {
            "id": 12345,
            "full_name": "user/repo",
            "name": "repo",
            "description": "新描述",
            "private": False,
        }
        with rm.Mocker() as m:
            m.patch(
                "https://gitee.com/api/v5/repos/user/repo",
                json=fake_response,
                status_code=200,
            )
            result = mock_client.update_repo("user/repo", "新描述")
            assert result is not None
            assert result["description"] == "新描述"


