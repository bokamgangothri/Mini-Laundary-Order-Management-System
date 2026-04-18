# 🧺 Mini Laundry Order Management System

A lightweight, full-stack Order Management System for a dry-cleaning store.
Built with **FastAPI** (backend) + vanilla **HTML/CSS/JS** (frontend).

---

## 🚀 Quick Start

### 1. Create & Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn main:app --reload --port 8000
```

### 4. Open the App
- **Frontend Dashboard** → http://localhost:8000
- **Auto Docs (Swagger)** → http://localhost:8000/docs
- **ReDoc**               → http://localhost:8000/redoc

---

## ✅ Features Implemented

- Create laundry orders with customer name, phone, garment list, and bill generation
- List and filter orders by customer name and status
- View order details in a modal with status transitions
- Update order status through the workflow: RECEIVED → PROCESSING → READY → DELIVERED
- Delete orders
- Dashboard metrics for total orders, revenue, and garment revenue breakdown
- Static frontend served by FastAPI from `static/index.html`

---

## 🤖 AI Usage Report

### Tools used
- **GitHub Copilot Chat** — primary assistant for scaffolding, code generation, and debugging
- **Claude (via Copilot)** — architecture review and validation support
- **Local workspace search** — to inspect code and confirm fixes in context

### What AI helped with
- Generated the initial FastAPI project structure and endpoint design
- Suggested Pydantic request models and validation patterns
- Assisted with frontend HTML/CSS/JS layout ideas for a SPA dashboard
- Diagnosed runtime errors such as missing static file paths

### What I fixed / improved manually
- Reworked AI-generated garment payloads into structured `GarmentItem` models
- Changed status update endpoint from `PUT` to semantic `PATCH`
- Added explicit status transition validation to prevent invalid order flows
- Moved `index.html` into `static/` so FastAPI could serve it correctly
- Rewrote frontend interactions to use `fetch()` and SPA state rendering

### Sample prompts used
- "Scaffold a FastAPI project with in-memory database for a laundry OMS. Include Pydantic models for Order with ID, Name, Phone, Garments list, Status (enum), and bill calculation."
- "Write a Python function that calculates a bill: takes a list of {garment_name, quantity} objects and a price catalog dict, returns total amount and garment-wise breakdown."
- "How do I enforce a finite state machine (RECEIVED → PROCESSING → READY → DELIVERED) in FastAPI? Should I use an enum? How to prevent invalid transitions?"
- "Create a dark-themed single-page HTML dashboard with stat cards (total orders, revenue), a filterable orders table, modal for order details, and a new order form. Use vanilla JS, no frameworks."
- "I'm getting `FileNotFoundError: [Errno 2] No such file or directory: '/path/to/static/index.html'`. My `index.html` is in the root. How do I serve it with FastAPI?"

> Full AI workflow notes and prompt journal are available in `AI_USAGE.md`.

---

## 📦 Project Structure
```
laundry_oms/
├── main.py            # FastAPI backend (all business logic)
├── requirements.txt   # Python dependencies
├── README.md
└── static/
    └── index.html     # Frontend dashboard (single-file SPA)
```

---

## 🔌 API Endpoints

| Method   | Endpoint                        | Description                        |
|----------|---------------------------------|------------------------------------|
| `POST`   | `/orders`                       | Create a new order                 |
| `GET`    | `/orders`                       | List all orders (with filters)     |
| `GET`    | `/orders/{order_id}`            | Get a single order                 |
| `PATCH`  | `/orders/{order_id}/status`     | Update order status                |
| `DELETE` | `/orders/{order_id}`            | Delete an order                    |
| `GET`    | `/dashboard`                    | Aggregated metrics & report        |
| `GET`    | `/catalog`                      | List garments and prices           |

### Filters for `GET /orders`
- `?status=RECEIVED` — filter by status
- `?customer_name=rahul` — partial name match

---

## 🔄 Order Status Flow
```
RECEIVED → PROCESSING → READY → DELIVERED
```
Status transitions are enforced — you cannot skip a stage.

---

## 💰 Garment Price Catalog (₹)

| Garment   | Price |
|-----------|-------|
| Shirt     | ₹50   |
| Trouser   | ₹60   |
| Saree     | ₹120  |
| Suit      | ₹200  |
| Jacket    | ₹150  |
| Kurta     | ₹70   |
| Dress     | ₹90   |
| Bedsheet  | ₹100  |
| Blanket   | ₹180  |
| Curtain   | ₹130  |

---

## 🧪 Sample API Calls (curl)

**Create Order:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Rahul Sharma",
    "phone": "9876543210",
    "garments": [
      {"name": "shirt", "quantity": 3},
      {"name": "saree", "quantity": 1}
    ]
  }'
```

**Update Status:**
```bash
curl -X PATCH http://localhost:8000/orders/ORD-XXXXXXXX/status \
  -H "Content-Type: application/json" \
  -d '{"status": "PROCESSING"}'
```

**Dashboard:**
```bash
curl http://localhost:8000/dashboard
```

---

## 🤖 AI Usage Log (for evaluation)

### Prompts Used
1. **Scaffold:** "Scaffold a FastAPI project with in-memory database for a laundry OMS. Include Pydantic models for Order with ID, Name, Phone, Garments list, Status."
2. **Billing:** "Write a Python billing function that takes a list of {name, quantity} garments and a price dict, returns total bill."
3. **Status transitions:** "How do I enforce a finite state machine for order statuses in FastAPI using an enum?"
4. **Frontend:** "Create a dark-themed single-page HTML dashboard with a table, stat cards, and a form — no frameworks."

### Fixes Applied
- AI generated `garments: List[str]` — fixed to `List[GarmentItem]` with proper Pydantic validation
- AI used `PUT` for status update — changed to `PATCH` (semantically correct for partial update)
- AI didn't include status transition validation — added `STATUS_TRANSITIONS` dict manually
- AI's frontend used `form` submit — rewrote with `fetch()` API calls for SPA behavior

---

## ⚖️ Tradeoffs

| Decision | Reasoning |
|----------|-----------|
| In-memory storage | Speed of development; data resets on restart (acceptable for demo) |
| Single HTML file frontend | Zero build step, instantly runnable, easy to demo |
| Pydantic v2 | Better validation error messages out of the box |
| Enforced status transitions | Prevents data integrity bugs in real store scenarios |

