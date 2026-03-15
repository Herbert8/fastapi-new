# fastapi-new

> FastAPI 项目脚手架工具 - 快速创建生产级 FastAPI 项目模板

一个 Python 脚本，用于快速初始化功能完整的 FastAPI 项目，集成了日志管理、配置管理、测试框架等最佳实践。

## 功能特性

- ⚡ **快速初始化** - 一条命令创建完整的项目结构
- 📦 **依赖管理** - 使用 uv 现代化包管理工具
- 📝 **日志系统** - 集成 loguru，支持控制台彩色输出和文件日志
- ⚙️ **配置管理** - 基于 pydantic-settings 的类型安全配置
- 🧪 **测试框架** - 预配置 pytest 和测试基础设施
- 📚 **API 文档** - 自动生成 Swagger/ReDoc 文档
- 🔧 **健康检查** - 内置健康检查 API 端点

## 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Python 包管理工具

### 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 使用方法

### 基本用法

```bash
./fastapi_new.py <项目名称>
```

### 示例

```bash
# 创建一个名为 my-api 的项目
./fastapi_new.py my-api

# 进入项目目录
cd my-api

# 同步依赖
uv sync

# 启动开发服务器
uv run fastapi dev
```

## 生成的项目结构

```
项目名/
├── app/
│   ├── api/              # API 路由模块
│   │   └── health.py     # 健康检查接口
│   ├── core/             # 核心模块
│   │   ├── config.py     # 配置管理（pydantic-settings）
│   │   └── logger.py     # 日志配置（loguru）
│   ├── models/           # 数据模型
│   ├── services/         # 业务服务层
│   ├── utils/            # 工具函数
│   └── main.py           # FastAPI 应用入口
├── tests/                # 测试文件
│   └── test_main.py      # 主应用测试
├── logs/                 # 日志文件目录
├── .env                  # 环境变量配置
├── .gitignore            # Git 忽略文件
├── main.py               # fastapi dev 命令入口
├── pyproject.toml        # uv 项目配置
└── README.md             # 项目说明文档
```

## 已安装的依赖

### 核心依赖

| 包 | 说明 |
|---|---|
| fastapi | 现代 Web 框架 |
| uvicorn | ASGI 服务器 |
| loguru | 简单强大的日志库 |
| pydantic-settings | 配置管理 |
| python-multipart | 表单数据支持 |

### 开发依赖

| 包 | 说明 |
|---|---|
| pytest | 测试框架 |
| pytest-asyncio | 异步测试支持 |
| httpx | HTTP 测试客户端 |

## 生成的项目特性

### 1. 日志系统

使用 loguru 配置的日志系统，支持：

- 🎨 控制台彩色输出
- 📄 文件日志（`logs/app.log`）
- 🚨 错误日志单独记录（`logs/error.log`）
- 🔄 日志轮转（500MB 自动切割）
- 🗑️ 日志保留（7 天自动清理）

### 2. 配置管理

基于 pydantic-settings 的类型安全配置：

- 支持环境变量
- 支持 .env 文件
- 类型验证和自动转换
- 单例模式缓存

### 3. API 端点

默认提供以下端点：

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |
| `/redoc` | GET | ReDoc 文档 |

### 4. 全局异常处理

自动捕获未处理的异常，返回统一格式的错误响应。

### 5. CORS 中间件

预配置跨域资源共享支持（生产环境需调整）。

## 快速开始指南

创建项目后的操作流程：

```bash
# 1. 进入项目目录
cd my-api

# 2. 同步依赖
uv sync

# 3. 启动开发服务器（推荐方式）
uv run fastapi dev

# 或指定端口
uv run fastapi dev --port 8080

# 4. 访问 API 文档
open http://localhost:8000/docs

# 5. 运行测试
uv run pytest

# 6. 查看详细测试输出
uv run pytest -v
```

## 添加新的 API 路由

```python
# 1. 在 app/api/ 目录下创建新路由
# app/api/users.py
from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()

@router.get("/users")
async def get_users():
    logger.debug("获取用户列表")
    return {"users": []}

# 2. 在 app/main.py 中注册路由
from app.api import users
app.include_router(users.router, prefix="/api/v1", tags=["users"])
```

## 生产部署

```bash
# 使用 gunicorn + uvicorn workers
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用 uvicorn 直接运行
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 环境变量配置

在 `.env` 文件中配置：

```env
# 应用配置
APP_NAME=My API
APP_VERSION=1.0.0
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# API配置
API_PREFIX=/api/v1
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 生成的项目模板包含默认的 CORS 配置允许所有来源，生产环境中请务必限制为可信域名。
