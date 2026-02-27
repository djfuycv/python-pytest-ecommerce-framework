# 🛒 电商接口自动化测试框架 (E-commerce Auto Test Framework)

基于 **Python + Pytest + Requests + Allure** 搭建的分层自动化测试框架。旨在通过数据驱动、业务解耦和深层数据校验，提升回归测试效率与质量。

## 🌟 核心亮点
- **分层架构设计**: 严格遵循 `Config` (配置), `Utils` (工具), `API` (接口封装), `TestCases` (用例), `Data` (数据) 分层，实现高内聚低耦合。
- **数据驱动测试**: 使用 `YAML` 管理测试数据，结合 `@pytest.mark.parametrize` 实现用例与数据分离，易于维护。
- **深层数据一致性校验**: 不仅校验接口返回码，更通过 **Mock DB/Redis** 机制校验数据库状态（如登录失败次数累加），有效发现“假成功”Bug。
- **智能 Fixture 管理**: 利用 `conftest.py` 和 `scope=session` 实现全局 Token 共享，避免重复登录触发风控。
- **可视化报告**: 集成 `Allure` 生成详细测试报告，包含请求参数、响应结果及日志步骤。

## 📂 项目结构
```bash
ecommerce_auto_test/
├── config/                # 环境配置层（多环境切换/全局参数）
│   └── env_config.py      # 环境变量、超时时间、接口基础地址等配置
├── utils/                 # 通用工具层（复用性强，与业务解耦）
│   ├── request_util.py    # HTTP请求封装（超时、重试、请求/响应日志）
│   ├── redis_util.py      # Mock Redis工具（Token缓存、缓存清理）
│   ├── db_util.py         # Mock DB工具（用户数据查询、失败次数更新）
│   └── log_util.py        # 日志配置（分级输出、格式标准化）
├── api/                   # 接口封装层（业务逻辑抽象）
│   └── login_api.py       # 登录接口封装（缓存校验、DB验证、Token生成）
├── testcases/             # 测试用例层（数据驱动，仅存测试逻辑）
│   ├── conftest.py        # Pytest夹具（全局Token、自动缓存清理）
│   └── test_login.py      # 登录场景用例（正向/反向/边界全覆盖）
├── data/                  # 测试数据层（YAML管理，与用例分离）
│   └── test_data.yaml     # 登录测试数据（正常登录/密码错误/超长密码等）
├── report/                # 测试报告层（Allure原始数据+静态HTML）
│   └── allure_report      # Allure原始报告数据
├── log/                   # 运行日志（自动生成，便于问题排查）
├── .gitignore             # Git忽略配置（排除虚拟环境、报告、日志等）
├── requirements.txt       # 依赖清单（版本锁定，保证环境一致性）
├── run.py                 # 执行入口（一键运行、结果提示、异常捕获）
└── README.md              # 项目说明文档（快速上手、核心亮点、结构说明）