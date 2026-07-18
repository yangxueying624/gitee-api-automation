from typing import Optional, Dict, Any
from config import GITEE_TOKEN
from utils.log import logger
from utils.request_util import RequestUtil


class GiteeRepoClient:
    """
    Gitee仓库接口客户端

    将散落的函数封装为类的好处：
    1. Token/Base_URL统一管理，不用每个参数重复传参
    2. 后续可以加Session复用、自动重试等增强功能
    3. 测试用例通过实例化调用，更符合工程实践
    """

    BASE_URL: str = "https://gitee.com/api/v5"

    def __init__(self, token: str = GITEE_TOKEN):
        """
        初始化仓库客户端
        :param token:Gitee个人访问令牌，默认从配置文件读取
        """
        self.token: str = token
        self.headers: Dict[str, str] = {"Authorization": f"token {self.token}"}

    def create_repo(self, repo_name: str, repo_desc: str = "") -> Optional[str]:
        """
        创建仓库
        :param repo_name:仓库名称
        :param repo_desc: 仓库描述
        :return: 成功返回仓库full_name,失败则返回None
        """
        url = f"{self.BASE_URL}/user/repos"
        json_data: Dict[str, str] = {"name": repo_name, "description": repo_desc}

        """
        1. 序列化（Python字典 → JSON文本）
        语法：json.dumps
        2. 反序列化（JSON 文本 → Python 字典）
        语法：json.loads
        """
        try:
            response = RequestUtil.send_requests(
                "POST", url, headers=self.headers, json=json_data
            )
            if response and response.status_code == 201:
                repo_full_name: str = response.json()["full_name"]
                logger.info(f"创建仓库成功！仓库名：{repo_full_name}")
                return repo_full_name
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"创建仓库失败！状态码：{status}")
                return None
        except Exception as e:
            logger.error(f"创建仓库异常：{str(e)}")
            return None

    def get_repo_info(self, repo_full_name: str) -> Optional[Dict[str, Any]]:
        """
        查询仓库信息
        :param repo_full_name: 仓库完整名（如：username/reponame）
        :return: 成功返回仓库信息，失败返回None
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}"
        try:
            response = RequestUtil.send_requests("GET", url, headers=self.headers)
            if response and response.status_code == 200:
                repo_info: Dict[str, Any] = response.json()
                logger.info(f"查询仓库信息成功！仓库名：{repo_info['full_name']}")
                return repo_info
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"查询仓库信息失败！状态码：{status}")
                return None
        except Exception as e:
            logger.error(f"查询仓库信息异常：{str(e)}")
            return None

    def delete_repo(self, repo_full_name: str) -> bool:
        """
        删除仓库
        :param repo_full_name: 仓库完整名（如：username/reponame）
        :return: 删除成功返回True，失败返回False
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}"
        try:
            response = RequestUtil.send_requests("DELETE", url, headers=self.headers)
            if response and response.status_code == 204:
                logger.info(f"删除仓库成功！仓库名：{repo_full_name}")
                return True
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"删除仓库失败！状态码：{status}")
                return False
        except Exception as e:
            logger.error(f"删除仓库异常：{str(e)}")
            return False
