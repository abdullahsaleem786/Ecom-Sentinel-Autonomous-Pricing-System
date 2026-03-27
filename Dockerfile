FROM python:3.13.0-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/        ./agents/
COPY engine/        ./engine/
COPY scripts/       ./scripts/
COPY dashboard/     ./dashboard/
COPY data/          ./data/
COPY models/        ./models/
COPY api/           ./api/
COPY market_data.db .

EXPOSE 8501
EXPOSE 8000

CMD ["streamlit", "run", "dashboard/pricing_dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]