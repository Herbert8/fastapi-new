#!/usr/bin/env python3
"""
FastAPI项目创建脚本

用法: python fastapi_new.py <项目名称>
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal


# ANSI 颜色代码
class Colors:
    """终端颜色定义"""
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str = Colors.NC) -> None:
    """打印带颜色的消息

    Args:
        message: 要打印的消息
        color: 颜色代码
    """
    print(f"{color}{message}{Colors.NC}")


def run_command(
    command: list[str],
    check: bool = True,
    cwd: str | Path | None = None
) -> subprocess.CompletedProcess[str]:
    """运行shell命令

    Args:
        command: 命令列表
        check: 是否检查返回码
        cwd: 工作目录

    Returns:
        命令执行结果
    """
    return subprocess.run(command, check=check, text=True, cwd=str(cwd) if cwd else None)


def check_uv_installed() -> bool:
    """检查uv是否已安装

    Returns:
        uv是否已安装
    """
    return shutil.which("uv") is not None


def create_project_structure(project_dir: Path) -> None:
    """创建项目目录结构

    Args:
        project_dir: 项目根目录
    """
    print_colored("[4/8] 创建项目结构...", Colors.GREEN)
    directories = [
        project_dir / "app" / "api",
        project_dir / "app" / "core",
        project_dir / "app" / "models",
        project_dir / "app" / "services",
        project_dir / "app" / "utils",
        project_dir / "tests",
        project_dir / "logs",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def create_logger_config(project_dir: Path) -> None:
    """创建日志配置文件

    Args:
        project_dir: 项目根目录
    """
    print_colored("[5/8] 创建日志配置...", Colors.GREEN)

    logger_content = '''"""日志配置模块"""
import sys
from pathlib import Path
from loguru import logger as loguru_logger


def setup_logger(
    log_level: str = "INFO",
    log_file: str = "logs/app.log",
    rotation: str = "500 MB",
    retention: str = "7 days"
) -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        rotation: 日志轮转大小
        retention: 日志保留时间
    """
    # 移除默认处理器
    loguru_logger.remove()

    # 控制台输出 - 带颜色
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # 文件输出 - 详细日志
    loguru_logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    # 错误日志单独文件
    error_log_file = str(Path(log_file).parent / "error.log")
    loguru_logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )


# 导出logger实例
logger = loguru_logger
'''

    (project_dir / "app" / "core" / "logger.py").write_text(logger_content, encoding="utf-8")


def create_config_file(project_dir: Path, project_name: str) -> None:
    """创建配置文件

    Args:
        project_dir: 项目根目录
        project_name: 项目名称
    """
    print_colored("[6/8] 创建配置文件...", Colors.GREEN)

    # 创建 config.py
    config_content = '''"""应用配置模块"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "FastAPI Application"
    app_version: str = "1.0.0"
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # API配置
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
'''

    (project_dir / "app" / "core" / "config.py").write_text(config_content, encoding="utf-8")

    # 创建 .env
    env_content = f'''# 应用配置
APP_NAME={project_name}
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
'''

    (project_dir / ".env").write_text(env_content, encoding="utf-8")


def create_main_app(project_dir: Path) -> None:
    """创建主应用文件

    Args:
        project_dir: 项目根目录
    """
    print_colored("[7/8] 创建主应用文件...", Colors.GREEN)

    # 创建 app/main.py
    main_content = '''"""FastAPI主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import logger, setup_logger
from app.api import health

# 获取配置
settings = get_settings()

# 设置日志
setup_logger(log_level=settings.log_level, log_file=settings.log_file)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["health"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    logger.info(f"📖 文档地址: http://{settings.host}:{settings.port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"👋 {settings.app_name} 正在关闭...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )
'''

    (project_dir / "app" / "main.py").write_text(main_content, encoding="utf-8")

    # 创建根目录的 main.py（用于 fastapi dev 命令）
    entry_content = '''"""项目入口文件 - 用于 fastapi dev 命令"""
from app.main import app

# 导出app实例供fastapi CLI使用
__all__ = ["app"]
'''

    (project_dir / "main.py").write_text(entry_content, encoding="utf-8")


def create_health_check(project_dir: Path) -> None:
    """创建健康检查路由

    Args:
        project_dir: 项目根目录
    """
    health_content = '''"""健康检查API"""
from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    logger.debug("健康检查请求")
    return {
        "status": "healthy",
        "message": "服务运行正常"
    }
'''

    (project_dir / "app" / "api" / "health.py").write_text(health_content, encoding="utf-8")


def create_init_files(project_dir: Path) -> None:
    """创建各模块的 __init__.py 文件

    Args:
        project_dir: 项目根目录
    """
    init_files = {
        project_dir / "app" / "__init__.py": '"""应用包"""',
        project_dir / "app" / "api" / "__init__.py": '"""API路由模块"""',
        project_dir / "app" / "core" / "__init__.py": '"""核心模块"""',
        project_dir / "app" / "models" / "__init__.py": '"""数据模型模块"""',
        project_dir / "app" / "services" / "__init__.py": '"""业务服务模块"""',
        project_dir / "app" / "utils" / "__init__.py": '"""工具模块"""',
        project_dir / "tests" / "__init__.py": '"""测试模块"""',
    }

    for file_path, content in init_files.items():
        file_path.write_text(content, encoding="utf-8")


def create_test_files(project_dir: Path) -> None:
    """创建测试文件

    Args:
        project_dir: 项目根目录
    """
    print_colored("[8/8] 创建测试文件...", Colors.GREEN)

    test_content = '''"""主应用测试"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """测试客户端fixture"""
    return TestClient(app)


def test_health_check(client):
    """测试健康检查接口"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data


def test_docs_available(client):
    """测试文档是否可访问"""
    response = client.get("/docs")
    assert response.status_code == 200
'''

    (project_dir / "tests" / "test_main.py").write_text(test_content, encoding="utf-8")


def create_readme(project_dir: Path, project_name: str) -> None:
    """创建 README.md 文件

    Args:
        project_dir: 项目根目录
        project_name: 项目名称
    """
    readme_content = f'''# {project_name}

FastAPI 项目模板，集成 loguru 日志框架。

## 项目结构

```
{project_name}/
├── app/
│   ├── api/          # API路由
│   ├── core/         # 核心模块（配置、日志等）
│   ├── models/       # 数据模型
│   ├── services/     # 业务服务
│   ├── utils/        # 工具函数
│   └── main.py       # 应用入口
├── tests/            # 测试文件
├── logs/             # 日志文件目录
├── main.py           # fastapi dev 命令入口
├── .env              # 环境变量配置
├── pyproject.toml    # 项目配置
└── README.md         # 项目说明
```

## 快速开始

### 安装依赖

```bash
uv sync
```

### 运行开发服务器

**推荐方式 - 使用 fastapi dev:**

```bash
uv run fastapi dev
```

**或者指定端口:**

```bash
uv run fastapi dev --port 8080
```

**传统方式 - 使用 uvicorn:**

```bash
uv run uvicorn app.main:app --reload
```

### 运行测试

```bash
uv run pytest
```

### 查看API文档

启动服务后访问: http://localhost:8000/docs

## 日志配置

日志由 `loguru` 管理，配置位于 `app/core/logger.py`。

- 日志文件: `logs/app.log`
- 错误日志: `logs/error.log`
- 日志轮转: 500MB
- 日志保留: 7天

## 环境变量

在 `.env` 文件中配置：

```
APP_NAME=Your App Name
DEBUG=true
LOG_LEVEL=INFO
```

## 开发

添加新的API路由:

1. 在 `app/api/` 下创建新的路由文件
2. 在 `app/main.py` 中注册路由

示例:

```python
from app.api import your_router
app.include_router(your_router.router, prefix="/api/v1", tags=["your-tag"])
```

## 生产部署

使用 gunicorn + uvicorn workers:

```bash
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 许可证

MIT
'''

    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")


def create_gitignore(project_dir: Path) -> None:
    """创建 .gitignore 文件

    Args:
        project_dir: 项目根目录
    """
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 日志
logs/*.log
*.log

# 环境变量
.env.local
.env.*.local

# 测试
.pytest_cache/
.coverage
htmlcov/

# uv
.uv/

# macOS
.DS_Store
'''

    (project_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")


def install_dependencies(project_dir: Path) -> None:
    """安装项目依赖

    Args:
        project_dir: 项目根目录
    """
    print_colored("[3/8] 安装依赖包...", Colors.GREEN)

    dependencies = [
        "fastapi",
        "uvicorn",
        "loguru",
        "pydantic-settings",
        "python-multipart",
    ]

    dev_dependencies = [
        "pytest",
        "pytest-asyncio",
        "httpx",
    ]

    run_command(["uv", "add"] + dependencies, cwd=project_dir)
    run_command(["uv", "add", "--dev"] + dev_dependencies, cwd=project_dir)


def print_completion_message(project_name: str) -> None:
    """打印完成信息

    Args:
        project_name: 项目名称
    """
    print()
    print_colored("========================================", Colors.BLUE)
    print_colored("✅ 项目创建完成！", Colors.GREEN)
    print_colored("========================================", Colors.BLUE)
    print()
    print_colored("下一步操作:", Colors.YELLOW)
    print_colored(f"  1. cd {project_name}", Colors.GREEN)
    print_colored("  2. uv sync  # 同步依赖", Colors.GREEN)
    print_colored("  3. uv run fastapi dev  # 启动开发服务器", Colors.GREEN)
    print_colored("  4. 访问文档: http://localhost:8000/docs", Colors.BLUE)
    print()
    print_colored("其他启动方式:", Colors.YELLOW)
    print_colored("  uv run fastapi dev --port 8080  # 指定端口", Colors.GREEN)
    print_colored("  uv run uvicorn app.main:app --reload  # 使用uvicorn", Colors.GREEN)
    print()
    print_colored("运行测试:", Colors.YELLOW)
    print_colored("  uv run pytest  # 运行所有测试", Colors.GREEN)
    print_colored("  uv run pytest -v  # 详细输出", Colors.GREEN)
    print()


def create_fastapi_project(project_name: str) -> Literal[0, 1]:
    """创建FastAPI项目

    Args:
        project_name: 项目名称

    Returns:
        0 表示成功，1 表示失败
    """
    # 检查项目名称
    if not project_name:
        print_colored("错误: 请提供项目名称", Colors.RED)
        print("用法: python fastapi_new.py <项目名称>")
        return 1

    # 检查 uv 是否安装
    if not check_uv_installed():
        print_colored("错误: 未找到 uv，请先安装 uv", Colors.RED)
        print("安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return 1

    # 获取当前工作目录
    current_dir = Path.cwd()
    project_dir = current_dir / project_name

    # 检查目录是否已存在
    if project_dir.exists():
        print_colored(f"错误: 目录 {project_name} 已存在", Colors.RED)
        return 1

    # 打印欢迎信息
    print()
    print_colored("========================================", Colors.BLUE)
    print_colored("  FastAPI 项目创建工具", Colors.BLUE)
    print_colored("========================================", Colors.BLUE)
    print()

    # 1. 创建项目目录
    print_colored("[1/8] 创建项目目录...", Colors.GREEN)
    project_dir.mkdir(parents=True, exist_ok=True)

    # 2. 初始化 uv 项目
    print_colored("[2/8] 初始化 uv 项目...", Colors.GREEN)
    run_command(["uv", "init", "--name", project_name], cwd=project_dir)

    # 3. 安装依赖
    install_dependencies(project_dir)

    # 4. 创建项目结构
    create_project_structure(project_dir)

    # 5. 创建日志配置
    create_logger_config(project_dir)

    # 6. 创建配置文件
    create_config_file(project_dir, project_name)

    # 7. 创建主应用文件
    create_main_app(project_dir)
    create_health_check(project_dir)
    create_init_files(project_dir)

    # 8. 创建测试文件
    create_test_files(project_dir)

    # 创建 README 和 .gitignore
    create_readme(project_dir, project_name)
    create_gitignore(project_dir)

    # 打印完成信息
    print_completion_message(project_name)

    return 0


def main() -> int:
    """主函数

    Returns:
        退出码
    """
    parser = argparse.ArgumentParser(
        description="FastAPI项目创建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python fastapi_new.py my-api
  python fastapi_new.py awesome-service
        """
    )
    parser.add_argument(
        "project_name",
        help="项目名称"
    )

    args = parser.parse_args()
    return create_fastapi_project(args.project_name)


if __name__ == "__main__":
    sys.exit(main())
