# Multi-stage build for production
FROM node:18-alpine AS frontend-build

# Set working directory
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
RUN mkdir -p ./frontend/public
COPY --from=frontend-build /app/frontend/package*.json ./frontend/
COPY --from=frontend-build /app/frontend/next.config.js ./frontend/
COPY --from=frontend-build /app/frontend/tailwind.config.js ./frontend/
COPY --from=frontend-build /app/frontend/postcss.config.js ./frontend/

# Copy course data (handle spaces via JSON array syntax)
COPY ["courses-report.2025-09-04 (7).csv", "/app/"]

# Create non-root user
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application with Gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
