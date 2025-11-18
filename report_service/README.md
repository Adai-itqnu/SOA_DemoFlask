# Report Service

Dịch vụ báo cáo cung cấp các chức năng thống kê số lượng hàng tồn, hàng bán được, doanh thu, chi phí, lợi nhuận theo sản phẩm và đơn hàng.

## Cấu hình

- **Port**: 5003
- **Database**: MySQL (report_db)
- **Service Name**: report-service

## Yêu cầu

- Python 3.7+
- MySQL Server
- Consul (cho service discovery)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cấu hình Database

Cấu hình MySQL trong file `config.py`:
- DB_HOST: localhost
- DB_PORT: 3306
- DB_USER: root
- DB_PASSWORD: (để trống hoặc cấu hình mật khẩu)
- DB_NAME: report_db

Database và các bảng sẽ được tạo tự động khi service khởi động.

## Cấu trúc Database

### Bảng orders_reports
- id (INT, PRIMARY KEY)
- order_id (INT)
- total_revenue (DECIMAL(10, 2))
- total_cost (DECIMAL(10, 2))
- total_profit (DECIMAL(10, 2))

### Bảng product_reports
- id (INT, PRIMARY KEY)
- order_report_id (INT, FOREIGN KEY)
- product_id (INT)
- total_sold (INT)
- revenue (DECIMAL(10, 2))
- cost (DECIMAL(10, 2))
- profit (DECIMAL(10, 2))

## API Endpoints

Tất cả các API yêu cầu xác thực qua header `Authorization` với JWT token.

### Orders Reports

#### GET /reports/orders
Lấy danh sách tất cả các báo cáo theo đơn hàng.

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "order_id": 1,
    "total_revenue": 1000.00,
    "total_cost": 700.00,
    "total_profit": 300.00
  }
]
```

#### GET /reports/orders/{id}
Lấy chi tiết báo cáo cho một đơn hàng.

**Response**: `200 OK`
```json
{
  "id": 1,
  "order_id": 1,
  "total_revenue": 1000.00,
  "total_cost": 700.00,
  "total_profit": 300.00,
  "product_reports": [...]
}
```

#### POST /reports/orders
Tạo báo cáo đơn hàng mới dựa trên dữ liệu từ dịch vụ quản lý đơn hàng.

**Request Body**:
```json
{
  "order_id": 1
}
```

**Response**: `201 Created`

#### DELETE /reports/orders/{id}
Xóa báo cáo đơn hàng.

**Response**: `200 OK`

### Product Reports

#### GET /reports/products
Lấy danh sách tất cả các báo cáo theo sản phẩm.

**Response**: `200 OK`

#### GET /reports/products/{id}
Lấy chi tiết báo cáo cho một sản phẩm.

**Response**: `200 OK`

#### POST /reports/products
Tạo báo cáo sản phẩm mới dựa trên dữ liệu từ dịch vụ quản lý sản phẩm và quản lý đơn hàng.

**Request Body**:
```json
{
  "order_report_id": 1,
  "product_id": 1
}
```

**Response**: `201 Created`

#### DELETE /reports/products/{id}
Xóa báo cáo sản phẩm.

**Response**: `200 OK`

### Statistics (Bonus)

#### GET /reports/products/{product_id}/statistics
Lấy thống kê tổng hợp cho một sản phẩm.

**Response**: `200 OK`

## Khởi chạy Service

```bash
python app.py
```

Service sẽ:
1. Tự động khởi tạo database nếu chưa tồn tại
2. Đăng ký với Consul service discovery
3. Chạy trên port 5003

## Tích hợp với các Service khác

Report Service tích hợp với:
- **Auth Service**: Xác thực JWT token
- **Product Service**: Lấy thông tin sản phẩm để tính toán chi phí
- **Order Service**: Lấy thông tin đơn hàng và order items để tính toán báo cáo

## Ghi chú

- Service hoạt động độc lập trên port 5003 và database riêng
- Tất cả API đều yêu cầu xác thực qua JWT token từ Auth Service
- Tính toán chi phí dựa trên giá nhập sản phẩm. Nếu không có trường `cost` trong product, mặc định sẽ dùng 70% giá bán.

