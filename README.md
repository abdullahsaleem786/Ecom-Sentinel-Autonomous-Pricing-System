# 🛡️ E-Com Sentinel — Autonomous Multi-Agent Pricing Intelligence System

## 🚀 Live Deployment

| Service | URL | Status |
|---------|-----|--------|
| Dashboard | https://ecom-sentinel-autonomous-pricing-system-production.up.railway.app | 🟢 Live |
| Service | URL | Status |
|---------|-----|--------|
| Dashboard | https://ecom-sentinel-autonomous-pricing-system-production.up.railway.app | 🟢 Live |
| Pricing API | https://perceptive-enchantment-production-98cd.up.railway.app | 🟢 Live |
| API Docs | https://perceptive-enchantment-production-98cd.up.railway.app/docs | 🟢 Live |

## 📌 Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Data & Feature Engineering | ✅ Complete |
| Phase 2 | Demand Forecasting (ML) | ✅ Complete |
| Phase 3 | Multi-Agent Pricing System | ✅ Complete |
| Phase 4 | Real-Time Pricing Engine | ✅ Complete |
| Phase 5 | Dashboard & Revenue Simulation | ✅ Complete |
| Phase 6 | Price Optimization Engine | ✅ Complete |
| Phase 7 | Cloud & Production Deployment | ✅ Complete |


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

# 📈 E-Com Sentinel — Phase 2: Demand Forecasting Intelligence

> **The Question Phase 2 Answers:**
> *If the price is X, how many units will likely sell in the next 7 days?*

---

## 📌 Overview

Phase 2 trains a machine learning model to **predict demand under different pricing conditions**. This is not a decision-making layer — it is an advisory layer. The ML model is a calculator, not a boss.

It answers one question precisely and hands the rest off to rules and agents.

---

## 🧠 ML's Role in the System

```
DATA → Features → ML → Rules + Agents → Price Decision
```

### ✅ What ML tells us:
- If price is **X**, how many units will sell in the next 7 days?
- How does demand change when price increases by 5%?
- Is demand likely to drop or remain stable?

### ❌ What ML does NOT decide:
- Whether to increase or decrease the price
- Whether a product is risky
- Whether to match a competitor

> Those decisions belong to **rules + agents**. ML is the advisor. Agents are the decision-makers.

---

## 🎯 Target Variable

```
y = units_sold_next_7_days
```

**Why 7 days?**
- Pricing decisions do not affect demand instantly
- A 7-day window smooths daily noise
- Captures delayed customer reactions
- Reflects how pricing actually works in real e-commerce systems

**Why rows without full future windows are dropped:**
- Prevents incorrect targets
- Eliminates data leakage
- Not related to elasticity — purely a data integrity decision

---

## 🗃️ Dataset Structure

Final DataFrame shape: **(24,281 rows × 20 columns)**

| Column | Source | Role |
|---|---|---|
| `product_id` | sales_history | Identifier |
| `decision_date` | sales_history | Timestamp |
| `price` | sales_history | Feature |
| `price_elasticity` | Phase 1 | Feature |
| `inventory_velocity` | Phase 1 | Feature |
| `price_gap` | Phase 1 | Feature |
| `demand_trend` | Phase 1 | Feature |
| `units_sold_next_7_days` | Engineered | **Target (y)** |

---

## ⚙️ Pipeline

### 1️⃣ Data Sources
- `sales_history` — transaction records
- `competitor_intel` — competitor price signals
- `inventory_cost` — stock levels and cost floors

### 2️⃣ Feature Engineering (from Phase 1)
All features computed and frozen in Phase 1:
- `price`
- `price_elasticity`
- `inventory_velocity`
- `price_gap`
- `demand_trend`

### 3️⃣ Data Cleaning
- Connected SQLite3 → Pandas
- Merged all 3 tables
- Added engineered columns
- Dropped null rows and incomplete future windows
- Committed clean dataset to GitHub

### 4️⃣ Target Variable
- Engineered `units_sold_next_7_days` per product per date

### 5️⃣ Model Training

---

## 📊 Model Results

### Baseline — Day 6/7 Sanity Check

```
Model : Linear Regression
MSE   : 31.84
R²    : -1.43
```

**What this meant:**
- Dataset signal was weak — synthetic data logic was unrealistic
- Nothing was broken — this was exactly what the validation checkpoint was designed to reveal
- A negative R² means the model was worse than predicting the mean

> This is the correct engineering response: **reveal the problem early, fix it deliberately.**

---

### Fixed Model — Day 8

```
Model : Linear Regression
MSE   : 1.92
R²    : 0.93
```

**What this means:**
- The model explains **93% of variance** in demand
- MSE of 1.92 units — tight, production-viable error margin
- Model is now trustworthy enough to pass signals to Rules + Agents

> R² = 0.93 is the green light. Phase 3 can begin.

---

## 📁 Project Structure (Phase 2)

```
e-com-sentinel/
│
├── data/
│   └── ecom_sentinel.db              # SQLite database (Phase 1)
│
├── phase1/
│   └── feature_contract.py           # Frozen feature definitions
│
├── phase2/
│   ├── connect_db.py                 # SQLite3 → Pandas connection
│   ├── build_dataset.py              # Merge tables, engineer target
│   ├── clean_data.py                 # Drop nulls, remove leakage rows
│   ├── train_model.py                # Linear Regression training
│   ├── evaluate_model.py             # MSE, R² reporting
│   └── model.pkl                     # Saved trained model
│
└── README.md
```

---

## ✅ Phase 2 Deliverables

- [x] ML role defined — advisor, not decision-maker
- [x] Target variable engineered (`units_sold_next_7_days`)
- [x] SQLite3 → Pandas pipeline connected
- [x] All 3 tables merged successfully
- [x] Feature columns added and validated
- [x] Null rows and leakage rows dropped
- [x] Dataset committed to GitHub (24,281 × 20)
- [x] Baseline model trained (R² = -1.43 — expected failure)
- [x] Model fixed and retrained (R² = 0.93 ✅)
- [x] Phase 2 validated and frozen

---

## 🔜 What Phase 3 Receives

A trained Linear Regression model (`model.pkl`) that:
- Takes `[price, elasticity, inventory_velocity, price_gap, demand_trend]` as input
- Returns `predicted_units_next_7_days` as output
- Is scoped strictly to demand forecasting — no pricing decisions embedded

Phase 3 (Multi-Agent System) will query this model, interpret the forecast, and make the actual pricing call.

---

## 📌 Design Principle

> *ML is the advisor. Rules and agents are the decision-makers. A model that knows its boundaries is safer than one that doesn't.*

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


# ⚙️ Phase 4: Real-Time Pricing Engine

> **The Question Phase 4 Answers:**
> *Can the system run end-to-end automatically and generate pricing decisions at scale?*

---

## 📌 Overview

Phase 4 transforms the system from isolated components into a **fully orchestrated pipeline**.

All modules — data, ML, agents — are connected into a single executable engine.

---

## 🔄 Engine Workflow

```
SQLite Data
      ↓
Feature Engineering (Pandas)
      ↓
ML Model (Demand Forecast)
      ↓
Agent System
      ↓
Pricing Decision
      ↓
Export Results
```

---

## 🧠 What Was Built

### ✅ Orchestration Engine

* Created `run_pricing_engine.py`
* Controls entire pipeline execution
* Processes **500+ products in one run**

---

### ✅ ML Integration

* Loaded `demand_model.pkl`
* Generated:

  ```
  predicted_units_next_7_days
  ```

---

### ✅ Multi-Agent System Connected

| Agent             | Role                 |
| ----------------- | -------------------- |
| Inventory Agent   | Stock pressure       |
| Competition Agent | Market pricing       |
| Risk Agent        | Elasticity safety    |
| Pricing Agent     | Final decision logic |

---

### ✅ Data Consistency Fixes

* Fixed **feature mismatch errors**
* Fixed **ambiguous truth value bugs**
* Standardized feature pipeline

---

### ✅ Output System

* Generated `recommendations.csv`
* Each row contains:

  * Product
  * Signals
  * Decision
  * Predicted demand

---

## 📊 Result

System runs end-to-end successfully.

---

## ⚠️ Critical Problem Discovered

> Revenue after pricing decisions = **same or worse**

This revealed a **core flaw**:

* System was making *decisions*
* But not doing *optimization*

---

## 📌 Design Insight

> *A system that reacts is not a system that optimizes.*

---

# 📊 Phase 5: Dashboard & Revenue Simulation

> **The Question Phase 5 Answers:**
> *Can we visualize and evaluate pricing decisions clearly?*

---

## 📌 Overview

Phase 5 introduces **visibility and evaluation** using Streamlit.

---

## 🧠 What Was Built

### ✅ Streamlit Dashboard

* Interactive UI for pricing decisions
* Visual representation of:

  * Agent outputs
  * Predictions
  * Decisions

---

### ✅ Revenue Simulation

Simulates:

```
Old Revenue = current_price × actual demand
New Revenue = new_price × predicted demand
```

---

## 📊 Key Finding

> **No meaningful revenue improvement**

---

## ⚠️ Core Issue

Your system was doing:

```
agents → vote → increase/decrease
```

This is:

* Rule-based
* Not optimal
* Not scalable

---

## 📌 Reality Check

> This is where most student projects stop — and fail in real-world evaluation.

---

# 🚀 Phase 6: Price Optimization Engine (CORE BREAKTHROUGH)

> **The Question Phase 6 Answers:**
> *What is the BEST possible price — not just a reasonable one?*

---

## 📌 Overview

Phase 6 replaces decision heuristics with **true optimization logic**.

---

## 🔥 Key Transformation

### ❌ Before:

```
increase / decrease / hold
```

### ✅ After:

```
test multiple prices → predict demand → compute revenue → choose best
```

---

## ⚙️ Optimization Engine

### 📁 New Module

```
engine/price_optimizer.py
```

---

## 🧠 Core Logic

For each product:

```
Test prices:
80%, 90%, 100%, 110%, 120%

For each price:
→ Predict demand
→ Calculate revenue

Select:
→ Price with MAX revenue
```

---

## 📈 Updated Pipeline

```
Dataset
   ↓
Demand Prediction
   ↓
Agent Signals (constraints)
   ↓
Price Optimizer (argmax)
   ↓
Revenue Simulation
   ↓
Dashboard
```

---

# 📅 Phase 6 — Implementation Progress

---

## ✅ Day 1 — Optimization Foundation

### 🔧 Major Changes

* Removed **data leakage** from ML model
* Replaced sklearn model with:

  ```
  Per-product power-law demand curves
  ```
* Average curve performance:

  ```
  R² ≈ 0.905
  Elasticity ≈ -1.4
  ```

---

### 🔁 Pricing Logic Upgrade

* Replaced voting system with:

  ```
  multiplier-based search ranges
  ```

---

### ⚙️ Optimizer Implemented

* Argmax optimization in `run_optimizer.py`
* Revenue computed per candidate price

---

### 📊 Data Improvements

* Seeded realistic dataset:

  * 30 products
  * 365 days
  * 3% noise

---

### ⚠️ Issue Found

* Agents too restrictive:

  ```
  28/30 products → HOLD
  ```

---

## ✅ Day 2 — Fixing Intelligence

### 🔧 Agent Recalibration

| Agent     | Fix                          |
| --------- | ---------------------------- |
| Inventory | Uses price_ratio (0.85–1.11) |
| Risk      | Uses elasticity magnitude    |
| Pricing   | Produces wider valid ranges  |

---

### 🔒 Constraints Added

```
MAX_DISCOUNT = 10%
MAX_INCREASE = 20%
```

---

### 🔁 Simulation Fix

* Baseline revenue now uses **same demand curve**
* Ensures fair comparison

---

### 📊 Result

```
Revenue Lift: +2.42%
All products ≥ baseline
Zero losses ✅
```

---

## ✅ Day 3 — Dashboard Upgrade

### 📊 New Visual Components

* KPI Cards:

  * Baseline Revenue
  * Optimized Revenue
  * Lift %

* Decision Distribution (Donut Chart)

* Price Change Bar Chart (color-coded)

* Revenue Impact Chart

* Product Explorer

* Demand Curve Visualization:

  * Current vs Optimal Price

* Full Optimization Table

---

## 📌 Final System Capability

Your system now:

✅ Predicts demand
✅ Understands market signals
✅ Applies constraints
✅ **Optimizes price mathematically**
✅ Guarantees revenue improvement

---

## 🧠 Final Design Principle

> *Don’t ask “Should we change price?”
> Ask “Which price maximizes revenue under constraints?”*

---

## 🔥 Final Reality

Before Phase 6:

> **Architecture Project**

After Phase 6:

> **AI-Driven Pricing System**

That’s the difference between:

* a student project
* and something that actually *resembles production thinking*

---

# ☁️ Phase 7: Cloud & Production Deployment

> **The Question Phase 7 Answers:**
> *Can this system run continuously in the cloud, serving real pricing decisions to anyone?*

---

## 📌 Overview

Phase 7 takes E-Com Sentinel from a local script to a production system running on cloud infrastructure. Real data, containerized pipeline, live API, public dashboard.

---

## 🔄 What Was Built

### ✅ Day 1 — Real Data Integration

Replaced synthetic data with real Olist Brazilian E-Commerce dataset:

- 30 real products extracted by sales volume
- Real price ranges: $22 – $350
- 8 product categories
- Hybrid demand calibrated to real price distributions
- Price-demand correlation: -0.87
- Demand curves avg R²: 0.750
- Revenue lift on real data: **+3.93%**

---

### ✅ Day 2 — Dockerization

Packaged entire pipeline into a Docker container:
```dockerfile
FROM python:3.13.0-slim
```

- Minimal `requirements.txt` — 10 packages only
- Dashboard service on port 8501
- FastAPI pricing API on port 8000
- Single command to run entire system:
```bash
docker run -p 8501:8501 ecom-sentinel
```

#### FastAPI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/products` | GET | List all product IDs |
| `/optimize` | POST | Get optimal price for a product |
| `/optimize/{product_id}` | GET | Quick optimize by product ID |

---

### ✅ Day 3 — Cloud Deployment

Deployed to Railway cloud infrastructure:

- Connected GitHub repo to Railway
- Docker container deployed to **us-west2**
- Auto-redeploy on every `git push` to master
- Public dashboard URL live

**Live URL:**
```
https://ecom-sentinel-autonomous-pricing-system-production.up.railway.app
```

---

## 🏗️ Production Architecture
```
GitHub (master branch)
        ↓  auto-deploy
Railway Cloud (us-west2)
        ↓
Docker Container
    ├── Streamlit Dashboard  (port 8501)
    └── FastAPI Pricing API  (port 8000)
              ↓
    Per-product demand curves
              ↓
    Price optimizer (argmax)
              ↓
    Optimal price recommendation
```

---

## 📊 Final System Results

| Metric | Value |
|--------|-------|
| Products optimized | 30 real Olist products |
| Demand curve avg R² | 0.750 |
| Revenue lift | +3.93% |
| Revenue losses | 0 |
| Deployment | Live on Railway |
| API response | < 100ms |

---

## 📌 Design Principle

> *A model that runs only on your laptop is not a product. A system that runs in the cloud, serves real data through an API, and redeploys automatically — that is.*

---

*E-Com Sentinel — Built one phase at a time. 🛡️*