# 多阶段构建，优化生产镜像大小
FROM python:3.13-slim as builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置工作目录
WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖
RUN uv sync --frozen --no-cache

# 生产镜像
FROM python:3.13-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/user_srv/logs && chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('127.0.0.1', 50051)); s.close()" || exit 1

# 暴露端口
EXPOSE 50051

# 启动命令
CMD ["python", "-m", "user_srv.server", "--host", "0.0.0.0", "--port", "50051"]