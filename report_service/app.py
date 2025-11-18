from flask import Flask, jsonify, request, session
from service_registry import register_service
from models.report_model import *
from config import *
import requests
import consul

app = Flask(__name__)
app.secret_key = "report_secret"

# ==================== SERVICE DISCOVERY ====================

def get_service_url(service_name):
    """Lấy URL của service từ Consul"""
    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
    services = c.agent.services()
    for s in services.values():
        if s["Service"] == service_name:
            return f"http://{s['Address']}:{s['Port']}"
    return None


def verify_token(token):
    """Xác thực token qua Auth Service"""
    auth_url = get_service_url(AUTH_SERVICE_NAME)
    if not auth_url:
        return False
    
    try:
        response = requests.post(
            f"{auth_url}/auth/verify",
            headers={"Authorization": token},
            timeout=5
        )
        return response.json().get("valid", False)
    except:
        return False


def get_order_data(order_id):
    """Lấy dữ liệu đơn hàng từ Order Service"""
    order_url = get_service_url(ORDER_SERVICE_NAME)
    if not order_url:
        return None
    
    try:
        # Lấy thông tin đơn hàng
        response = requests.get(f"{order_url}/orders/{order_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_order_items_data(order_id):
    """Lấy danh sách order items từ Order Service"""
    order_url = get_service_url(ORDER_SERVICE_NAME)
    if not order_url:
        return []
    
    try:
        response = requests.get(f"{order_url}/orders/{order_id}", timeout=5)
        if response.status_code == 200:
            order = response.json()
            return order.get("items", [])
        return []
    except:
        return []


def get_product_data(product_id):
    """Lấy dữ liệu sản phẩm từ Product Service"""
    product_url = get_service_url(PRODUCT_SERVICE_NAME)
    if not product_url:
        return None
    
    try:
        response = requests.get(f"{product_url}/products/{product_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


# ==================== HELPER FUNCTIONS ====================

def calculate_order_report(order_id):
    """Tính toán và tạo báo cáo đơn hàng dựa trên dữ liệu từ Order Service"""
    # Lấy dữ liệu đơn hàng
    order = get_order_data(order_id)
    if not order:
        return None, "Không tìm thấy đơn hàng"
    
    # Lấy danh sách order items
    items = order.get("items", [])
    if not items:
        items = get_order_items_data(order_id)
    
    if not items:
        return None, "Đơn hàng không có sản phẩm"
    
    total_revenue = 0.0
    total_cost = 0.0
    
    # Tính toán doanh thu và chi phí từ các order items
    product_reports_data = []
    
    for item in items:
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 0))
        unit_price = float(item.get("unit_price", 0))
        revenue = quantity * unit_price
        total_revenue += revenue
        
        # Lấy thông tin sản phẩm để tính chi phí
        product = get_product_data(product_id)
        if product:
            # Giả sử cost là giá nhập, nếu không có thì dùng giá bán * 0.7
            # Trong thực tế, cần có trường cost trong product
            cost_per_unit = float(product.get("cost", product.get("price", 0) * 0.7))
            cost = quantity * cost_per_unit
            total_cost += cost
            
            profit = revenue - cost
            
            product_reports_data.append({
                "product_id": product_id,
                "total_sold": quantity,
                "revenue": revenue,
                "cost": cost,
                "profit": profit
            })
        else:
            # Nếu không lấy được product, giả sử cost = 70% revenue
            cost = revenue * 0.7
            total_cost += cost
            profit = revenue - cost
            
            product_reports_data.append({
                "product_id": product_id,
                "total_sold": quantity,
                "revenue": revenue,
                "cost": cost,
                "profit": profit
            })
    
    total_profit = total_revenue - total_cost
    
    return {
        "order_id": order_id,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "product_reports": product_reports_data
    }, None


def calculate_product_report(order_report_id, product_id):
    """Tính toán và tạo báo cáo sản phẩm từ order items của một order_report cụ thể"""
    # order_report_id có thể là order_id
    order_report = get_order_report_by_id(order_report_id)
    if not order_report:
        return None
    
    order_id = order_report.get("order_id", order_report_id)
    
    # Lấy order items từ order này
    items = get_order_items_data(order_id)
    
    total_sold = 0
    total_revenue = 0.0
    total_cost = 0.0
    
    # Tìm các item có product_id này trong order này
    for item in items:
        if item.get("product_id") == product_id:
            quantity = int(item.get("quantity", 0))
            unit_price = float(item.get("unit_price", 0))
            revenue = quantity * unit_price
            
            # Lấy thông tin sản phẩm để tính cost
            product = get_product_data(product_id)
            if product:
                # Giả sử cost là giá nhập, nếu không có thì dùng giá bán * 0.7
                cost_per_unit = float(product.get("cost", product.get("price", 0) * 0.7))
                cost = quantity * cost_per_unit
            else:
                # Nếu không lấy được product, giả sử cost = 70% revenue
                cost = revenue * 0.7
            
            total_sold += quantity
            total_revenue += revenue
            total_cost += cost
    
    total_profit = total_revenue - total_cost
    
    return {
        "order_report_id": order_report_id,
        "product_id": product_id,
        "total_sold": total_sold,
        "revenue": total_revenue,
        "cost": total_cost,
        "profit": total_profit
    }


# ==================== HEALTH CHECK ====================

@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


# ==================== ORDERS REPORTS API ====================

@app.route("/reports/orders", methods=["GET"])
def get_order_reports():
    """GET /reports/orders - Lấy danh sách tất cả các báo cáo theo đơn hàng"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    reports = get_all_order_reports()
    return jsonify(reports), 200


@app.route("/reports/orders/<int:report_id>", methods=["GET"])
def get_order_report(report_id):
    """GET /reports/orders/id - Lấy chi tiết báo cáo cho một đơn hàng"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    report = get_order_report_by_id(report_id)
    if report:
        # Lấy thêm các product reports liên quan
        product_reports = get_product_reports_by_order_report_id(report_id)
        report["product_reports"] = product_reports
        return jsonify(report), 200
    
    return jsonify({"error": "Không tìm thấy báo cáo đơn hàng"}), 404


@app.route("/reports/orders", methods=["POST"])
def create_order_report():
    """POST /reports/orders - Tạo báo cáo đơn hàng mới dựa trên dữ liệu từ dịch vụ quản lý đơn hàng"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    # Validate required fields
    if "order_id" not in data:
        return jsonify({"error": "Thiếu trường order_id"}), 400
    
    order_id = data["order_id"]
    
    # Kiểm tra xem đã có báo cáo cho order này chưa
    existing_report = get_order_report_by_order_id(order_id)
    if existing_report:
        return jsonify({"error": "Báo cáo cho đơn hàng này đã tồn tại", "report": existing_report}), 400
    
    # Tính toán báo cáo
    report_data, error = calculate_order_report(order_id)
    if error:
        return jsonify({"error": error}), 400
    
    # Tạo order report
    order_report = create_order_report(
        report_data["order_id"],
        report_data["total_revenue"],
        report_data["total_cost"],
        report_data["total_profit"]
    )
    
    if not order_report:
        return jsonify({"error": "Lỗi khi tạo báo cáo đơn hàng"}), 500
    
    order_report_id = order_report.get("order_id")
    
    # Tạo các product reports
    for product_report_data in report_data["product_reports"]:
        create_product_report(
            order_report_id,
            product_report_data["product_id"],
            product_report_data["total_sold"],
            product_report_data["revenue"],
            product_report_data["cost"],
            product_report_data["profit"]
        )
    
    # Lấy lại report đầy đủ
    created_report = get_order_report_by_id(order_report_id)
    product_reports = get_product_reports_by_order_report_id(order_report_id)
    created_report["product_reports"] = product_reports
    
    return jsonify(created_report), 201


@app.route("/reports/orders/<int:report_id>", methods=["DELETE"])
def delete_order_report_route(report_id):
    """DELETE /reports/orders/id - Xóa báo cáo đơn hàng"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    deleted = delete_order_report(report_id)
    if deleted:
        return jsonify({"message": "Xóa báo cáo đơn hàng thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy báo cáo đơn hàng"}), 404


# ==================== PRODUCT REPORTS API ====================

@app.route("/reports/products", methods=["GET"])
def get_product_reports():
    """GET /reports/products - Lấy danh sách tất cả các báo cáo theo sản phẩm"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    reports = get_all_product_reports()
    return jsonify(reports), 200


@app.route("/reports/products/<int:report_id>", methods=["GET"])
def get_product_report(report_id):
    """GET /reports/products/id - Lấy chi tiết báo cáo cho một sản phẩm"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    report = get_product_report_by_id(report_id)
    if report:
        return jsonify(report), 200
    
    return jsonify({"error": "Không tìm thấy báo cáo sản phẩm"}), 404


@app.route("/reports/products", methods=["POST"])
def create_product_report_route():
    """POST /reports/products - Tạo báo cáo sản phẩm mới dựa trên dữ liệu từ dịch vụ quản lý sản phẩm và quản lý đơn hàng"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    # Validate required fields
    required_fields = ["order_report_id", "product_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Thiếu trường {field}"}), 400
    
    order_report_id = data["order_report_id"]
    product_id = data["product_id"]
    
    # Kiểm tra order_report có tồn tại không
    order_report = get_order_report_by_id(order_report_id)
    if not order_report:
        return jsonify({"error": "Báo cáo đơn hàng không tồn tại"}), 404
    
    # Tính toán báo cáo sản phẩm
    report_data = calculate_product_report(order_report_id, product_id)
    if not report_data:
        return jsonify({"error": "Lỗi khi tính toán báo cáo sản phẩm"}), 500
    
    # Tạo product report
    created_report = create_product_report(
        report_data["order_report_id"],
        report_data["product_id"],
        report_data["total_sold"],
        report_data["revenue"],
        report_data["cost"],
        report_data["profit"]
    )
    
    if not created_report:
        return jsonify({"error": "Lỗi khi tạo báo cáo sản phẩm"}), 500
    
    # Lấy lại report đầy đủ
    report_id = created_report.get("id")
    if report_id:
        created_report_full = get_product_report_by_id(report_id)
        if created_report_full:
            created_report = created_report_full
    return jsonify(created_report), 201


@app.route("/reports/products/<int:report_id>", methods=["DELETE"])
def delete_product_report_route(report_id):
    """DELETE /reports/products/id - Xóa báo cáo sản phẩm"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    deleted = delete_product_report(report_id)
    if deleted:
        return jsonify({"message": "Xóa báo cáo sản phẩm thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy báo cáo sản phẩm"}), 404


# ==================== STATISTICS API (Bonus) ====================

@app.route("/reports/products/<int:product_id>/statistics", methods=["GET"])
def get_product_statistics(product_id):
    """GET /reports/products/<product_id>/statistics - Lấy thống kê tổng hợp cho một sản phẩm"""
    # Kiểm tra token
    token = request.headers.get("Authorization")
    if not token or not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    stats = get_product_statistics_by_id(product_id)
    if stats:
        return jsonify(stats), 200
    
    return jsonify({"error": "Không tìm thấy thống kê cho sản phẩm này"}), 404


if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)

