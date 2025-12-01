# Use Python 3.11 slim as the base
FROM python:3.11-slim

# 1. Install 'uv' efficiently by copying it from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# 2. Environment variables for uv
# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use the virtual environment created by uv
ENV PATH="/app/.venv/bin:$PATH"

# 3. Copy dependency files first (for Docker caching)
# We copy uv.lock if it exists, otherwise just pyproject.toml
COPY pyproject.toml uv.lock* ./

# 4. Install dependencies
# --frozen: strict install from uv.lock (fails if lock is out of sync)
# --no-install-project: we only want dependencies, not the project itself yet
RUN uv sync --frozen --no-install-project

# 5. Copy the rest of the application
COPY streamlit_app.py .

# 6. Streamlit configuration
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run using the environment's streamlit (found via PATH)
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]