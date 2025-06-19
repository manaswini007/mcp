from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from bson import ObjectId

from utils.db_utils import db
from utils.constant import USERS_COLLECTION, INVENTORY_COLLECTION, ORDERS_COLLECTION, CARTS_COLLECTION

app = FastAPI()

mcp = FastApiMCP(app, name="Buyer Service", description="Buyer operations for Super Store")
mcp.mount()

Users = db[USERS_COLLECTION]
Inventory = db[INVENTORY_COLLECTION]
Orders = db[ORDERS_COLLECTION]
Carts = db[CARTS_COLLECTION]

@app.get("/", operation_id="root", summary="Root Endpoint")
def root():
    return {"message": "Buyer MCP server is running"}

@app.get("/view_products", operation_id="view_products", summary="View all products in store")
def view_products():
    products = list(Inventory.find())
    return [{
        "product_id": str(p["_id"]),
        "product": p["product"],
        "price": p["price"],
        "quantity": p["quantity"]
    } for p in products] or {"message": "No products found."}

@app.get("/view_cart", operation_id="view_cart", summary="View contents of the buyer's cart")
def view_cart(buyer: str):
    cart_items = list(Carts.find({"buyer": buyer}))
    if not cart_items:
        return {"message": f"{buyer}'s cart is empty."}
    return [{
        "cart_id": str(item["_id"]),
        "product": item["product"],
        "quantity": item["quantity"],
        "price": item["price"]
    } for item in cart_items]

@app.get("/check_balance", operation_id="check_balance", summary="Check buyer balance by name")
def check_balance(buyer: str):
    user = Users.find_one({"username": buyer})
    if not user:
        return {"error": f"No user found with username: {buyer}"}
    return {"balance": user.get("savings", 0)}

@app.post("/add_balance", operation_id="add_balance", summary="Add balance to buyer account")
def add_balance(buyer: str, amount: float):
    if amount <= 0:
        return {"error": "Amount must be greater than zero."}
    result = Users.update_one({"username": buyer}, {"$inc": {"savings": amount}})
    if result.matched_count == 0:
        return {"error": f"No user found with username: {buyer}"}
    user = Users.find_one({"username": buyer})
    return {"message": f"Balance updated. New balance: ₹{user.get('savings', 0)}"}

@app.post("/add_to_cart", operation_id="add_to_cart", summary="Add item(s) to buyer's cart")
def add_to_cart(buyer: str, product_id: str, quantity: int):
    if quantity <= 0:
        return {"error": "Quantity must be greater than zero."}
    product = Inventory.find_one({"_id": ObjectId(product_id)})
    if not product:
        return {"error": "Product not found."}
    if product["quantity"] < quantity:
        return {"error": f"Insufficient stock for '{product['product']}'."}
    Carts.insert_one({
        "buyer": buyer,
        "product_id": str(product["_id"]),
        "product": product["product"],
        "quantity": quantity,
        "price": product["price"]
    })
    return {"message": f"Added {quantity} of '{product['product']}' to {buyer}'s cart."}

@app.delete("/remove_from_cart", operation_id="remove_from_cart", summary="Remove product from cart")
def remove_from_cart(buyer: str, product_id: str):
    result = Carts.delete_one({"buyer": buyer, "product_id": product_id})
    if result.deleted_count > 0:
        return {"message": "Item removed from cart."}
    return {"error": "Item not found in cart."}

@app.post("/place_order", operation_id="place_order", summary="Place order for all items in cart")
def place_order(buyer: str):
    cart = list(Carts.find({"buyer": buyer}))
    if not cart:
        return {"error": f"{buyer}'s cart is empty."}
    user = Users.find_one({"username": buyer})
    if not user:
        return {"error": f"No user found with username: {buyer}"}
    total = sum(item["price"] * item["quantity"] for item in cart)
    if user.get("savings", 0) < total:
        return {"error": f"Insufficient balance. Total: ₹{total}, Available: ₹{user.get('savings', 0)}"}

    for item in cart:
        product = Inventory.find_one({"_id": ObjectId(item["product_id"])})
        if not product or product["quantity"] < item["quantity"]:
            return {"error": f"Insufficient stock for '{item['product']}'."}

    for item in cart:
        Inventory.update_one({"_id": ObjectId(item["product_id"])}, {"$inc": {"quantity": -item["quantity"]}})
    Users.update_one({"username": buyer}, {"$inc": {"savings": -total}})
    Orders.insert_one({
        "buyer": buyer,
        "items": [{k: v for k, v in item.items() if k != "_id"} for item in cart],
        "total_payment": total,
        "status": "placed"
    })
    Carts.delete_many({"buyer": buyer})
    return {"message": f"Order placed! Total paid: ₹{total}"}

@app.get("/view_orders", operation_id="view_orders", summary="View buyer orders")
def view_orders(buyer: str):
    orders = list(Orders.find({"buyer": buyer}))
    return [{
        "order_id": str(o["_id"]),
        "items": o["items"],
        "total_payment": o["total_payment"],
        "status": o["status"]
    } for o in orders] or {"message": f"No orders found for {buyer}."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("buyer_server:app", host="127.0.0.1", port=8000)
