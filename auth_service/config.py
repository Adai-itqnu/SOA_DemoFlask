import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/user_db")
SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5000"))
JWT_SECRET = os.getenv("JWT_SECRET", "mysecretkey")
CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
