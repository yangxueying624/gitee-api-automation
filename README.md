# Gitee 接口自动化实战

本项目以 Gitee OpenAPI 作为被测服务，实现一套完整的接口自动化实现，包含请求封装、日志埋点、失败重试、契约校验、异常 Mock、多格式数据驱动与持续集成。

---

## 一、项目关注的工程问题

项目实现过程重点处理接口自动化中常见的工程问题：

1. 请求、鉴权、日志逻辑散落于用例，带来后期维护负担
2. 网络波动、第三方服务不稳定造成流水线随机失败
3. 敏感配置管理不当，配置缺失产生隐晦报错，增加排查成本
4. 接口字段发生静默变更，单纯依靠业务断言难以感知
5. 服务异常、超时、权限类场景难以在线上稳定复现，无法固化为回归用例

---

## 二、运行效果

日志、重试、契约校验组件实际输出示例：

```text
INFO  - [api_log] >>> create_repo 调用 | 参数=('test-repo-001',)
INFO  - [api_log] <<< create_repo 完成 | 耗时=0.82秒
WARN  - [重试] create_repo 第1次返回None，判定失败
INFO  - [重试] create_repo 第2次重试成功
INFO  - [schema] 校验通过：TC001 get_repo_info 返回
```

Mock 异常用例可完全脱离网络运行，适合作为代码提交触发的快速回归集：

```text
$ pytest testcases/test_mock.py -q
...........                                          [100%]
11 passed in 1.75s
```

---

## 三、核心设计与能力

| 模块能力 | 设计思路、约束与收益 |
| --- | --- |
| **分层职责隔离** | api 层仅负责 HTTP 请求组装，业务断言收敛在 testcases 用例层；同一 API 客户端支持多组用例复用，降低维护成本。 |
| **非侵入式增强组件** | `@api_log` 请求日志埋点；`@retry` 失败重试。约束：重试仅用于幂等 GET 查询接口；POST 写接口不启用，避免网络抖动产生重复资源。 |
| **JSON-Schema 契约校验** | 校验响应报文结构，定位异常字段路径，捕获字段删除、类型变更等不易察觉的接口改动。 |
| **Mock 用例分层执行** | requests-mock 模拟 500、超时、403、404 等异常。Mock 用例离线执行，用于 CI 快速冒烟；真实接口用例受第三方服务限制，适合定时调度执行，缓解流水线随机失败。 |
| **多格式数据驱动** | 支持 Excel / YAML / JSON 测试数据源自动解析；多格式并行可发现字段命名不一致问题。 |
| **配置安全容错** | Token 通过 `.env` 环境变量管理，不纳入版本库；关键配置缺失抛出明确异常，规避迷惑性 401 鉴权报错。 |
| **持续集成流水线** | GitHub-Actions 自动执行测试；requirements.txt 锁定依赖版本，消除本地与 CI 环境差异。 |

---

## 四、新增用例工作流

基于本项目新增接口测试用例遵循如下流程：

1. **接口封装**：在 `api/` 下封装业务 Client 方法，仅处理 URL、Header、参数组装，不实现断言。
2. **契约定义**：在 `schemas/` 编写 JSON-Schema，定义接口返回数据约束。
3. **准备测试数据**：在 `data/` 维护输入测试数据，支持 Excel / YAML / JSON。
4. **编写业务用例**：在 `testcases/` 编写 pytest 用例，调用 API 客户端，完成业务断言与 schema 契约校验。
5. **异常场景（可选）**：故障类场景可通过 Mock 实现离线用例，纳入快速回归集。

---

## 五、项目目录

```text
Gitee_api_test/
├── api/                  # API业务客户端层，封装接口请求逻辑
├── utils/                # 通用工具：请求封装、装饰器、schema校验、数据解析、日志组件
├── testcases/            # pytest用例、fixture、业务断言逻辑
├── schemas/              # JSON-Schema接口契约定义
├── data/                 # 多格式测试数据集
├── config.py             # 配置加载：.env优先，config.yaml兜底
├── config.yaml           # 非敏感业务配置
├── .env.example          # 环境变量配置模板
├── mypy.ini              # mypy静态类型检查配置
├── requirements.txt      # 锁定项目依赖版本
└── DESIGN.md             # 架构取舍、实现细节与问题复盘
```

---

## 六、快速上手

> 环境要求：Python >= 3.10

```bash
# 拉取代码
git clone https://github.com/yangxueying624/gitee-api-automation.git
cd Gitee_api_test

# 安装依赖
pip install -r requirements.txt

# 配置鉴权
# 复制 .env.example 为 .env，填入 Gitee 私人令牌

# 执行测试
pytest testcases/ -v                  # 执行全部用例
pytest testcases/test_mock.py -v      # 离线Mock冒烟，无需token、断网可运行
```

日志同时输出至控制台与 `logs/` 目录，日志文件按日期切割。

---

## 七、技术栈

`Python3.11` `pytest` `requests` `requests-mock` `jsonschema` `PyYAML` `openpyxl` `python-dotenv` `mypy` `GitHub Actions`
