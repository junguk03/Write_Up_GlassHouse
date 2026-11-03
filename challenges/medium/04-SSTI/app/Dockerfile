# 문제 서버 이미지
#
# 직접 빌드할 필요는 없습니다. docker compose 가 대신 해 줍니다.
#   docker compose up --build

FROM python:3.12-slim

WORKDIR /srv

# 라이브러리를 먼저 설치하면, 코드만 바꿨을 때 이 단계가 다시 돌지 않아 빠릅니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
