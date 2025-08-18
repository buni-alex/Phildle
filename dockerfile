# Stage 1: build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: backend
FROM python:3.12-alpine AS backend
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ .
COPY --from=frontend-build /app/dist ./static 
CMD ["python", "app.py"]  # or your backend start command