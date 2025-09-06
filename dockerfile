# ==========================
# 1. Build frontend
# ==========================
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY phildle-frontend/package*.json ./
RUN npm install
COPY phildle-frontend/ .
RUN npm run build

# ==========================
# 2. Build backend
# ==========================
FROM python:3.10-slim AS backend-build
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libcurl4-openssl-dev \
    libssl-dev \
    libpq-dev \
    python3-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY phildle-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY phildle-backend/ .

# Copy frontend build
COPY --from=frontend-build /app/dist ./static

# ==========================
# 3. Final image: Nginx + Gunicorn
# ==========================
FROM python:3.10-slim
WORKDIR /app

# Install Nginx + Supervisor
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*
# Remove default Nginx site
RUN rm /etc/nginx/sites-enabled/default

# Copy backend + frontend
COPY --from=backend-build /usr/local /usr/local
COPY --from=backend-build /app /app

# Ensure log dirs
RUN mkdir -p /var/log/supervisor

# Nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
