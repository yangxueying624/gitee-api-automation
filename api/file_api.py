import requests
import base64
import os
from utils.log import logger
from config import GITEE_TOKEN,TIMEOUT

# 获取仓库具体路径下的内容
def get_old_file_sha(owner,repo,repo_file_path):
    get_url=f"https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{repo_file_path}"
    headers = {"Authorization": f"token {GITEE_TOKEN}"}
    try:
        response=requests.get(url=get_url, headers=headers,timeout=TIMEOUT)
        if response.status_code == 200:
            old_sha=response.json()["sha"]
            logger.info(f"✅ 找到旧文件！sha值：{old_sha}")
            return old_sha
        elif response.status_code == 404:
            logger.info(f"ℹ️ 未找到旧文件，准备上传新文件")
            return None
        else:
            logger.error(f"❌ 查询文件sha失败！状态码：{response.status_code}，响应：{response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ 查询文件sha异常：{str(e)}")
        return None


# 上传文件到Gitee仓库
def upload_file_to_repo(repo_full_name,local_file_path,repo_file_path):
    try:
        owner,repo=repo_full_name.split("/")
    except Exception as e:
        logger.error(f"❌ 仓库完整名格式错误！{str(e)}")
        return False
    old_sha=get_old_file_sha(owner,repo,repo_file_path)
    if not os.path.exists(local_file_path):   # 判断本地文件是否存在
        logger.info(f"❌ 本地文件不存在！路径：{local_file_path}")
        return False
    try:
        with open(local_file_path,"rb") as f:
            file_content=f.read()
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
            file_base64=base64.b64encode(file_content).decode("utf-8")
    except Exception as e:
        logger.error(f"❌ 读取/编码文件失败！{str(e)}")
        return False

    upload_url=f"https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{repo_file_path}"
    headers={"Authorization": f"token {GITEE_TOKEN}"}
    json_data={
        "message":f"Upload file:{repo_file_path}",
        "content":file_base64
    }
    if old_sha is not None:
        json_data["sha"]=old_sha
    try:
        response=requests.post(url=upload_url, json=json_data, headers=headers, timeout=TIMEOUT)
        if response.status_code in [200,201]:
            logger.info(f"✅ 文件上传成功！仓库路径：{repo_file_path}，状态码：{response.status_code}")
            return True
        else:
            logger.error(f"❌ 文件上传失败！状态码：{response.status_code}，响应：{response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ 上传文件异常：{str(e)}")
        return False


# 删除仓库中的文件
def delete_gitee_file(repo_full_name,repo_file_path):
    try:
        owner,repo=repo_full_name.split("/")
    except Exception as e:
        logger.error(f"❌ 仓库完整名格式错误！{str(e)}")
        return False
    # 先查询文件sha
    old_sha=get_old_file_sha(owner,repo,repo_file_path)
    if old_sha is None:
        logger.error(f"❌ 文件不存在或查询sha失败，无法删除")
        return False
    # 发送删除请求
    delete_url=f" https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{repo_file_path}"
    headers={"Authorization": f"token {GITEE_TOKEN}"}
    json_data={
        "message": f"Delete file: {repo_file_path}",
        "sha": old_sha
    }
    try:
        response=requests.delete(url=delete_url, json=json_data, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            logger.info(f"✅ 删除文件成功！文件路径：{repo_file_path}")
            return True
        else:
            logger.error(f"❌ 删除文件失败！状态码：{response.status_code}，响应：{response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ 删除文件异常：{str(e)}")
        return False