# Stage 1: build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY phildle-frontend/package*.json ./
RUN npm install
COPY phildle-frontend/ .
RUN npm run build

# Stage 2: backend
FROM python:3.10-slim AS backend-build

WORKDIR /app

# Install system dependencies needed for pycurl, psycopg2, lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libcurl4-openssl-dev \
    libssl-dev \
    libpq-dev \
    python3-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY phildle-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY phildle-backend/ ./

# Copy frontend build into static
COPY --from=frontend-build /app/dist ./static

EXPOSE 5000
CMD ["python", "run.py"]