from api.file_api import GiteeFileClient
from utils.log import logger


# 测试文件上传 → 删除的流程
def test_file_upload_verify(
    file_client: GiteeFileClient, upload_file: str, created_repo: str
) -> None:
    owner, repo = created_repo.split("/")
    file_sha = file_client.get_file_sha(owner, repo, upload_file)
    assert file_sha is not None, f"上传失败，服务器上未找到{upload_file}文件"
    logger.info(f"文件上传成功！文件sha{file_sha}")
