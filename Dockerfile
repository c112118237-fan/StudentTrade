FROM python:3.10-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 建立上傳目錄
RUN mkdir -p /app/app/static/uploads/products && \
    mkdir -p /app/app/static/uploads/avatars

EXPOSE 5000

CMD ["python", "run.py"]
