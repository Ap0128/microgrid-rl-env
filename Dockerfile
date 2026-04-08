# ─────────────────────────────────────────────
# Base Image
# ─────────────────────────────────────────────
FROM python:3.11-slim

# ─────────────────────────────────────────────
# Environment Settings
# ─────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─────────────────────────────────────────────
# System Dependencies (IMPORTANT)
# ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# Working Directory
# ─────────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────────
# Install Python Dependencies
# ─────────────────────────────────────────────
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Copy Project Files
# ─────────────────────────────────────────────
COPY . .

# ─────────────────────────────────────────────
# Expose Port (HF Spaces uses 7860)
# ─────────────────────────────────────────────
EXPOSE 7860

# ─────────────────────────────────────────────
# Start Server
# ─────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
