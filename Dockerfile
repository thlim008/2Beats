# Python 3.12 slim 버전 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL, Pillow 관련 라이브러리 등)
# 3.12-slim에서도 동일한 의존성이 필요합니다.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
# Python이 pyc 파일을 쓰지 않도록 함
ENV PYTHONDONTWRITEBYTECODE 1
# Python 로그가 버퍼링 없이 출력되도록 함
ENV PYTHONUNBUFFERED 1

# requirements.txt 복사 및 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 프로젝트 코드 복사
COPY . /app/

# Gunicorn 실행 (포트 8000)
CMD python manage.py migrate && \
    python manage.py init_tags && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000