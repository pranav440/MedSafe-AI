# Build Stage for Frontend
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY medsafe-insight-main/package*.json ./
RUN npm install
COPY medsafe-insight-main/ ./
# Use relative paths for the API in production
ENV VITE_API_URL=""
RUN npm run build

# Final Stage
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose ports (Railway uses $PORT env var)
ENV PYTHONUNBUFFERED=1

# Start Flask directly (Simulator starts as a thread inside Flask)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 api.app:app
