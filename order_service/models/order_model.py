from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["orderdb"]
orders_collection = db["orders"]
order_items_collection = db["order_items"]

# ==================== ORDERS ====================

def create_order(data, username):
    """Tạo đơn hàng mới"""
    now = datetime.utcnow()
    order = {
        "id": data["id"],
        "customer_name": data["customer_name"],
        "customer_email": data["customer_email"],
        "total_amount": float(data.get("total_amount", 0)),
        "status": data.get("status", "pending"),
        "owner": username,  # người tạo đơn
        "created_at": now,
        "updated_at": now
    }
    result = orders_collection.insert_one(order)
    order["_id"] = str(result.inserted_id)
    order["created_at"] = now.isoformat()
    order["updated_at"] = now.isoformat()
    return order


def get_all_orders(username):
    """Lấy tất cả đơn hàng của user"""
    orders = list(orders_collection.find({"owner": username}, {"_id": 0}))
    for order in orders:
        if isinstance(order.get("created_at"), datetime):
            order["created_at"] = order["created_at"].isoformat()
        if isinstance(order.get("updated_at"), datetime):
            order["updated_at"] = order["updated_at"].isoformat()
    return orders


def get_order_by_id(order_id, username):
    """Lấy thông tin đơn hàng theo ID"""
    order = orders_collection.find_one({"id": order_id, "owner": username}, {"_id": 0})
    if order:
        if isinstance(order.get("created_at"), datetime):
            order["created_at"] = order["created_at"].isoformat()
        if isinstance(order.get("updated_at"), datetime):
            order["updated_at"] = order["updated_at"].isoformat()
    return order


def update_order(order_id, data, username):
    """Cập nhật trạng thái đơn hàng"""
    now = datetime.utcnow()
    update_data = {"updated_at": now}
    
    # Chỉ cập nhật các field được phép
    allowed_fields = ["customer_name", "customer_email", "total_amount", "status"]
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    result = orders_collection.update_one(
        {"id": order_id, "owner": username},
        {"$set": update_data}
    )
    return result.modified_count > 0


def delete_order(order_id, username):
    """Xóa đơn hàng"""
    # Xóa các order items liên quan
    order_items_collection.delete_many({"order_id": order_id, "owner": username})
    
    # Xóa order
    result = orders_collection.delete_one({"id": order_id, "owner": username})
    return result.deleted_count > 0


# ==================== ORDER ITEMS ====================

def create_order_item(data, username):
    """Tạo chi tiết đơn hàng mới"""
    order_item = {
        "id": data["id"],
        "order_id": data["order_id"],
        "product_id": data["product_id"],
        "product_name": data["product_name"],
        "quantity": int(data["quantity"]),
        "unit_price": float(data["unit_price"]),
        "total_price": float(data["quantity"]) * float(data["unit_price"]),
        "owner": username
    }
    result = order_items_collection.insert_one(order_item)
    order_item["_id"] = str(result.inserted_id)
    return order_item


def get_all_order_items(username):
    """Lấy tất cả order items của user"""
    items = list(order_items_collection.find({"owner": username}, {"_id": 0}))
    return items


def get_order_item_by_id(item_id, username):
    """Lấy thông tin order item theo ID"""
    return order_items_collection.find_one({"id": item_id, "owner": username}, {"_id": 0})


def get_order_items_by_order(order_id, username):
    """Lấy tất cả order items của một đơn hàng"""
    items = list(order_items_collection.find({"order_id": order_id, "owner": username}, {"_id": 0}))
    return items


def update_order_item(item_id, data, username):
    """Cập nhật order item"""
    update_data = {}
    
    allowed_fields = ["product_name", "quantity", "unit_price"]
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Tính lại total_price nếu có thay đổi quantity hoặc unit_price
    if "quantity" in update_data or "unit_price" in update_data:
        item = order_items_collection.find_one({"id": item_id, "owner": username})
        if item:
            qty = update_data.get("quantity", item["quantity"])
            price = update_data.get("unit_price", item["unit_price"])
            update_data["total_price"] = float(qty) * float(price)
    
    result = order_items_collection.update_one(
        {"id": item_id, "owner": username},
        {"$set": update_data}
    )
    return result.modified_count > 0


def delete_order_item(item_id, username):
    """Xóa order item"""
    result = order_items_collection.delete_one({"id": item_id, "owner": username})
    return result.deleted_count > 0


def calculate_order_total(order_id, username):
    """Tính tổng tiền của đơn hàng"""
    items = get_order_items_by_order(order_id, username)
    total = sum(item["total_price"] for item in items)
    
    # Cập nhật total_amount vào order
    orders_collection.update_one(
        {"id": order_id, "owner": username},
        {"$set": {"total_amount": total, "updated_at": datetime.utcnow()}}
    )
    
    return total