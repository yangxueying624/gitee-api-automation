import yaml
import os
def load_config():
    # 找到config.yaml文件
    config_path=os.path.join(os.path.dirname(__file__),"config.yaml")
    with open(config_path,"r",encoding="utf-8") as f:
        # 把yaml文件里的内容，转成Python能识别的字典
        return yaml.safe_load(f)   # {"gitee": {"token": "abc123", "timeout": 10}}

config=load_config()
GITEE_TOKEN=config["gitee"]["token"]
TIMEOUT=config["gitee"]["timeout"]