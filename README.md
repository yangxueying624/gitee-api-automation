# Gitee 接口自动化测试框架

基于 **Python + pytest** 的接口自动化测试框架，覆盖请求封装、日志埋点、失败重试、契约校验、异常 Mock、多格式数据驱动与持续集成。


## 一、设计目标

搭建时就瞄准接口测试中的三个共性难点，逐项对应解法：

| 目标问题 | 解法 |
|---|---|
| 重复回归枯燥易漏 | 用例脚本化，一条命令跑完 |
| 500 / 超时 / 无权限等异常难以稳定复现 | `requests-mock` 主动构造异常 |
| 接口改字段下游才发现 | JSON Schema 契约校验，结构变化立即失败 |

---

## 二、实际效果

真实运行日志（`@api_log` 与 `@retry` 均在实际工作）：

```text
INFO  - [api_log] >>> create_repo 调用 | 参数=('test-repo-001',)
INFO  - [api_log] <<< create_repo 完成 | 耗时=0.82秒
WARN  - [重试] create_repo 第1次返回None，判定失败
INFO  - [重试] create_repo 第2次重试成功
INFO  - [schema] 校验通过：TC001 get_repo_info 返回
```

异常场景用例脱离网络运行：

```text
$ pytest testcases/test_mock.py -q
...........                                          [100%]
11 passed in 1.75s
```

**断网状态下结果相同** —— 这批用例不依赖外部服务，适合作为提交即触发的快速回归。

---

## 三、核心特性

| 特性 | 实现 |
|---|---|
| **五层分离** | `api` 业务层 · `utils` 技术层 · `testcases` 用例层 · `schemas` 契约层 · `data` 数据层 |
| **装饰器横切** | 自研 `@api_log`（埋点）与 `@retry`（重试），业务代码零侵入 |
| **契约校验** | JSON Schema 定义返回结构，`e.absolute_path` 精确定位出错字段 |
| **异常 Mock** | 覆盖 500 / 超时 / 403 / 404 / 空列表 |
| **三格式数据驱动** | Excel / YAML / JSON，按后缀自动分发 |
| **敏感信息隔离** | token 存 `.env`，配置缺失时快速失败 |
| **持续集成** | GitHub Actions 自动执行 |

---


## 四、目录结构

```
Gitee_api_test/
├── api/                  # 业务层：按业务域封装 Client 类
│   ├── repo_api.py       #   仓库：创建/查询/更新/删除/列表
│   └── file_api.py       #   文件：查询 sha/上传/删除
├── utils/                # 技术层：与业务无关的通用能力
│   ├── request_util.py   #   requests 统一封装
│   ├── decorators.py     #   @api_log / @retry
│   ├── schema_util.py    #   JSON Schema 校验
│   ├── data_util.py      #   三格式数据读取（策略模式）
│   └── log.py            #   日志：文件按天切分 + 控制台
├── testcases/
│   ├── conftest.py       #   fixture：session 级 Client / function 级数据
│   ├── test_repo.py      #   数据驱动用例
│   ├── test_file.py      #   文件上传验证
│   └── test_mock.py      #   Mock 异常场景（断网可跑）
├── schemas/              # 契约层
│   ├── repo_schema.py
│   └── user_schema.py
├── data/                 # xlsx / yaml / json 三份同源数据
├── config.py             # .env 优先，config.yaml 兜底
├── mypy.ini              # 静态类型检查
└── DESIGN.md             # 设计决策与踩坑复盘
```

---

## 五、快速开始

```bash
# 1. 安装依赖（已锁版本）
pip install -r requirements.txt

# 2. 配置 token（根目录创建 .env，参考 .env.example）
GITEE_TOKEN=你的Gitee私人令牌

# 3. 执行
pytest testcases/ -v                  # 全部用例
pytest testcases/test_mock.py -v      # 仅 Mock，无需 token，断网可跑
```

日志同时输出到控制台与 `logs/` 目录，文件按日期命名。

---

## 六、技术栈

Python 3.11 · pytest · requests · requests-mock · jsonschema · PyYAML · openpyxl · python-dotenv · mypy · GitHub Actions

---
