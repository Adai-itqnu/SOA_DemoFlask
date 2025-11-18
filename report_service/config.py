import os

# MongoDB Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/report_db")

# Service Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "report-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5003"))

# External Services
AUTH_SERVICE_NAME = os.getenv("AUTH_SERVICE_NAME", "auth-service")
PRODUCT_SERVICE_NAME = os.getenv("PRODUCT_SERVICE_NAME", "product-service")
ORDER_SERVICE_NAME = os.getenv("ORDER_SERVICE_NAME", "order-service")

# Consul Configuration
CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))

