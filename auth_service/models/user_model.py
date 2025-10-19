from pymongo import MongoClient
from config import MONGO_URI
import bcrypt

# Kết nối MongoDB
client = MongoClient(MONGO_URI)
db = client["userdb"]
users = db["users"]

def hash_password(password):
    """Mã hoá mật khẩu bằng bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Kiểm tra mật khẩu có khớp với hash hay không"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(username, password):
    """Tạo user mới với mật khẩu đã hash"""
    hashed_pw = hash_password(password)
    user = {"username": username, "password": hashed_pw, "token": ""}
    users.insert_one(user)
    return user

def find_user(username):
    """Tìm user theo username"""
    return users.find_one({"username": username})

def update_token(username, token):
    """Cập nhật JWT token cho user"""
    users.update_one({"username": username}, {"$set": {"token": token}})
