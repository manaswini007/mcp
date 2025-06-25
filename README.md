#  Super Store MCP - E-Commerce Platform

## able of Contents

1. [Overview](#-overview)
2. [Project Structure](#-project-structure)
3. [Technologies Used](#⚙%ef%b8%8f-technologies-used)
4. [Setup Instructions](#-setup-instructions)

   * [Clone & Setup](#-1-clone--setup)
   * [Install MCP Proxy](#-2-install-mcp-proxy)
   * [Setup MongoDB](#-3-setup-mongodb)
   * [Running the MCP Servers](#-4-running-the-mcp-servers)
   * [Python Commands & Environment](#-5-python-commands--environment)
5. [MCP Proxy Tool Configuration](#-mcp-proxy-tool-configuration)
6. [Services Summary](#⚒%ef%b8%8f-services-summary)
7. [Hosting on EC2 with tmux](#-hosting-on-ec2-with-tmux)
8. [Future Improvements](#-future-improvements)
9. [Author](#-author)
10. [License](#-license)

---

## 📌 Overview

This project is a **modular e-commerce system** integrated with the **Model Context Protocol (MCP)**. It is designed with microservices in mind, dividing the application into three key FastAPI-based servers:

* **Auth Service** - For user registration and login
* **Buyer Service** - For browsing, purchasing, and managing cart
* **Seller Service** - For inventory and order management

All services are integrated using `mcp-proxy` for natural language interaction.

---

## 📁 Project Structure

```
.
├── auth.py                # Auth service (register/login)
├── buyer.py               # Buyer service
├── seller.py              # Seller service
├── utils/
│   ├── db_utils.py        # MongoDB connection
│   └── constant.py        # Collection names
├── requirements.txt       # Python packages
├── venv/                  # Virtual environment
```

---

## ⚙️ Technologies Used

* **FastAPI** - Web API framework
* **MongoDB** - NoSQL database
* **Uvicorn** - ASGI server
* **mcp-proxy** - For connecting with Claude
* **AWS EC2** - Hosting environment
* **tmux** - For managing persistent server sessions on EC2

---

## 🚀 Setup Instructions

### 🔧 1. Clone & Setup

```bash
git clone https://github.com/your-username/super-store-mcp.git
cd super-store-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ✨ 2. Install MCP Proxy

```bash
uv pip install mcp-proxy
```

Or manually:

```bash
mkdir -p ~/mcp-tools
cd ~/mcp-tools
curl -Lo mcp-proxy https://github.com/modelcontext/proxy/releases/latest/download/mcp-proxy-windows-x64.exe
chmod +x mcp-proxy
```

Make sure `mcp-proxy` is available in your PATH or provide the full path in the configuration file.

### 🌿 3. Setup MongoDB

* Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) or local MongoDB
* Update your `utils/db_utils.py` with the correct URI

### 🔌 4. Running the MCP Servers

Start the servers (each in its own terminal or tmux window):

```bash
uvicorn auth:app --host 0.0.0.0 --port 8002
uvicorn buyer:app --host 0.0.0.0 --port 8000
uvicorn seller:app --host 0.0.0.0 --port 8001
```

### 5. Python Commands & Environment

####  Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # For Linux/macOS
venv\Scripts\activate           # For Windows
```

#### 📆 Install Requirements

```bash
pip install -r requirements.txt
```

#### 🚀 Start FastAPI Servers

```bash
uvicorn buyer:app --host 0.0.0.0 --port 8000
uvicorn seller:app --host 0.0.0.0 --port 8001
uvicorn auth:app --host 0.0.0.0 --port 8002
```

####  Deactivate Virtual Environment

```bash
deactivate
```

---

## 🔗 MCP Proxy Tool Configuration

**Claude-compatible configuration (on Windows):**

```json
{
  "mcpServers": {
    "buyer": {
      "command": "C:\\Users\\manas\\.local\\bin\\mcp-proxy.exe",
      "args": ["http://13.204.42.98:8000/mcp"]
    },
    "seller": {
      "command": "C:\\Users\\manas\\.local\\bin\\mcp-proxy.exe",
      "args": ["http://13.204.42.98:8001/mcp"]
    },
    "auth": {
      "command": "C:\\Users\\manas\\.local\\bin\\mcp-proxy.exe",
      "args": ["http://13.204.42.98:8002/mcp"]
    }
  }
}
```

---

##  Services Summary

###  Auth Service

* `/register_user` — Register a new buyer/seller
* `/login_user` — Login and get user role

### Buyer Service

* `/view_products` — See all products
* `/view_cart` — View cart
* `/add_to_cart` — Add product to cart
* `/remove_from_cart` — Remove item from cart
* `/check_balance` — Check user savings
* `/add_balance` — Add money
* `/place_order` — Place final order
* `/view_orders` — See all past orders

### 🏪 Seller Service

* `/add_product` — Add new item to inventory
* `/view_inventory` — View existing products
* `/delete_product` — Remove item
* `/edit_product` — Update price/quantity
* `/view_orders` — View all placed orders

---

## Hosting on EC2 with `tmux`

To persist servers on EC2:

```bash
tmux new -s myservers
# (inside tmux)
source venv/bin/activate
uvicorn buyer:app --host 0.0.0.0 --port 8000
# Open new window in tmux: Ctrl + b, then c
# Repeat for seller and auth
```

To detach: `Ctrl + b`, then `d`
To reattach: `tmux attach -t myservers`

---

## 📋 Future Improvements

* Token-based login/authentication
* Frontend for buyers/sellers
* Product image support
* Deployment via Docker

---

##  Author

**ManasWini**
Student Developer | MCP Integration | AWS EC2 & FastAPI

---

## 📄 License

This project is licensed under the MIT License.
