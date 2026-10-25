
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root application user
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --home-dir /app appuser

# Copy application source with non-root ownership
COPY --chown=appuser:appgroup . .

# Run the application without root privileges
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
