import requests
from config import GITEE_TOKEN,TIMEOUT
from utils.log import logger

# 创建仓库
def create_gitee_repo(repo_name,repo_desc):
    create_url="https://gitee.com/api/v5/user/repos"
    headers={"Authorization": f"token {GITEE_TOKEN}"}
    json_data={
        "name": repo_name,
        "description": repo_desc
    }
    try:
        response=requests.post(url=create_url,headers=headers,json=json_data)
        if response.status_code == 201:
            repo_full_name=response.json()["full_name"]
            logger.info(f"✅ 创建仓库成功！仓库名：{repo_full_name}")
            return repo_full_name
        else:
            logger.error(f"❌ 创建仓库失败！状态码：{response.status_code}，响应：{response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ 创建仓库异常：{str(e)}")
        return None

# 查询仓库信息
def get_gitee_repo_info(repo_full_name):
    get_url=f"https://gitee.com/api/v5/repos/{repo_full_name}"
    headers={"Authorization": f"token {GITEE_TOKEN}"}
    try:
        response=requests.get(url=get_url,headers=headers,timeout=TIMEOUT)
        if response.status_code == 200:
            repo_info=response.json()
            logger.info(f"✅ 查询仓库信息成功！仓库名：{repo_info['full_name']}")
            return repo_info
        else:
            logger.error(f"查询仓库信息失败！状态码：{response.status_code}，响应：{response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ 查询仓库信息异常：{str(e)}")
        return None


# 删除仓库
def delete_gitee_repo(repo_full_name):
    delete_url=f"https://gitee.com/api/v5/repos/{repo_full_name}"
    headers={"Authorization": f"token {GITEE_TOKEN}"}
    try:
        response=requests.delete(url=delete_url,headers=headers,timeout=TIMEOUT)
        if response.status_code == 204:
            logger.info(f"✅ 删除仓库成功！仓库名：{repo_full_name}")
            return True
        else:
            logger.error(f"❌ 删除仓库失败！状态码：{response.status_code}，响应：{response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ 删除仓库异常：{str(e)}")
        return False

