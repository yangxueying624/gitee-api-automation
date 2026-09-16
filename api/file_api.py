import base64
import os
from typing import Optional, Dict
from utils.log import logger
from config import GITEE_TOKEN
from utils.request_util import RequestUtil
from utils.decorators import retry,api_log

class GiteeFileClient:
    """Gitee文件接口客户端，封装文件上传、删除、查询操作"""
    BASE_URL: str = "https://gitee.com/api/v5"

    def __init__(self, token: str = GITEE_TOKEN):
        self.token: str = token
        self.headers: Dict[str, str] = {"Authorization": f"token {self.token}"}


    @api_log
    @retry(max_retries=2,delay=1.0)
    def get_file_sha(self, owner: str, repo: str, file_path: str) -> Optional[str]:
        """
        查询仓库中文件的唯一标识 sha
        更新或删除文件时必须传入 sha，Gitee用它做版本控制

        :param owner:仓库所有者用户名
        :param repo:仓库名
        :param file_path:仓库内文件路径
        :return:文件存在返回sha字符串，不存在返回None（404），异常返回None
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
        try:
            response = RequestUtil.send_requests("GET", url, headers=self.headers)
            if response and response.status_code == 200:
                old_sha = response.json()["sha"]
                logger.info(f"找到旧文件！sha值：{old_sha}")
                return old_sha
            elif response and response.status_code == 404:
                logger.info(f"未找到旧文件，准备上传新文件")
                return None
            else:
                logger.error(
                    f"查询文件sha失败！状态码：{response.status_code}，响应：{response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"查询文件sha异常：{str(e)}")
            return None


    @api_log
    def upload_file(self, repo_full_name: str, local_path: str, remote_path: str) -> bool:
        """
        上传文件到仓库（创建新文件或更新已有文件）

        base64编码流程：
            本地文件二进制 → base64.b64encode() → base64字节 → .decode("utf-8") → 字符串
            Gitee API 要求文件内容以 base64 字符串格式传入

        :param repo_full_name:仓库完整名
        :param local_path:本地文件路径
        :param remote_path:仓库内目标路径
        :return:成功返回 True，失败返回 False
        """
        try:
            owner, repo = repo_full_name.split("/")
        except Exception as e:
            logger.error(f"仓库完整名格式错误！{str(e)}")
            return False

        old_sha = self.get_file_sha(owner, repo, remote_path)
        if not os.path.exists(local_path):
            logger.info(f"本地文件不存在！路径：{local_path}")
            return False
        try:
            # rb：以二进制只读模式打开文件
            with open(local_path, "rb") as f:
                file_content = f.read()
                """
                file_content:
                是从本地读取的原始二进制数据（类型为bytes） 比如：图片的像素数据，文档的二进制编码，本质就是0、1字节串
                例：若文本是“hello”，则file_content就是b'hello'（Python对二进制的显示形式），实际对应二进制01101000 01100101
    
                base64.b64encode(file_content)：
                将原始二进制数据（file_content）按照base64编码规则 转为base64格式的二进制数据
                具体规则：
                （1）原始二进制按 6 位一组拆分（不足 6 位补 0）
                （2）每组 6 位二进制对应 0-63 的整数
                （3）通过 base64 密码表（A-Z、a-z、0-9、+、/）映射为字符
                （4）最终得到这些字符对应的二进制（仍为 bytes 类型）
                例：file_content=b'hello经过编码后，得到'b'aGVsbG8='（base64格式的二进制）
    
                .decode("utf-8")做了什么：
                将base64格式的二进制数据（如 b'aGVsbG8='）按照utf-8编码规则转换为字符串
                原因：base64编码后的二进制对应的字符均在UTF-8可识别范围内
                例：b'aGVsbG8=' 解码后得到字符串 'aGVsbG8='
                """
                file_base64 = base64.b64encode(file_content).decode("utf-8")
        except Exception as e:
            logger.error(f"读取/编码文件失败！{str(e)}")
            return False

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{remote_path}"
        json_data = {"message": f"Upload file:{remote_path}", "content": file_base64}
        if old_sha is not None:
            json_data["sha"] = old_sha
        try:
            response = RequestUtil.send_requests(
                "POST", url, json=json_data, headers=self.headers
            )
            if response and response.status_code in [200, 201]:
                logger.info(
                    f"文件上传成功！仓库路径：{remote_path}，状态码：{response.status_code}"
                )
                return True
            else:
                logger.error(
                    f"文件上传失败！状态码：{response.status_code}，响应：{response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"上传文件异常：{str(e)}")
            return False


    @api_log
    def delete_file(self, repo_full_name: str, file_path: str) -> bool:
        """
        删除仓库中的文件（需要先查询sha值才能删除）

        :param repo_full_name:仓库完整名
        :param file_path:仓库内文件路径
        :return:成功返回True，失败返回False
        """
        try:
            owner, repo = repo_full_name.split("/")
        except Exception as e:
            logger.error(f"仓库完整名格式错误！{str(e)}")
            return False

        # 先查询文件sha
        old_sha = self.get_file_sha(owner, repo, file_path)
        if old_sha is None:
            logger.error(f"文件不存在或查询sha失败，无法删除")
            return False

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
        json_data = {"message": f"Delete file: {file_path}", "sha": old_sha}
        try:
            response = RequestUtil.send_requests(
                "DELETE", url, json=json_data, headers=self.headers
            )
            if response and response.status_code == 200:
                logger.info(f"删除文件成功！文件路径：{file_path}")
                return True
            else:
                status = response.status_code if response else "无响应"
                logger.error(f"删除文件失败！状态码：{status}，响应：{response.text}")
                return False
        except Exception as e:
            logger.error(f"删除文件异常：{str(e)}")
            return False
