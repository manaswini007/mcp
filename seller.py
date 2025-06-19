from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from bson import ObjectId

from utils.db_utils import db
from utils.constant import USERS_COLLECTION, INVENTORY_COLLECTION

app = FastAPI()

mcp = FastApiMCP(app, name="Seller Service", description="Seller operations for Super Store")
mcp.mount()

Users = db[USERS_COLLECTION]
Inventory = db[INVENTORY_COLLECTION]

@app.get("/", operation_id="root", summary="Root Endpoint")
def root():
    return {"message": "Seller MCP server is running"}

@app.post("/add_item", operation_id="add_item", summary="Add product to inventory")
def add_item(username: str, product: str, price: int, quantity: int, image_url: str):
    if not image_url.startswith("http"):
        return {"error": "Please provide a valid web image URL (starting with http or https)."}
    if price <= 0 or quantity <= 0:
        return {"error": "Price and quantity must be greater than zero."}

    existing = Inventory.find_one({"seller": username, "product": product})
    if existing:
        return {"error": f"Product '{product}' already exists for seller '{username}'."}

    Inventory.insert_one({
        "seller": username,
        "product": product,
        "price": price,
        "quantity": quantity,
        "image_url": image_url
    })
    return {"message": f"Product '{product}' added successfully by seller '{username}'."}

@app.post("/update_item", operation_id="update_item", summary="Update product details")
def update_item(username: str, product: str, upd_price: int, upd_quantity: int):
    if upd_price < 0 or upd_quantity < 0:
        return {"error": "Updated price and quantity must not be negative."}

    result = Inventory.update_one(
        {"seller": username, "product": product},
        {"$set": {"price": upd_price, "quantity": upd_quantity}}
    )

    if result.matched_count > 0:
        return {"message": f"Product '{product}' updated by seller '{username}'."}
    return {"error": f"Product '{product}' not found for seller '{username}'."}

@app.get("/view_seller_products", operation_id="view_seller_products", summary="View seller's products")
def view_seller_products(username: str):
    products = list(Inventory.find({"seller": username}))
    return [{
        "product_id": str(p["_id"]),
        "product": p["product"],
        "price": p["price"],
        "quantity": p["quantity"],
        "image_url": p["image_url"]
    } for p in products] or {"message": f"No products found for seller '{username}'."}

@app.delete("/remove_item", operation_id="remove_item", summary="Remove product from inventory")
def remove_item(username: str, product: str):
    result = Inventory.delete_one({"seller": username, "product": product})
    if result.deleted_count > 0:
        return {"message": f"Product '{product}' removed from seller '{username}' inventory."}
    return {"error": f"Product '{product}' not found for seller '{username}'."}

@app.get("/get_product_image_url", operation_id="get_product_image_url", summary="Get product image URL")
def get_product_image_url(product: str):
    item = Inventory.find_one({"product": product}, {"image_url": 1})
    if not item or "image_url" not in item:
        return {"error": "Image not found for this product."}
    return {"image_markdown": f"![{product}]({item['image_url']})"}

@app.get("/get_product_info_with_image", operation_id="get_product_info_with_image", summary="Get product info with image")
def get_product_info_with_image(product: str):
    item = Inventory.find_one({"product": product})
    if not item:
        return {"error": f"Sorry, we don't have the product '{product}'."}

    image_url = item.get("image_url", "")
    price = item.get("price", "N/A")
    quantity = item.get("quantity", 0)

    if image_url:
        return {
            "info": f"![{product}]({image_url})\n\n Price: ₹{price}\n Stock: {quantity} units."
        }
    else:
        return {
            "info": (
                f"No image for '{product}'.\n"
                f" Price: ₹{price}\n📦 Stock: {quantity} units.\n"
                "Would you like to:\n"
                "1 Proceed to buy anyway?\n"
                "2 Wait for an image?\n"
                "3Check other products?"
            )
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("seller:app", host="127.0.0.1", port=8001)
