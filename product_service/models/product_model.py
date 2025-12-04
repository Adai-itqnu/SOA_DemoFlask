from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["productdb"]
collection = db["products"]

# CREATE
def create_product(data, username):
    now = datetime.utcnow()
    product = {
        "id": data["id"],
        "name": data["name"],
        "description": data.get("description", ""),
        "price": float(data["price"]),
        "quantity": int(data["quantity"]),
        "owner": username,   # ✅ gắn username người tạo
        "created_at": now,
        "updated_at": now
    }
    result = collection.insert_one(product)
    product["_id"] = str(result.inserted_id)
    product["created_at"] = now.isoformat()
    product["updated_at"] = now.isoformat()
    return product

# READ (all)
def get_all_products():
    return list(collection.find({}, {"_id": 0}))

# READ (by id)
def get_product_by_id(pid):
    return collection.find_one({"id": pid}, {"_id": 0})

# ---- UPDATE ----
def update_product(pid, data, username):
    now = datetime.utcnow()
    update_data = {
        "updated_at": now
    }
    return result.deleted_count > 0

# ---- READ ----
def get_products_by_user(username):
    products = list(collection.find({"owner": username}))
    for p in products:
        p["_id"] = str(p["_id"])
        p["created_at"] = p["created_at"].isoformat()
        p["updated_at"] = p["updated_at"].isoformat()
    return products

# ---- REDUCE QUANTITY OR DELETE ----
def reduce_quantity(pid, amount, username):
    product = collection.find_one({"id": pid, "owner": username})
    if not product:
        return {"error": "Product not found"}

    current_qty = product["quantity"]
    if amount >= current_qty:
        # Xóa hẳn nếu hết hàng
        collection.delete_one({"id": pid, "owner": username})
        return {"message": f"Sản phẩm {product['name']} đã được xóa hoàn toàn."}
    else:
        new_qty = current_qty - amount
        collection.update_one(
            {"id": pid, "owner": username},
            {"$set": {"quantity": new_qty, "updated_at": datetime.utcnow()}}
        )
        return {"message": f"Đã giảm {amount} sản phẩm. Số lượng còn lại: {new_qty}."}