# ./Dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 시스템 라이브러리(필요 최소)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# 프로젝트 복사
COPY . /app

# 파이썬 의존성 설치
RUN pip install --upgrade pip && \
    pip install -e . "langgraph-cli[inmem]"

# 8123 포트로 LangGraph Server dev 모드 실행
EXPOSE 8123
CMD ["bash","-lc","langgraph dev --host 0.0.0.0 --port 8123"]
