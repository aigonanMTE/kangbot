FROM python:3.11-slim

# 작업 디렉토리 생성
WORKDIR /app

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# 환경변수는 런타임에 주입
CMD ["python", "main.py"]
