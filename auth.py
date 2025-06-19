from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from utils.db_utils import db
from utils.constant import USERS_COLLECTION

app = FastAPI()

mcp = FastApiMCP(app, name="Main Store Service", description="User registration and login for Super Store")
mcp.mount()

Users = db[USERS_COLLECTION]

@app.get("/", operation_id="root", summary="Root Endpoint")
def root():
    return {"message": "Main Store MCP server is running"}

@app.post("/register_user", operation_id="register_user", summary="Register a new user")
def register_user(username: str, password: str, role: str):
    """
    Register a user as 'buyer' or 'seller'.
    """
    if Users.find_one({"username": username}):
        return {"error": "User already exists. Please log in instead."}

    Users.insert_one({
        "username": username,
        "password": password,
        "role": role.lower()
    })
    return {"message": f"User '{username}' registered as '{role}'."}

@app.post("/login_user", operation_id="login_user", summary="Login a user")
def login_user(username: str, password: str):
    """
    Authenticate a user and return their role.
    """
    user = Users.find_one({"username": username, "password": password})
    if not user:
        return {"error": "Invalid username or password."}

    role = user.get("role", "unknown")
    return {"message": f"Login successful. You are logged in as '{role}'."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("auth:app", host="127.0.0.1", port=8002)
