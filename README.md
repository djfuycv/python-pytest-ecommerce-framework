# 电商自动化测试框架
基于 Python + Pytest 构建的电商自动化测试框架，覆盖登录、商品核心业务场景，支持 Mock 环境/真实环境切换、数据驱动、Allure 报告生成，代码结构清晰、易扩展。

## 📋 项目特点
- 分层设计：API 层、Mock 层、测试层分离，符合软件工程最佳实践
- 环境适配：支持 Mock 环境（快速执行）/ 真实环境（接口验证）一键切换
- 数据驱动：YAML 管理测试用例，参数化执行，易维护
- 工具封装：统一的请求工具、日志工具、配置工具，降低重复代码
- 报告完善：支持 Allure 生成可视化测试报告，便于问题定位

## 📂 目录结构
```
ecommerce_auto_test/
├── .gitignore              # Git 忽略规则（排除冗余/敏感文件）
├── run.py                  # 测试执行入口（一键运行+生成报告）
├── config/                 # 环境配置目录
│   └── env_config.py       # 环境变量、URL、超时等配置
├── api/                    # 接口层（封装业务接口）
│   ├── login_api.py        # 登录接口封装
│   └── product_api.py      # 商品接口封装（列表/详情/创建/库存扣减）
├── mock/                   # Mock 层（模拟业务逻辑，脱离真实环境）
│   ├── login_mock.py       # 登录 Mock 数据/逻辑
│   └── product_mock.py     # 商品 Mock 数据/逻辑
├── testcases/              # 测试用例层
│   ├── conftest.py         # Pytest 夹具（前置/后置操作）
│   ├── test_login.py       # 登录模块测试用例
│   └── test_product.py     # 商品模块测试用例
├── utils/                  # 工具层（通用能力封装）
│   ├── request_util.py     # HTTP 请求工具（Session 复用、参数分离）
│   ├── log_util.py         # 日志工具（统一日志格式）
│   ├── data_util.py        # 数据工具（加载 YAML 用例）
│   └── db_util.py          # 数据库工具（可选，真实环境用）
└── data/                   # 测试数据层
    ├── test_login.yaml     # 登录测试用例数据
    └── test_product.yaml   # 商品测试用例数据
```


## 🚀 快速开始
### 1. 环境准备
#### 1.1 安装依赖
conda activate test_env
pip install -r requirements.txt

#### 1.2 依赖清单（requirements.txt）
pytest>=9.0.2
requests>=2.31.0
PyYAML>=6.0.1
python-dotenv>=1.0.0
allure-pytest>=2.15.3
pytest-html>=4.2.0

#### 1.3 配置环境变量
在项目根目录创建 .env 文件（不上传 Git），配置基础信息：
AUTO_ENV=test
AUTO_IS_MOCK=True
TEST_BASE_URL=https://httpbin.org
AUTO_TIMEOUT=10

### 2. 执行测试
#### 2.1 一键运行所有用例（推荐）
python run.py

#### 2.2 单独运行指定模块
pytest testcases/test_login.py -v
pytest testcases/test_product.py -v

#### 2.3 查看 Allure 报告
allure open report/html

## 🧪 核心测试场景
### 登录模块
| 用例场景                | 验证点                          |
|-------------------------|---------------------------------|
| 正确密码登录-复用 Token | Token 复用、失败次数重置、状态校验 |
| 错误密码登录-失败次数+1 | 失败次数累加、错误码/提示语匹配  |
| 失败5次-账号锁定        | 账号锁定逻辑、状态流转           |
| 超长密码登录-安全校验    | 密码长度校验、安全断言           |

### 商品模块
| 用例场景                | 验证点                          |
|-------------------------|---------------------------------|
| 查询存在商品-正常在售    | 商品详情返回、状态校验           |
| 查询不存在商品          | 404 错误码/提示语匹配           |
| 扣减库存-库存充足        | 库存扣减逻辑、剩余库存校验       |
| 扣减库存-库存不足        | 400 错误码/提示语匹配           |
| 创建商品-正常创建        | POST 请求参数、创建结果校验      |

## 🔧 扩展指南
### 新增业务模块（如订单模块）
1. 在 mock/ 下创建 order_mock.py（模拟订单业务逻辑）
2. 在 api/ 下创建 order_api.py（封装订单接口）
3. 在 data/ 下创建 test_order.yaml（编写订单测试用例）
4. 在 testcases/ 下创建 test_order.py（编写订单测试脚本）

### 切换环境
- Mock 环境（默认）：.env 中 AUTO_IS_MOCK=True，跳过真实接口调用，快速执行
- 真实环境：.env 中 AUTO_IS_MOCK=False，调用真实接口，验证端到端流程

## 📌 注意事项
1. .env 文件包含敏感配置（如 URL、Token），请勿提交到 Git
2. __pycache__/、log/、report/ 等冗余文件已加入 .gitignore，无需手动删除
3. 执行 Allure 报告需提前安装 allure-commandline 工具

## 🛠️ 问题排查
- 接口调用失败：检查 config/env_config.py 中 BASE_URL 是否正确
- Mock 数据不生效：确认 .env 中 AUTO_IS_MOCK=True
- 报告生成失败：检查 allure-commandline 是否安装并配置到环境变量


'''
想验证电商自动化项目的持续集成能力
'''