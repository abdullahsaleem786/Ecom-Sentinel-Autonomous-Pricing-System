# Dockerfile
FROM python:3.13.0-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY agents/        ./agents/
COPY engine/        ./engine/
COPY scripts/       ./scripts/
COPY dashboard/     ./dashboard/
COPY data/          ./data/
COPY models/        ./models/
COPY market_data.db .

# Expose ports
# 8501 = Streamlit dashboard
# 8000 = FastAPI pricing endpoint (Day 3)
EXPOSE 8501
EXPOSE 8000

# Default command runs the dashboard
CMD ["streamlit", "run", "dashboard/pricing_dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]