from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["reportdb"]
orders_reports_collection = db["orders_reports"]
product_reports_collection = db["product_reports"]

# ==================== ORDERS REPORTS ====================

def create_order_report(order_id, total_revenue, total_cost, total_profit):
    """Tạo báo cáo đơn hàng mới"""
    now = datetime.utcnow()
    order_report = {
        "id": order_id,  # Dùng order_id làm id chính, có thể tự động generate ID nếu cần
        "order_id": order_id,
        "total_revenue": float(total_revenue),
        "total_cost": float(total_cost),
        "total_profit": float(total_profit),
        "created_at": now,
        "updated_at": now
    }
    result = orders_reports_collection.insert_one(order_report)
    order_report["_id"] = str(result.inserted_id)
    # Tạo id dựa trên inserted_id nếu chưa có
    if "_id" in order_report:
        # Sử dụng _id string để tạo id số
        order_report["report_id"] = str(result.inserted_id)[:8]
    order_report["created_at"] = now.isoformat()
    order_report["updated_at"] = now.isoformat()
    return order_report


def get_all_order_reports():
    """Lấy tất cả báo cáo đơn hàng"""
    reports = list(orders_reports_collection.find({}, {"_id": 0}))
    for report in reports:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return reports


def get_order_report_by_id(report_id):
    """Lấy báo cáo đơn hàng theo ID (có thể là order_id hoặc _id)"""
    # Thử tìm theo order_id trước
    report = orders_reports_collection.find_one({"order_id": int(report_id)}, {"_id": 0})
    if not report:
        # Thử tìm theo id
        report = orders_reports_collection.find_one({"id": int(report_id)}, {"_id": 0})
    
    if report:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return report


def get_order_report_by_order_id(order_id):
    """Lấy báo cáo đơn hàng theo order_id"""
    report = orders_reports_collection.find_one({"order_id": int(order_id)}, {"_id": 0})
    if report:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return report


def delete_order_report(report_id):
    """Xóa báo cáo đơn hàng (sẽ xóa các product_reports liên quan)"""
    # Tìm order_report để lấy order_id
    order_report = get_order_report_by_id(report_id)
    if not order_report:
        return False
    
    order_id = order_report.get("order_id")
    
    # Xóa các product_reports liên quan
    product_reports_collection.delete_many({"order_report_id": order_id})
    
    # Xóa order_report
    result = orders_reports_collection.delete_one({"order_id": order_id})
    return result.deleted_count > 0


# ==================== PRODUCT REPORTS ====================

def create_product_report(order_report_id, product_id, total_sold, revenue, cost, profit):
    """Tạo báo cáo sản phẩm mới"""
    now = datetime.utcnow()
    product_report = {
        "order_report_id": int(order_report_id),
        "product_id": int(product_id),
        "total_sold": int(total_sold),
        "revenue": float(revenue),
        "cost": float(cost),
        "profit": float(profit),
        "created_at": now,
        "updated_at": now
    }
    result = product_reports_collection.insert_one(product_report)
    product_report["id"] = str(result.inserted_id)
    product_report["_id"] = str(result.inserted_id)
    product_report["created_at"] = now.isoformat()
    product_report["updated_at"] = now.isoformat()
    return product_report


def get_all_product_reports():
    """Lấy tất cả báo cáo sản phẩm"""
    reports = list(product_reports_collection.find({}, {"_id": 0}))
    for report in reports:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return reports


def get_product_report_by_id(report_id):
    """Lấy báo cáo sản phẩm theo ID"""
    # Tìm theo id string
    report = product_reports_collection.find_one({"id": str(report_id)}, {"_id": 0})
    if not report:
        # Thử tìm theo MongoDB _id
        from bson import ObjectId
        try:
            report = product_reports_collection.find_one({"_id": ObjectId(str(report_id))}, {"_id": 0})
        except:
            pass
    
    if report:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return report


def get_product_reports_by_order_report_id(order_report_id):
    """Lấy tất cả báo cáo sản phẩm của một order_report"""
    reports = list(product_reports_collection.find({"order_report_id": int(order_report_id)}, {"_id": 0}))
    for report in reports:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return reports


def get_product_reports_by_product_id(product_id):
    """Lấy tất cả báo cáo sản phẩm theo product_id"""
    reports = list(product_reports_collection.find({"product_id": int(product_id)}, {"_id": 0}))
    for report in reports:
        if isinstance(report.get("created_at"), datetime):
            report["created_at"] = report["created_at"].isoformat()
        if isinstance(report.get("updated_at"), datetime):
            report["updated_at"] = report["updated_at"].isoformat()
    return reports


def delete_product_report(report_id):
    """Xóa báo cáo sản phẩm"""
    # Thử xóa theo id
    result = product_reports_collection.delete_one({"id": str(report_id)})
    if result.deleted_count == 0:
        # Thử xóa theo MongoDB _id
        from bson import ObjectId
        try:
            result = product_reports_collection.delete_one({"_id": ObjectId(str(report_id))})
        except:
            pass
    return result.deleted_count > 0


# Thống kê tổng hợp
def get_product_statistics_by_id(product_id):
    """Tính toán thống kê tổng hợp cho một sản phẩm"""
    pipeline = [
        {"$match": {"product_id": int(product_id)}},
        {"$group": {
            "_id": "$product_id",
            "total_sold": {"$sum": "$total_sold"},
            "total_revenue": {"$sum": "$revenue"},
            "total_cost": {"$sum": "$cost"},
            "total_profit": {"$sum": "$profit"}
        }}
    ]
    
    result = list(product_reports_collection.aggregate(pipeline))
    if result:
        stats = result[0]
        stats["product_id"] = stats["_id"]
        del stats["_id"]
        return stats
    return None
