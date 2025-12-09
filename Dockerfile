# ==========================================
# Stage 1: Builder (빌드 단계)
# ==========================================
FROM python:3.12-slim as builder

WORKDIR /app

# 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# Stage 2: Runtime (실행 단계)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# 런타임 라이브러리만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Builder에서 Python 패키지 복사
COPY --from=builder /root/.local /root/.local

# 프로젝트 코드 복사 (.dockerignore 적용됨)
COPY . .

# 포트
EXPOSE 8000

# Gunicorn 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "config.wsgi:application"]