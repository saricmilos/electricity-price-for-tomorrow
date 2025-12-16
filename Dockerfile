FROM python:3.12-slim

WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY src ./src
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.plotter:app", "--host", "0.0.0.0", "--port", "8000"]