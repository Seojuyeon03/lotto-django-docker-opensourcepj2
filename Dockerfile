# 1. 파이썬 베이스 이미지 사용 (슬림 버전)
FROM python:3.11-slim

# 2. 파이썬 버퍼링/pyc 파일 방지 (선택이지만 관례)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 필요한 패키지 먼저 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 소스 전체 복사
COPY . .

# 6. 컨테이너에서 열 포트
EXPOSE 8000

# 7. 컨테이너 시작 시 실행할 명령
#    - migrate 하고
#    - 개발 서버를 0.0.0.0:8000 으로 실행
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
