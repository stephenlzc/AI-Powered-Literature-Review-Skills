# Literature Reviewer Skill - Docker 运行环境
# 提供隔离、安全的运行环境

FROM mcr.microsoft.com/playwright:v1.40.0-jammy

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -s /bin/bash researcher && \
    mkdir -p /app/skills /app/sessions /app/output && \
    chown -R researcher:researcher /app

# 切换到非 root 用户
USER researcher

# 设置环境变量
ENV PYTHONPATH=/app
ENV NODE_PATH=/usr/lib/node_modules
ENV PATH="/home/researcher/.local/bin:${PATH}"

# 创建工作目录
WORKDIR /app/skills/literature-reviewer-skill

# 提示信息
RUN echo "========================================" && \
    echo "Literature Reviewer Skill - Docker 环境" && \
    echo "========================================" && \
    echo "" && \
    echo "使用方法:" && \
    echo "1. 将本 Skill 代码挂载到容器:" && \
    echo "   docker run -v $(pwd):/app/skills/literature-reviewer-skill ..." && \
    echo "" && \
    echo "2. 运行 Playwright 安装:" && \
    echo "   playwright install chromium" && \
    echo "" && \
    echo "3. 启动 Skill:" && \
    echo "   在 AI 工具中使用本 Skill" && \
    echo "========================================"

# 默认命令
CMD ["/bin/bash"]
