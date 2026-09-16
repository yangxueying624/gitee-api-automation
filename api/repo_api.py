from sqlite3.dbapi2 import paramstyle
from typing import Optional, Dict, List,Any
from config import GITEE_TOKEN
from utils.log import logger
from utils.request_util import RequestUtil
from utils.decorators import api_log,retry


class GiteeRepoClient:
    """
    Gitee仓库接口客户端

    将散落的函数封装为类的好处：
    1. Token/Base_URL统一管理，不用每个参数重复传参
    2. 后续可以加Session复用、自动重试等增强功能
    3. 测试用例通过实例化调用，更符合工程实践
    """

    BASE_URL: str = "https://gitee.com/api/v5"

    # __init__ 是Python内置固定名字，不能改名，但内部的业务代码可以自己定义
    # 前后的双下划线作用是：告诉Python这是特殊方法，实例化对象时自动触发执行，不用手动调用
    def __init__(self, token: str = GITEE_TOKEN):
        """
        初始化仓库客户端
        :param token:Gitee个人访问令牌，默认从配置文件读取
        """
        self.token: str = token
        self.headers: Dict[str, str] = {"Authorization": f"token {self.token}"}


    # def是可执行语句，读到就生成函数对象（不执行函数内部代码）；加()才执行函数体，@装饰器拿到def生成的函数对象做包装替换
    @api_log
    def create_repo(self, repo_name: str, repo_desc: str = "") -> Optional[str]:
        """
        创建仓库

        装饰器叠加顺序（从下往上包裹，从上往下执行）：
            @api_log 在外层 → 先记录日志
            @retry   在内层 → 再执行重试
            create_repo → 最后执行实际逻辑

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
                """
                response到底是什么？
                response是一个requests库的Response类的实例对象
                response.status_code → HTTP状态码，数字
                response.headers → 接口响应头，字典
                response.text → 接口返回原始文本，字符串
                response.content → 原始字节数据
                response.json() → 对象的方法，调用之后，把返回文本解析成 Python 字典 / 列表
                """
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


    @api_log
    @retry(max_retries=2,delay=1.0)
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


    @api_log
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


    @api_log
    def update_repo(self,repo_full_name: str,new_desc: str) -> Optional[Dict[str, Any]]:
        """
        更新仓库描述（使用PATCH方法）

        PATCH 和 PUT 的区别：
            PATCH = 部分更新（只改指定字段）
            PUT = 全量替换（替换整个资源）

        :param repo_full_name:仓库完整名
        :param new_desc:新的仓库描述
        :return:成功返回更新后的仓库信息，失败返回 None
        """
        url = f"{self.BASE_URL}/repos/{repo_full_name}"
        json_data: Dict[str, str] = {"description": new_desc}
        try:
            response = RequestUtil.send_requests("PATCH", url, headers=self.headers, json=json_data)
            if response and response.status_code == 200:
                logger.info(f"<更新仓库成功：{repo_full_name}")
                return response.json()
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"<更新仓库失败：状态码={status}")
                return None
        except Exception as e:
            logger.error(f"更新仓库异常：{str(e)}")
            return None


    @api_log
    def list_user_repos(self,page: int=1,per_page: int=20) -> Optional[List[Dict[str,Any]]]:
        """
        获取当前用户的仓库列表（支持分页）
        分页机制：
            page=1，per_page=20 → 前20个仓库
            page=2，per_page=20 → 第21-40个仓库

        :param page:页码，默认1
        :param per_page:每页数量，默认20
        :return:成功返回仓库列表，失败返回None
        """
        url=f"{self.BASE_URL}/user/repos"
        params: Dict[str, int] = {"page": page, "per_page": per_page}
        try:
            response = RequestUtil.send_requests("GET", url, headers=self.headers, params=params)
            if response and response.status_code == 200:
                repos=response.json()
                logger.info(f"获取仓库列表成功：共{len(repos)}个")
                return repos
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"获取仓库列表失败：状态码={status}")
                return None
        except Exception as e:
            logger.error(f"获取仓库列表异常：{str(e)}")
            return None
