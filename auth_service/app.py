from flask import Flask, request, jsonify, redirect, url_for, session
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from datetime import timedelta
from models.user_model import create_user, find_user, update_token, check_password
from service_registry import register_service
from config import *
import consul

app = Flask(__name__)
app.secret_key = "auth_secret"

# JWT setup
app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)

@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


# ---------------- API Endpoints ----------------
# Frontend đã được tách ra thư mục frontend riêng
# Các routes chỉ trả về JSON, không render template nữa

@app.route("/register", methods=["POST"])
def register():
    """API đăng ký - chỉ trả về JSON"""
    data = request.get_json()
    username = data.get("username") if data else request.form.get("username")
    password = data.get("password") if data else request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Thiếu thông tin đăng nhập!"}), 400

    if find_user(username):
        return jsonify({"error": "Tên đăng nhập đã tồn tại!"}), 400

    create_user(username, password)
    return jsonify({"message": "Đăng ký thành công"}), 201


@app.route("/login", methods=["POST"])
def login():
    """API đăng nhập - chỉ trả về JSON"""
    data = request.get_json()
    username = data.get("username") if data else request.form.get("username")
    password = data.get("password") if data else request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Thiếu thông tin đăng nhập!"}), 400

    user = find_user(username)
    if not user:
        return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu!"}), 401

    # Kiểm tra mật khẩu (hash)
    if not check_password(password, user["password"]):
        return jsonify({"error": "Sai mật khẩu!"}), 401

    # Tạo JWT token
    token = create_access_token(identity=username, expires_delta=timedelta(hours=1))
    update_token(username, token)

    session["username"] = username
    session["token"] = token

    return jsonify({
        "token": token,
        "username": username,
        "message": "Đăng nhập thành công"
    }), 200


# ---------------- API cho Product Service ----------------
@app.route("/auth/verify", methods=["POST"])
def verify_token():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Thiếu token"}), 401

    try:
        decode_token(token)
        return jsonify({"valid": True}), 200
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401


if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=True)
