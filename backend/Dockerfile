FROM python:3.11-slim

WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY app/ ./app/
COPY main.py .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["python", "main.py"]
