#!/usr/bin/env bash
# FastAPI项目创建脚本
# 用法: ./fastapinew.sh <项目名称>

set -e # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供项目名称${NC}"
    echo "用法: $0 <项目名称>"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$(pwd)/$PROJECT_NAME"

# 检查目录是否已存在
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 目录 $PROJECT_NAME 已存在${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FastAPI 项目创建工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 创建项目目录
echo -e "${GREEN}[1/8] 创建项目目录...${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 2. 初始化uv项目
echo -e "${GREEN}[2/8] 初始化uv项目...${NC}"
uv init --name "$PROJECT_NAME"

# 3. 安装依赖
echo -e "${GREEN}[3/8] 安装依赖包...${NC}"
uv add fastapi "fastapi[standard]" uvicorn loguru pydantic-settings python-multipart
uv add --dev pytest pytest-asyncio httpx

# 4. 创建项目结构
echo -e "${GREEN}[4/8] 创建项目结构...${NC}"
mkdir -p app/{api,core,models,services,utils}
mkdir -p tests
mkdir -p logs

# 5. 创建日志配置
echo -e "${GREEN}[5/8] 创建日志配置...${NC}"
cat >app/core/logger.py <<'EOF'
"""日志配置模块"""
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
EOF

# 6. 创建配置文件
echo -e "${GREEN}[6/8] 创建配置文件...${NC}"
cat >app/core/config.py <<'EOF'
"""应用配置模块"""
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
EOF

cat >.env <<EOF
# 应用配置
APP_NAME=${PROJECT_NAME}
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
EOF

# 7. 创建主应用文件
echo -e "${GREEN}[7/8] 创建主应用文件...${NC}"
cat >app/main.py <<'EOF'
"""FastAPI主应用"""
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
EOF

# 在项目根目录创建main.py入口，用于fastapi dev命令
cat >main.py <<'EOF'
"""项目入口文件 - 用于 fastapi dev 命令"""
from app.main import app

# 导出app实例供fastapi CLI使用
__all__ = ["app"]
EOF

# 创建健康检查路由
cat >app/api/health.py <<'EOF'
"""健康检查API"""
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
EOF

# 创建API模块初始化文件
cat >app/api/__init__.py <<'EOF'
"""API路由模块"""
EOF

# 创建各模块初始化文件
cat >app/__init__.py <<'EOF'
"""应用包"""
EOF
cat >app/core/__init__.py <<'EOF'
"""核心模块"""
EOF
cat >app/models/__init__.py <<'EOF'
"""数据模型模块"""
EOF
cat >app/services/__init__.py <<'EOF'
"""业务服务模块"""
EOF
cat >app/utils/__init__.py <<'EOF'
"""工具模块"""
EOF

# 8. 创建测试文件
echo -e "${GREEN}[8/8] 创建测试文件...${NC}"
cat >tests/__init__.py <<'EOF'
"""测试模块"""
EOF

cat >tests/test_main.py <<'EOF'
"""主应用测试"""
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
EOF

# 9. 更新README
cat >README.md <<EOF
# ${PROJECT_NAME}

FastAPI 项目模板，集成 loguru 日志框架。

## 项目结构

\`\`\`
${PROJECT_NAME}/
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
\`\`\`

## 快速开始

### 安装依赖

\`\`\`bash
uv sync
\`\`\`

### 运行开发服务器

**推荐方式 - 使用 fastapi dev:**

\`\`\`bash
uv run fastapi dev
\`\`\`

**或者指定端口:**

\`\`\`bash
uv run fastapi dev --port 8080
\`\`\`

**传统方式 - 使用 uvicorn:**

\`\`\`bash
uv run uvicorn app.main:app --reload
\`\`\`

### 运行测试

\`\`\`bash
uv run pytest
\`\`\`

### 查看API文档

启动服务后访问: http://localhost:8000/docs

## 日志配置

日志由 \`loguru\` 管理，配置位于 \`app/core/logger.py\`。

- 日志文件: \`logs/app.log\`
- 错误日志: \`logs/error.log\`
- 日志轮转: 500MB
- 日志保留: 7天

## 环境变量

在 \`.env\` 文件中配置：

\`\`\`
APP_NAME=Your App Name
DEBUG=true
LOG_LEVEL=INFO
\`\`\`

## 开发

添加新的API路由:

1. 在 \`app/api/\` 下创建新的路由文件
2. 在 \`app/main.py\` 中注册路由

示例:

\`\`\`python
from app.api import your_router
app.include_router(your_router.router, prefix="/api/v1", tags=["your-tag"])
\`\`\`

## 生产部署

使用 gunicorn + uvicorn workers:

\`\`\`bash
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
\`\`\`

## 许可证

MIT
EOF

# 10. 创建.gitignore

cat >.gitignore <<'EOF'
# Python
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
EOF

# 完成
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 项目创建完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo -e "  1. ${GREEN}cd $PROJECT_NAME${NC}"
echo -e "  2. ${GREEN}uv sync${NC}  # 同步依赖"
echo -e "  3. ${GREEN}uv run fastapi dev${NC}  # 启动开发服务器"
echo -e "  4. 访问文档: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}其他启动方式:${NC}"
echo -e "  ${GREEN}uv run fastapi dev --port 8080${NC}  # 指定端口"
echo -e "  ${GREEN}uv run uvicorn app.main:app --reload${NC}  # 使用uvicorn"
echo ""
echo -e "${YELLOW}运行测试:${NC}"
echo -e "  ${GREEN}uv run pytest${NC}  # 运行所有测试"
echo -e "  ${GREEN}uv run pytest -v${NC}  # 详细输出"
echo ""
