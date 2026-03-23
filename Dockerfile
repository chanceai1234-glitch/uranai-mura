FROM python:3.12-slim

# システム依存パッケージ
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI インストール
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係インストール
COPY pyproject.toml ./
RUN pip install --no-cache-dir pyyaml anthropic pytest pytest-asyncio ruff

# アプリケーションコード
COPY . .

# Vault マウントポイント
VOLUME ["/vault"]

ENV OBSIDIAN_VAULT_PATH=/vault
ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "agents.run"]
