from flask import Flask, render_template, request, jsonify, redirect, url_for, session
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


# ---------------- Web Giao Diện ----------------
@app.route("/")
def home():
    return redirect(url_for("login_page"))

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        password = data.get("password")

        if find_user(username):
            return render_template("register.html", msg="Tên đăng nhập đã tồn tại!")

        create_user(username, password)
        return redirect(url_for("login_page"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() if request.is_json else request.form
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return render_template("login.html", msg="Thiếu thông tin đăng nhập!")

    user = find_user(username)
    if not user:
        return render_template("login.html", msg="Sai tên đăng nhập hoặc mật khẩu!")

    # Kiểm tra mật khẩu (hash)
    if not check_password(password, user["password"]):
        return render_template("login.html", msg="Sai mật khẩu!")

    # Tạo JWT token
    token = create_access_token(identity=username, expires_delta=timedelta(hours=1))
    update_token(username, token)

    session["username"] = username
    session["token"] = token

    return render_template("success.html", username=username, token=token)


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
    app.run(port=SERVICE_PORT, debug=True)
