# SOA Demo - Microservices Architecture

Dự án SOA Demo với kiến trúc microservices sử dụng Flask, MongoDB, Consul và Nginx API Gateway.

## Kiến trúc

- **Auth Service** (Port 5000): Dịch vụ xác thực với JWT
- **Product Service** (Port 5001): Quản lý sản phẩm
- **Order Service** (Port 5002): Quản lý đơn hàng
- **Report Service** (Port 5003): Báo cáo và thống kê
- **Nginx API Gateway** (Port 80): API Gateway với Consul Template
- **MongoDB**: Database cho tất cả services
- **Consul**: Service Discovery

## Cấu trúc dự án

```
SOA_Demo/
├── auth_service/
├── product_service/
├── order_service/
├── report_service/
├── nginx/
├── docker-compose.yml
└── README.md
```

## Yêu cầu

- Docker và Docker Compose
- Hoặc Python 3.9+ và MongoDB, Consul (để chạy local)

## Chạy với Docker Compose

### 1. Khởi động toàn bộ hệ thống

```bash
docker-compose up -d
```

### 2. Kiểm tra services đã chạy

```bash
docker-compose ps
```

### 3. Xem logs

```bash
# Xem logs tất cả services
docker-compose logs -f

# Xem logs của một service cụ thể
docker-compose logs -f auth_service
docker-compose logs -f nginx
```

### 4. Dừng hệ thống

```bash
docker-compose down
```

### 5. Dừng và xóa volumes (dữ liệu)

```bash
docker-compose down -v
```

## Chạy local (không dùng Docker)

### 1. Khởi động MongoDB

```bash
# Trên Windows/Linux
mongod

# Hoặc với Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### 2. Khởi động Consul

```bash
# Với Docker
docker run -d -p 8500:8500 --name consul consul:1.17 agent -dev -client=0.0.0.0

# Hoặc download và chạy binary
consul agent -dev
```

### 3. Cài đặt dependencies cho mỗi service

```bash
cd auth_service
pip install -r requirements.txt
python app.py

cd ../product_service
pip install -r requirements.txt
python app.py

cd ../order_service
pip install -r requirements.txt
python app.py

cd ../report_service
pip install -r requirements.txt
python app.py
```

### 4. Khởi động Nginx (với consul-template)

```bash
cd nginx
docker build -t nginx-gateway .
docker run -d -p 80:80 \
  -e CONSUL_ADDR=localhost:8500 \
  --link consul:consul \
  nginx-gateway
```

## API Gateway Endpoints

Tất cả requests đều qua Nginx API Gateway tại `http://localhost`

### Auth Service
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `POST /auth/verify` - Xác thực token

### Product Service
- `GET /products` - Lấy danh sách sản phẩm
- `GET /products/{id}` - Lấy chi tiết sản phẩm
- `POST /products` - Tạo sản phẩm mới
- `PUT /products/{id}` - Cập nhật sản phẩm
- `DELETE /products/{id}` - Xóa sản phẩm

### Order Service
- `GET /orders` - Lấy danh sách đơn hàng
- `GET /orders/{id}` - Lấy chi tiết đơn hàng
- `POST /orders` - Tạo đơn hàng mới
- `PUT /orders/{id}` - Cập nhật đơn hàng
- `DELETE /orders/{id}` - Xóa đơn hàng
- `GET /order_items` - Lấy danh sách order items
- `GET /order_items/{id}` - Lấy chi tiết order item

### Report Service
- `GET /reports/orders` - Lấy danh sách báo cáo đơn hàng
- `GET /reports/orders/{id}` - Lấy chi tiết báo cáo đơn hàng
- `POST /reports/orders` - Tạo báo cáo đơn hàng mới
- `DELETE /reports/orders/{id}` - Xóa báo cáo đơn hàng
- `GET /reports/products` - Lấy danh sách báo cáo sản phẩm
- `GET /reports/products/{id}` - Lấy chi tiết báo cáo sản phẩm
- `POST /reports/products` - Tạo báo cáo sản phẩm mới
- `DELETE /reports/products/{id}` - Xóa báo cáo sản phẩm
- `GET /reports/products/{product_id}/statistics` - Thống kê sản phẩm

## Consul UI

Truy cập Consul UI để xem service discovery:
- URL: `http://localhost:8500/ui`

## Kiểm tra Health Check

```bash
# Auth Service
curl http://localhost:5000/health

# Product Service
curl http://localhost:5001/health

# Order Service
curl http://localhost:5002/health

# Report Service
curl http://localhost:5003/health

# Nginx Gateway
curl http://localhost/health
```

## Ghi chú

- Tất cả services sử dụng MongoDB riêng biệt (database khác nhau)
- Service Discovery tự động qua Consul
- Nginx API Gateway tự động cập nhật upstream khi services thay đổi (qua consul-template)
- Tất cả API đều yêu cầu JWT token (trừ /auth/login và /auth/register)
- Services có thể scale bằng cách chạy nhiều instances và Consul sẽ tự động load balance

## Troubleshooting

### Services không kết nối được Consul

Kiểm tra Consul đang chạy:
```bash
curl http://localhost:8500/v1/status/leader
```

### MongoDB connection error

Kiểm tra MongoDB đang chạy:
```bash
docker ps | grep mongodb
# hoặc
mongosh
```

### Nginx không route đúng

Kiểm tra consul-template logs:
```bash
docker-compose logs nginx
```

Kiểm tra services đã đăng ký trong Consul:
- Truy cập: http://localhost:8500/ui
- Kiểm tra Services tab

## Development

### Build lại một service

```bash
docker-compose build auth_service
docker-compose up -d auth_service
```

### Rebuild tất cả

```bash
docker-compose build --no-cache
docker-compose up -d
```

