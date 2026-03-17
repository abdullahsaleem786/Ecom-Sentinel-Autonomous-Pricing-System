# 🛡️ E-Com Sentinel — Phase 1: Data & Feature Engineering

> **The Question Phase 1 Answers:**
> *Do we even have trustworthy, structured data to make autonomous pricing decisions?*

---

## 📌 Overview

Phase 1 is the foundation of E-Com Sentinel. Before any ML model runs, before any agent reasons, before any price gets changed — the data must be clean, structured, and signal-rich.

This phase builds the **data pipeline and feature engineering layer** that every downstream component depends on.

---

## 🗄️ Database Design — 3 Core Tables (SQLite)

### 1. `sales_history`
Tracks historical transactions per product.

| Column | Type | Purpose |
|---|---|---|
| `product_id` | TEXT | Product identifier |
| `date` | DATE | Transaction date |
| `units_sold` | INTEGER | Volume sold |
| `price` | REAL | Price at time of sale |

> **Why it matters:** Informs demand trends. Without this, elasticity cannot be calculated.

---

### 2. `competitor_prices`
Tracks what the market is doing in real time.

| Column | Type | Purpose |
|---|---|---|
| `product_id` | TEXT | Product identifier |
| `competitor_name` | TEXT | Amazon, Flipkart, etc. |
| `competitor_price` | REAL | Their current price |
| `recorded_at` | DATETIME | When signal was captured |

> **Why it matters:** Pricing signal for market behavior. Tells agents whether we're too expensive or too cheap.

---

### 3. `inventory_cost`
Tracks stock levels and cost floors.

| Column | Type | Purpose |
|---|---|---|
| `product_id` | TEXT | Product identifier |
| `current_stock` | INTEGER | Units in warehouse |
| `cost_price` | REAL | Our cost per unit |
| `reorder_threshold` | INTEGER | Min stock before reorder |

> **Why it matters:** Ensures we **never price below a safe margin**. The agent's hard floor.

---

## ⚙️ Feature Engineering — 3 Pricing Signals

Features are computed using a **SQL → Pandas pipeline**:
- **SQL** handles data retrieval, joins, and ordering
- **Pandas** handles ratio calculations, trends, and edge cases

---

### 1. 📉 Price Elasticity

Measures how sensitive demand is to price changes.

```
Price Elasticity = % Change in Units Sold / % Change in Price

% Change in Units Sold = (New Units - Old Units) / Old Units
```

**Example:**
```
Elasticity = -1.2
|Elasticity| > 1 → HIGH elasticity
```

**What it means:**
- Customers are very sensitive to price
- A small price increase causes a **bigger** drop in demand
- This product punishes price hikes

---

### 2. 📦 Inventory Velocity

Measures how fast stock is moving relative to current inventory.

```
Inventory Velocity = Units Sold / Current Stock
```

**Reasoning logic:**
```
Demand dropped after price increase
→ Inventory isn't moving fast
→ Elastic product + slowing sales = danger zone
→ Discount or price correction may be needed
```

---

### 3. 🏷️ Competitor Price Difference

Measures our price gap vs. the market.

```
Competitor Difference = Our Price - Competitor Price
```

**Example:**
```
Our Price:         $20.00
Competitor Price:  $18.50
Difference:        +$1.50  (we are MORE expensive)
```

**Reasoning logic:**
```
Even a small gap hurts on elastic products.
Agent should consider reducing price or matching competitor.
```

---

## 🧠 Pricing Rules (Pre-ML Logic)

Before handing off to ML, explicit rules define when to act:

| Condition | Action |
|---|---|
| Elasticity > 1 + competitor cheaper + stock high | **Decrease price** |
| Elasticity < 1 + competitor more expensive + stock low | **Increase price** |
| Signals mixed or unclear | **No change** |

---

## 🗃️ SQL Window Functions Used

Phase 1 uses SQL window functions and joins to extract signals before Pandas processing:

```sql
-- Elasticity signal per product
SELECT
    product_id,
    price,
    units_sold,
    LAG(price) OVER (PARTITION BY product_id ORDER BY date) AS prev_price,
    LAG(units_sold) OVER (PARTITION BY product_id ORDER BY date) AS prev_units
FROM sales_history;
```

---

## 📋 Feature Contract (Phase 1 Output)

The final output of Phase 1 is a **stable feature DataFrame** that Phase 2 (ML) and Phase 3 (Agents) can trust:

| Feature | Source | Computed In |
|---|---|---|
| `price_elasticity` | sales_history | Pandas |
| `inventory_velocity` | inventory_cost + sales_history | Pandas |
| `competitor_diff` | competitor_prices + inventory_cost | SQL + Pandas |
| `demand_trend` | sales_history (window) | SQL |
| `margin_floor` | inventory_cost | Pandas |

> **Phase 1 rule:** Features are frozen before Phase 2 begins. No silent changes downstream.

---

## 📁 Project Structure (Phase 1)

```
e-com-sentinel/
│
├── data/
│   └── ecom_sentinel.db          # SQLite database
│
├── phase1/
│   ├── schema.sql                 # Table definitions
│   ├── seed_data.py               # Sample data insertion
│   ├── sql_queries.py             # Window functions & joins
│   ├── feature_engineering.py     # Pandas feature calculations
│   └── feature_contract.py        # Frozen output schema
│
└── README.md
```

---

## ✅ Phase 1 Deliverables

- [x] 3-table SQLite schema designed and seeded
- [x] Price elasticity calculated manually and verified
- [x] Inventory velocity logic defined
- [x] Competitor price difference signal extracted
- [x] SQL window functions for demand trends
- [x] SQL vs Pandas responsibility boundary defined
- [x] Edge cases and missing data handled
- [x] Feature contract frozen for Phase 2

---

## 🔜 What Phase 2 Receives

A clean, validated Pandas DataFrame with:
- All 5 features above
- No nulls in critical columns
- Consistent product-level granularity
- Ready for ML model training

---

## 📌 Design Principle

> *No model runs on bad data. No agent reasons on missing signals. Before intelligence, there's infrastructure.*

---

*E-Com Sentinel — Built one phase at a time. 🛡️*

SQLite Data
      ↓
Feature Engineering (Pandas)
      ↓
ML Model (Demand Forecast)
      ↓
Agent System
    ├ Inventory Agent
    ├ Competition Agent
    ├ Risk Agent
      ↓
Pricing Agent (Final Brain)
      ↓
Price Decision

Phase-1  Data Pipeline        ✅
Phase-2  ML Demand Model      ✅
Phase-3  Agent Decision Layer ✅
Phase-4  Real time processing and Decision  ✅
Phase-5  Dashboard Streamlit ✅
