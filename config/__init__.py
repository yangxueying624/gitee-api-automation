import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# BASE_DIR是项目根目录的路径对象（pathlib.Path类型，不是普通字符串）
BASE_DIR = Path(__file__).parent.parent
# 拼接出根目录下.env的完整路径，强制读取，不受控制台/脚本启动目录影响
load_dotenv(dotenv_path=BASE_DIR / ".env")
def load_config() -> Dict[str, Any]:
    """
    加载config.yaml配置文件
    :return:配置字典，结构如{"gitee": {"token": "abc123", "timeout": 10}}
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    # with会自动关闭文件，不用手写会 f.close()，避免资源泄漏
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config: Dict[str, Any] = load_config()
# 优先读取环境变量，取不到再读取config.yaml里面的token兜底
# os.getenv(变量名，默认值)   当.env文件内未定义GITEE_TOKEN时，自动取用config.yaml内的token作为备用值
GITEE_TOKEN: str = os.getenv("GITEE_TOKEN",config["gitee"]["token"])

if not GITEE_TOKEN:
    raise RuntimeError("未配置 GITEE_TOKEN：请在项目根目录创建 .env 文件（参考 .env.example）")

# 超时时间属于无敏感公开配置，直接从yaml读取，无需放入.env
TIMEOUT: int = config["gitee"]["timeout"]