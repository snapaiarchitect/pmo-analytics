# pmo-analytics — Containerized Data Science Portfolio
FROM python:3.10-slim

WORKDIR /app

# Install system deps for data science
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose all dashboard ports
EXPOSE 8511
EXPOSE 8512
EXPOSE 8513
EXPOSE 8514

# Default: show available dashboards
CMD ["python", "-c", "\nprint('  streamlit run capital-portfolio -> http://localhost:8511')\nprint('  streamlit run executive-decision -> http://localhost:8512')\nprint('  streamlit run federal-risk -> http://localhost:8513')\nprint('  streamlit run program-performance -> http://localhost:8514')\n"]
