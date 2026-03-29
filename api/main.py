# api/main.py
"""
Phase 7 Day 2 — FastAPI Pricing Endpoint
Serves optimal price recommendations via REST API.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from engine.run_optimizer import optimize_price

app = FastAPI(
    title="E-Com Sentinel Pricing API",
    description="Autonomous pricing optimization engine",
    version="1.0.0"
)

# Load model and features at startup
curves   = joblib.load("models/demand_model.pkl")
features = pd.read_csv("data/processed/pricing_features.csv")

# Latest feature row per product
LATEST = (
    features.sort_values("date")
    .groupby("product_id")
    .last()
    .reset_index()
    .set_index("product_id")
)


class PriceRequest(BaseModel):
    product_id: str
    current_price: float | None = None   # optional override


class PriceResponse(BaseModel):
    product_id:       str
    current_price:    float
    optimal_price:    float
    predicted_demand: float
    optimal_revenue:  float
    decision:         str
    price_change_pct: float
    elasticity:       float


@app.get("/health")
def health():
    return {"status": "ok", "products_loaded": len(LATEST)}


@app.get("/products")
def list_products():
    return {"products": list(LATEST.index)}


@app.post("/optimize", response_model=PriceResponse)
def optimize(request: PriceRequest):
    if request.product_id not in LATEST.index:
        raise HTTPException(
            status_code=404,
            detail=f"Product {request.product_id} not found"
        )

    row = LATEST.loc[request.product_id].copy()

    # Allow price override
    if request.current_price:
        row["price"] = request.current_price

    row["product_id"] = request.product_id
    cost_price = float(row["cost_price"])

    best_price, best_revenue, best_demand, decision = optimize_price(
        row=row,
        model=curves,
        cost_price=cost_price,
    )

    price_change_pct = round(
        (best_price - float(row["price"])) / float(row["price"]) * 100, 2
    )

    elasticity = curves[request.product_id]["b"]

    return PriceResponse(
        product_id       = request.product_id,
        current_price    = round(float(row["price"]), 2),
        optimal_price    = best_price,
        predicted_demand = best_demand,
        optimal_revenue  = best_revenue,
        decision         = decision,
        price_change_pct = price_change_pct,
        elasticity       = round(elasticity, 4),
    )


@app.get("/optimize/{product_id}", response_model=PriceResponse)
def optimize_get(product_id: str):
    return optimize(PriceRequest(product_id=product_id))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


