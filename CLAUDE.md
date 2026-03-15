# fastapi-new 项目

FastAPI 项目脚手架工具，用于快速创建生产级的 FastAPI 项目模板。

## 项目概述

这是一个 Python 实现的脚手架工具，通过一条命令即可生成功能完整的 FastAPI 项目。

**项目定位：** 快速启动、简洁易用、面向中小型项目

## 功能特性

该工具会自动创建一个完整的 FastAPI 项目，包含：

| 功能 | 实现方式 |
|------|----------|
| 项目结构 | 标准的分层架构 |
| 日志系统 | 基于 loguru 的彩色日志和文件日志 |
| 配置管理 | 基于 pydantic-settings 的类型安全配置 |
| 测试框架 | 预配置的 pytest 测试环境 |
| API 文档 | 自动生成的 Swagger/ReDoc 文档 |
| 健康检查 | 内置的健康检查端点 |

## 使用方法

### 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Python 包管理工具

### 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 创建项目

```bash
# 确保脚本有执行权限
chmod +x fastapi_new.py

# 创建项目
./fastapi_new.py <项目名称>

# 或使用 Python 运行
python fastapi_new.py <项目名称>
```

### 示例

```bash
./fastapi_new.py my-api
cd my-api
uv sync
uv run fastapi dev
```

## 生成的项目结构

```
项目名/
├── app/
│   ├── api/              # API 路由模块
│   │   ├── __init__.py
│   │   └── health.py     # 健康检查接口
│   ├── core/             # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理（pydantic-settings）
│   │   └── logger.py     # 日志配置（loguru）
│   ├── models/           # 数据模型
│   │   └── __init__.py
│   ├── services/         # 业务服务层
│   │   └── __init__.py
│   ├── utils/            # 工具函数
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py           # FastAPI 应用入口
├── tests/                # 测试文件
│   ├── __init__.py
│   └── test_main.py      # 主应用测试
├── logs/                 # 日志文件目录
├── .env                  # 环境变量配置
├── .gitignore            # Git 忽略文件
├── main.py               # fastapi dev 命令入口
├── pyproject.toml        # uv 项目配置
└── README.md             # 项目说明文档
```

## 核心依赖

### 生产依赖

| 包 | 说明 | 评级 |
|---|------|------|
| fastapi | 现代 Web 框架 | ⭐⭐⭐⭐⭐ |
| uvicorn | ASGI 服务器 | ⭐⭐⭐⭐⭐ |
| loguru | 简单强大的日志库 | ⭐⭐⭐⭐ |
| pydantic-settings | 配置管理 | ⭐⭐⭐⭐⭐ |
| python-multipart | 表单数据支持 | ⭐⭐⭐⭐ |

### 开发依赖

| 包 | 说明 | 评级 |
|---|------|------|
| pytest | 测试框架 | ⭐⭐⭐⭐⭐ |
| pytest-asyncio | 异步测试支持 | ⭐⭐⭐⭐⭐ |
| httpx | HTTP 测试客户端 | ⭐⭐⭐⭐⭐ |

## 技术栈

- **Python 3.10+**
- **FastAPI** - 现代化的 Web 框架
- **uv** - 快速的 Python 包管理器
- **loguru** - 简单强大的日志库
- **pydantic-settings** - 类型安全的配置管理
- **pytest** - 测试框架

## 开发指南

### 添加新的 API 路由

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

### 运行生成的项目

```bash
# 进入项目目录
cd <项目名称>

# 同步依赖
uv sync

# 启动开发服务器（推荐方式）
uv run fastapi dev

# 或指定端口
uv run fastapi dev --port 8080

# 运行测试
uv run pytest
```

## 日志配置

日志系统位于 `app/core/logger.py`，支持：

- 🎨 控制台彩色输出
- 📄 文件日志（`logs/app.log`）
- 🚨 错误日志单独记录（`logs/error.log`）
- 🔄 日志轮转（500MB 自动切割）
- 🗑️ 日志保留（7 天自动清理）

**注意：** loguru 适合快速开发和小型项目。如需生产级结构化日志（OpenTelemetry 支持），可替换为 structlog。

## 环境变量

在 `.env` 文件中配置：

```env
# 应用配置
APP_NAME=My API
APP_VERSION=1.0.0
DEBUG=true

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# API配置
API_PREFIX=/api/v1
```

## 生产部署

```bash
# 使用 gunicorn + uvicorn workers
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用 uvicorn 直接运行
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 代码规范

- ✅ 使用类型注解
- ✅ 遵循 PEP 8 规范
- ✅ 所有注释使用中文
- ✅ 函数和类使用文档字符串

## 维护说明

当修改这个脚手架工具时：

1. **测试生成结果** - 每次修改后生成一个测试项目，确保可以正常运行
2. **更新文档** - 保持 README.md 和 CLAUDE.md 同步更新

## 项目文件

| 文件 | 说明 |
|------|------|
| `fastapi_new.py` | 脚手架主脚本 |
| `README.md` | 项目使用说明 |
| `CLAUDE.md` | Claude AI 指导文档 |

## 设计原则

1. **简洁优先** - 只包含必需的功能，避免过度设计
2. **快速启动** - 一条命令即可开始开发
3. **标准实践** - 遵循 FastAPI 社区最佳实践
4. **易于扩展** - 提供清晰的扩展点
