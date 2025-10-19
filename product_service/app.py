from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from pymongo import MongoClient
from service_registry import register_service
from models.product_model import *
from config import *
import requests, consul

app = Flask(__name__)
app.secret_key = "product_secret"

# ---- Consul Service Discovery ----
def get_auth_service_url():
    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
    services = c.agent.services()
    for s in services.values():
        if s["Service"] == AUTH_SERVICE_NAME:
            return f"http://{s['Address']}:{s['Port']}"
    return None

@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


# ---------------- RESTful API ----------------

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(get_all_products()), 200

@app.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    product = get_product_by_id(pid)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

@app.route("/products", methods=["POST"])
def add_product():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.get_json()
    username = session["username"]
    new_product = create_product(data, username)
    return jsonify(new_product), 201


@app.route("/products/<int:pid>", methods=["PUT"])
def update_product_route(pid):
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu dữ liệu JSON"}), 400

    username = session["username"]
    updated = update_product(pid, data, username)
    if updated:
        return jsonify({"message": "Cập nhật sản phẩm thành công"}), 200
    return jsonify({"error": "Không tìm thấy sản phẩm"}), 404


@app.route("/products/<int:pid>", methods=["PUT"])
def edit_product(pid):
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.get_json()
    username = session["username"]
    updated = update_product(pid, data, username)
    if updated:
        return jsonify({"message": "Cập nhật sản phẩm thành công"}), 200
    return jsonify({"error": "Không tìm thấy sản phẩm"}), 404

@app.route("/products/<int:pid>", methods=["DELETE"])
def delete_product_route(pid):
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.get_json()
    if not data or "amount" not in data:
        return jsonify({"error": "Thiếu số lượng cần xóa"}), 400

    username = session["username"]
    result = reduce_quantity(pid, int(data["amount"]), username)
    return jsonify(result)

# ---------------- WEB GIAO DIỆN ----------------
@app.route("/")
def home():
    # Lấy token và username từ query string
    token = request.args.get("token")
    username = request.args.get("username")

    if not token or not username:
        return "<h3>Thiếu token hoặc username!</h3>", 401

    # Gọi Auth Service để xác thực token
    auth_url = get_auth_service_url()
    if not auth_url:
        return "Không tìm thấy Auth Service!", 500

    response = requests.post(f"{auth_url}/auth/verify", headers={"Authorization": token})
    result = response.json()

    if not result.get("valid"):
        return "<h3>Token không hợp lệ hoặc đã hết hạn!</h3>", 401

    # ✅ Lưu username vào session để các API CRUD dùng
    session["username"] = username
    products = get_products_by_user(username)

    return render_template("products.html", products=products, username=username)



if __name__ == "__main__":
    register_service()
    app.run(port=SERVICE_PORT, debug=True)
