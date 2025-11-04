from flask import Flask, jsonify, request, render_template, session, redirect
from service_registry import register_service
from models.order_model import *
from config import *
import requests
import consul

app = Flask(__name__)
app.secret_key = "order_secret"

# ---- Consul Service Discovery ----
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


def check_product_stock(product_id, quantity):
    """Kiểm tra tồn kho sản phẩm từ Product Service"""
    product_url = get_service_url(PRODUCT_SERVICE_NAME)
    if not product_url:
        return {"available": False, "message": "Không tìm thấy Product Service"}
    
    try:
        response = requests.get(f"{product_url}/products/{product_id}", timeout=5)
        if response.status_code == 200:
            product = response.json()
            if product["quantity"] >= quantity:
                return {"available": True, "product": product}
            else:
                return {
                    "available": False,
                    "message": f"Không đủ hàng. Tồn kho: {product['quantity']}"
                }
        else:
            return {"available": False, "message": "Sản phẩm không tồn tại"}
    except:
        return {"available": False, "message": "Lỗi kết nối Product Service"}


@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


# ==================== ORDERS API ====================

@app.route("/orders", methods=["GET"])
def get_orders():
    """GET /orders - Lấy danh sách tất cả đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    orders = get_all_orders(username)
    return jsonify(orders), 200


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """GET /orders/id - Lấy thông tin chi tiết một đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    order = get_order_by_id(order_id, username)
    
    if order:
        # Lấy thêm danh sách order items
        items = get_order_items_by_order(order_id, username)
        order["items"] = items
        return jsonify(order), 200
    
    return jsonify({"error": "Không tìm thấy đơn hàng"}), 404


@app.route("/orders", methods=["POST"])
def add_order():
    """POST /orders - Tạo đơn hàng mới"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    # Validate required fields
    required = ["id", "customer_name", "customer_email"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Thiếu trường {field}"}), 400
    
    username = session["username"]
    
    # Kiểm tra tồn kho cho các sản phẩm trong đơn (nếu có items)
    if "items" in data:
        for item in data["items"]:
            stock_check = check_product_stock(item["product_id"], item["quantity"])
            if not stock_check["available"]:
                return jsonify({
                    "error": f"Sản phẩm {item['product_id']}: {stock_check['message']}"
                }), 400
    
    # Tạo đơn hàng
    new_order = create_order(data, username)
    
    # Tạo order items nếu có
    if "items" in data:
        for item in data["items"]:
            item_data = {
                "id": item["id"],
                "order_id": data["id"],
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"]
            }
            create_order_item(item_data, username)
        
        # Tính lại tổng tiền
        total = calculate_order_total(data["id"], username)
        new_order["total_amount"] = total
    
    return jsonify(new_order), 201


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order_route(order_id):
    """PUT /orders/id - Cập nhật trạng thái đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    username = session["username"]
    updated = update_order(order_id, data, username)
    
    if updated:
        return jsonify({"message": "Cập nhật đơn hàng thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy đơn hàng"}), 404


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order_route(order_id):
    """DELETE /orders/id - Xóa đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    deleted = delete_order(order_id, username)
    
    if deleted:
        return jsonify({"message": "Xóa đơn hàng thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy đơn hàng"}), 404


# ==================== ORDER ITEMS API ====================

@app.route("/order_items", methods=["GET"])
def get_items():
    """GET /order_items - Lấy danh sách tất cả mặt hàng trong đơn"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    items = get_all_order_items(username)
    return jsonify(items), 200


@app.route("/order_items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """GET /order_items/id - Lấy thông tin chi tiết một mặt hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    item = get_order_item_by_id(item_id, username)
    
    if item:
        return jsonify(item), 200
    
    return jsonify({"error": "Không tìm thấy mặt hàng"}), 404


@app.route("/order_items", methods=["POST"])
def add_item():
    """POST /order_items - Tạo mặt hàng mới trong đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    # Validate required fields
    required = ["id", "order_id", "product_id", "product_name", "quantity", "unit_price"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Thiếu trường {field}"}), 400
    
    # Kiểm tra tồn kho
    stock_check = check_product_stock(data["product_id"], data["quantity"])
    if not stock_check["available"]:
        return jsonify({"error": stock_check["message"]}), 400
    
    username = session["username"]
    
    # Kiểm tra order có tồn tại không
    order = get_order_by_id(data["order_id"], username)
    if not order:
        return jsonify({"error": "Đơn hàng không tồn tại"}), 404
    
    new_item = create_order_item(data, username)
    
    # Cập nhật tổng tiền đơn hàng
    calculate_order_total(data["order_id"], username)
    
    return jsonify(new_item), 201


@app.route("/order_items/<int:item_id>", methods=["PUT"])
def update_item_route(item_id):
    """PUT /order_items/id - Cập nhật mặt hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400
    
    username = session["username"]
    
    # Lấy thông tin item hiện tại
    item = get_order_item_by_id(item_id, username)
    if not item:
        return jsonify({"error": "Không tìm thấy mặt hàng"}), 404
    
    # Nếu thay đổi số lượng, kiểm tra tồn kho
    if "quantity" in data and data["quantity"] != item["quantity"]:
        stock_check = check_product_stock(item["product_id"], data["quantity"])
        if not stock_check["available"]:
            return jsonify({"error": stock_check["message"]}), 400
    
    updated = update_order_item(item_id, data, username)
    
    if updated:
        # Cập nhật lại tổng tiền đơn hàng
        calculate_order_total(item["order_id"], username)
        return jsonify({"message": "Cập nhật mặt hàng thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy mặt hàng"}), 404


@app.route("/order_items/<int:item_id>", methods=["DELETE"])
def delete_item_route(item_id):
    """DELETE /order_items/id - Xóa mặt hàng trong đơn hàng"""
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    username = session["username"]
    
    # Lấy thông tin item để biết order_id
    item = get_order_item_by_id(item_id, username)
    if not item:
        return jsonify({"error": "Không tìm thấy mặt hàng"}), 404
    
    order_id = item["order_id"]
    deleted = delete_order_item(item_id, username)
    
    if deleted:
        # Cập nhật lại tổng tiền đơn hàng
        calculate_order_total(order_id, username)
        return jsonify({"message": "Xóa mặt hàng thành công"}), 200
    
    return jsonify({"error": "Không tìm thấy mặt hàng"}), 404


# ==================== WEB INTERFACE ====================

@app.route("/")
def home():
    """Trang chủ hiển thị danh sách đơn hàng"""
    token = request.args.get("token")
    username = request.args.get("username")
    
    if not token or not username:
        return "<h3>Thiếu token hoặc username!</h3>", 401
    
    # Xác thực token
    if not verify_token(token):
        return "<h3>Token không hợp lệ hoặc đã hết hạn!</h3>", 401
    
    # Lưu username vào session
    session["username"] = username
    
    # Lấy danh sách đơn hàng
    orders = get_all_orders(username)
    
    return render_template("orders.html", orders=orders, username=username)


if __name__ == "__main__":
    register_service()
    app.run(port=SERVICE_PORT, debug=True)