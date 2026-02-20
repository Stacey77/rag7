# Dockerfile – rag7 AGI Robotics Framework
# Multi-stage build: install deps then copy source.

# ---------------------------------------------------------------------------
# Stage 1: Builder – install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /build

# Install system build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user \
    torch>=2.0.0 \
    torchvision>=0.15.0 \
    numpy>=1.24.0 \
    scipy>=1.10.0 \
    opencv-python-headless>=4.7.0 \
    pyyaml>=6.0 \
    pytest>=7.0.0 \
    pytest-cov>=4.0.0

# ---------------------------------------------------------------------------
# Stage 2: Runtime – lean image with the application
# ---------------------------------------------------------------------------
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Install minimal runtime system libraries (OpenCV needs libGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Ensure user-installed packages are on the path
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app"

# Default command: run the test suite
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
