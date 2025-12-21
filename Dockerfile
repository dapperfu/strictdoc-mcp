# Use Python 3.11 slim image to avoid tomli dependencies
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed by strictdoc
# (Add any system packages required by strictdoc here if needed)
# Example: RUN apt-get update && apt-get install -y --no-install-recommends <package> && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir .

# Create a non-root user for security and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set entrypoint to run the MCP server
ENTRYPOINT ["strictdoc-mcp"]

