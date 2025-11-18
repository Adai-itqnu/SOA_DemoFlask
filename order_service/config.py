import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/order_db")
SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5002"))
AUTH_SERVICE_NAME = os.getenv("AUTH_SERVICE_NAME", "auth-service")
PRODUCT_SERVICE_NAME = os.getenv("PRODUCT_SERVICE_NAME", "product-service")
CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))