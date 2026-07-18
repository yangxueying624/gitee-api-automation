import base64
import os
from typing import Optional, Dict
from utils.log import logger
from config import GITEE_TOKEN
from utils.request_util import RequestUtil


class GiteeFileClient:
    BASE_URL: str = "https://gitee.com/api/v5"

    def __init__(self, token: str = GITEE_TOKEN):
        self.token: str = token
        self.headers: Dict[str, str] = {"Authorization": f"token {self.token}"}

    # 查询Gitee仓库中指定路径的文件，获取这个文件的唯一版本标识sha
    def get_file_sha(self, owner: str, repo: str, file_path: str) -> Optional[str]:
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

    # 上传文件到Gitee仓库
    def upload_file(
        self, repo_full_name: str, local_path: str, remote_path: str
    ) -> bool:
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
                将原始二进制数据（file_content）按照 base64编码规则 转为base64格式的二进制数据
                具体规则：
                （1）原始二进制按 6 位一组拆分（不足 6 位补 0）
                （2）每组 6 位二进制对应 0-63 的整数
                （3）通过 base64 密码表（A-Z、a-z、0-9、+、/）映射为字符
                （4）最终得到这些字符对应的二进制（仍为 bytes 类型）
                例：file_content=b'hello经过编码后，得到'b'aGVsbG8='（base64格式的二进制）
    
                .decode("utf-8")做了什么：
                将base64 格式的二进制数据（如 b'aGVsbG8='）按照utf-8编码规则转换为字符串
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

    # 删除仓库中的文件
    def delete_file(self, repo_full_name: str, file_path: str) -> bool:
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
        # 发送删除请求
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
                logger.error(
                    f"删除文件失败！状态码：{response.status_code}，响应：{response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"删除文件异常：{str(e)}")
            return False
