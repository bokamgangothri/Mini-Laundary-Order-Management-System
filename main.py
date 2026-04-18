"""
Mini Laundry Order Management System
FastAPI Backend with in-memory storage
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
import uuid
import datetime
import os

app = FastAPI(
    title="Mini Laundry OMS",
    description="Order Management System for a dry cleaning store",
    version="1.0.0"
)

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# GARMENT PRICE CATALOG
# ─────────────────────────────────────────────
GARMENT_PRICES = {
    "shirt":        50.0,
    "trouser":      60.0,
    "saree":       120.0,
    "suit":        200.0,
    "jacket":      150.0,
    "kurta":        70.0,
    "dress":        90.0,
    "bedsheet":    100.0,
    "blanket":     180.0,
    "curtain":     130.0,
}

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class OrderStatus(str, Enum):
    RECEIVED   = "RECEIVED"
    PROCESSING = "PROCESSING"
    READY      = "READY"
    DELIVERED  = "DELIVERED"


class GarmentItem(BaseModel):
    name: str = Field(..., description="Garment type, e.g. 'shirt'")
    quantity: int = Field(..., ge=1, description="Number of pieces")

    @field_validator("name", mode="before")
    def validate_garment_name(cls, v):
        key = v.lower().strip()
        if key not in GARMENT_PRICES:
            raise ValueError(
                f"Unknown garment '{v}'. Valid types: {', '.join(GARMENT_PRICES.keys())}"
            )
        return key


class CreateOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Customer full name")
    phone: str = Field(..., min_length=7, description="Customer phone number")
    garments: List[GarmentItem] = Field(..., min_items=1, description="List of garments")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Rahul Sharma",
                "phone": "9876543210",
                "garments": [
                    {"name": "shirt", "quantity": 3},
                    {"name": "trouser", "quantity": 2},
                    {"name": "saree", "quantity": 1}
                ]
            }
        }


class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    phone: str
    garments: List[GarmentItem]
    status: OrderStatus
    total_bill: float
    created_at: str
    updated_at: str


class StatusUpdateRequest(BaseModel):
    status: OrderStatus

    class Config:
        json_schema_extra = {"example": {"status": "PROCESSING"}}


# ─────────────────────────────────────────────
# IN-MEMORY DATABASE
# ─────────────────────────────────────────────
orders_db: dict[str, dict] = {}


# ─────────────────────────────────────────────
# BILLING ENGINE
# ─────────────────────────────────────────────
def calculate_bill(garments: List[GarmentItem]) -> float:
    """Calculate total bill based on garment types and quantities."""
    total = 0.0
    for item in garments:
        price_per_unit = GARMENT_PRICES.get(item.name.lower(), 0)
        total += price_per_unit * item.quantity
    return round(total, 2)


def generate_order_id() -> str:
    """Generate a short, human-readable order ID."""
    short = str(uuid.uuid4()).replace("-", "").upper()[:8]
    return f"ORD-{short}"


def now_iso() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


# -- 1. Create Order --
@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def create_order(payload: CreateOrderRequest):
    """Create a new laundry order and generate a bill."""
    order_id  = generate_order_id()
    bill      = calculate_bill(payload.garments)
    timestamp = now_iso()

    order = {
        "order_id":      order_id,
        "customer_name": payload.customer_name.strip(),
        "phone":         payload.phone.strip(),
        "garments":      [g.dict() for g in payload.garments],
        "status":        OrderStatus.RECEIVED,
        "total_bill":    bill,
        "created_at":    timestamp,
        "updated_at":    timestamp,
    }
    orders_db[order_id] = order
    return order


# -- 2. List Orders (with optional filters) --
@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_name: Optional[str]  = Query(None, description="Filter by customer name (partial match)"),
):
    """Retrieve all orders with optional filters by status or customer name."""
    results = list(orders_db.values())

    if status:
        results = [o for o in results if o["status"] == status]

    if customer_name:
        q = customer_name.lower()
        results = [o for o in results if q in o["customer_name"].lower()]

    return results


# -- 3. Get Single Order --
@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: str):
    """Retrieve a single order by its ID."""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return order


# -- 4. Update Order Status --
STATUS_TRANSITIONS = {
    OrderStatus.RECEIVED:   [OrderStatus.PROCESSING],
    OrderStatus.PROCESSING: [OrderStatus.READY],
    OrderStatus.READY:      [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED:  [],
}

@app.patch("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(order_id: str, payload: StatusUpdateRequest):
    """
    Update the status of an order.
    Enforces valid transitions: RECEIVED → PROCESSING → READY → DELIVERED
    """
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")

    current_status = order["status"]
    new_status     = payload.status

    if new_status not in STATUS_TRANSITIONS[current_status]:
        allowed = STATUS_TRANSITIONS[current_status]
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {new_status}. "
                   f"Allowed next: {[s.value for s in allowed] or 'None (terminal state)'}",
        )

    order["status"]     = new_status
    order["updated_at"] = now_iso()
    return order


# -- 5. Delete Order --
@app.delete("/orders/{order_id}", status_code=204, tags=["Orders"])
def delete_order(order_id: str):
    """Delete an order (admin use)."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    del orders_db[order_id]
    return None


# -- 6. Dashboard / Report --
@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard():
    """Returns aggregated metrics: total orders, revenue, and status breakdown."""
    all_orders = list(orders_db.values())

    total_orders  = len(all_orders)
    total_revenue = round(sum(o["total_bill"] for o in all_orders), 2)

    status_counts = {s.value: 0 for s in OrderStatus}
    for o in all_orders:
        status_counts[o["status"]] += 1

    # Revenue by garment type
    garment_revenue = {g: 0.0 for g in GARMENT_PRICES}
    for o in all_orders:
        for item in o["garments"]:
            garment_revenue[item["name"]] += GARMENT_PRICES[item["name"]] * item["quantity"]
    garment_revenue = {k: round(v, 2) for k, v in garment_revenue.items() if v > 0}

    return {
        "total_orders":    total_orders,
        "total_revenue":   total_revenue,
        "status_breakdown": status_counts,
        "garment_revenue": garment_revenue,
        "price_catalog":   GARMENT_PRICES,
    }


# -- 7. Price Catalog --
@app.get("/catalog", tags=["Catalog"])
def get_catalog():
    """Returns available garment types and their prices."""
    return {
        "garments": [
            {"name": name, "price_per_unit": price}
            for name, price in GARMENT_PRICES.items()
        ]
    }
