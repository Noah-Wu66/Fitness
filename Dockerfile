FROM python:3.11-slim

# 安装运行所需的系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（Zeabur 默认读取 PORT 环境变量）
ENV PORT=5000
EXPOSE $PORT

# 使用 Gunicorn 启动 Flask 应用
CMD ["sh", "-c", "gunicorn --workers 2 --timeout 300 --bind 0.0.0.0:${PORT:-${WEB_PORT:-5000}} app:app"] 