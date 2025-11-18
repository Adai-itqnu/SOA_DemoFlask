FROM python:3.9-slim

WORKDIR /app

# Copy requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 5001

# Chạy ứng dụng
CMD ["python", "app.py"]

