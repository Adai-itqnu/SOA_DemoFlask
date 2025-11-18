import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/product_db")
SERVICE_NAME = os.getenv("SERVICE_NAME", "product-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5001"))
AUTH_SERVICE_NAME = os.getenv("AUTH_SERVICE_NAME", "auth-service")
CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
