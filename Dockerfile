
# 使用官方Python运行时作为父镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到位于/app的容器中
COPY . /app

# 安装任何所需的包
RUN pip install --no-cache-dir -r requirements.txt

# 使端口5000可用于此容器外部
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app/app.py

# 运行app.py
CMD ["flask", "run", "--host", "0.0.0.0"] 