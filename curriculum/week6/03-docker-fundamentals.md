# Docker Fundamentals

Docker packages your application and all its dependencies into a portable container that runs identically anywhere. This lesson covers the core concepts you need to containerize the expense tracker.


## Why Docker Exists

Consider deploying a Python application to a server. You need:

- The correct Python version (3.12, not 3.11)
- All pip dependencies with exact versions
- System libraries (SQLite headers, SSL certificates)
- Environment variables configured correctly
- File permissions and directory structure
- Process management to keep the app running

Without containerization, you document these requirements in a README and hope the deployment engineer follows them precisely. One missed step or version mismatch causes failures that may take hours to debug.

Docker encapsulates all these requirements in an image that runs the same way on any Linux host (and through virtualization, on macOS and Windows).


## Core Concepts

### Images and Containers

An **image** is a read-only template containing your application code, dependencies, and configuration. Think of it as a snapshot of a filesystem plus instructions for how to run the application.

A **container** is a running instance of an image. You can run multiple containers from the same image, each with its own isolated filesystem and network.

```
+------------------+
|    Docker Image  |   (immutable template)
|  - Python 3.12   |
|  - Your code     |
|  - Dependencies  |
+------------------+
         |
         | docker run
         v
+------------------+    +------------------+
|   Container A    |    |   Container B    |
|   (instance 1)   |    |   (instance 2)   |
+------------------+    +------------------+
```

### Dockerfile

A **Dockerfile** is a text file with instructions for building an image. Each instruction creates a layer in the image:

```dockerfile
# Start from a base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency specification
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install uv && uv pip install --system -e .

# Copy application code
COPY src/ ./src/

# Define how to start the application
CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0"]
```

### Layers and Caching

Docker caches each layer. When you rebuild, unchanged layers are reused:

```dockerfile
# This layer rarely changes - cached
FROM python:3.12-slim

# This layer changes when dependencies change
COPY pyproject.toml uv.lock ./
RUN pip install -e .

# This layer changes frequently - rebuilt often
COPY src/ ./src/
```

Order matters: put frequently-changing instructions last to maximize cache hits.


## Multi-Stage Builds

Production images should be small and contain only runtime dependencies, not build tools. Multi-stage builds achieve this:

```dockerfile
# Stage 1: Builder (larger, has build tools)
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system -e .

# Stage 2: Runtime (minimal, just runs the app)
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0"]
```

The final image contains only what is needed to run the application, not the build tools used to create it.


## The .dockerignore File

Just as `.gitignore` excludes files from version control, `.dockerignore` excludes files from the build context sent to Docker:

```
# Version control
.git
.gitignore

# Virtual environments
.venv
venv/

# Python cache
__pycache__
*.pyc
*.pyo
.pytest_cache

# IDE and editor files
.vscode
.idea
*.swp

# Local data and secrets
.env
*.db
.coverage

# Documentation and curriculum
curriculum/
docs/
*.md

# Test files (if not needed in production)
tests/
```

Benefits:
- Faster builds (smaller context to transfer)
- Smaller images (excluded files never enter layers)
- Security (secrets never copied into image)


## Docker Compose

Running multiple containers (API, Streamlit, database) requires orchestration. Docker Compose manages multi-container applications:

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/expenses.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:8000/api/v1
    depends_on:
      - api
```

Key concepts:

- **services**: Named containers to run
- **build**: Path to Dockerfile (or context + dockerfile)
- **ports**: Map host:container ports
- **environment**: Set environment variables
- **volumes**: Mount host directories into container
- **depends_on**: Control startup order


## Networking in Docker Compose

Services in the same compose file can communicate using service names as hostnames:

```yaml
streamlit:
  environment:
    - API_BASE_URL=http://api:8000/api/v1  # "api" resolves to the API container
  depends_on:
    - api
```

Docker Compose creates a network and registers each service name in DNS.


## Volumes for Persistent Data

Containers are ephemeral: when they stop, their filesystem changes are lost. Volumes persist data outside the container:

```yaml
services:
  api:
    volumes:
      - ./data:/app/data  # Host ./data mounted at /app/data in container
```

For SQLite, this means the database file persists even when the container is recreated.


## Common Docker Commands

```bash
# Build an image
docker build -t expenses-api .

# List images
docker images

# Run a container
docker run -p 8000:8000 expenses-api

# Run with environment variables
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY expenses-api

# Run in background (detached)
docker run -d -p 8000:8000 expenses-api

# List running containers
docker ps

# Stop a container
docker stop <container_id>

# View container logs
docker logs <container_id>

# Remove an image
docker rmi expenses-api
```


## Common Docker Compose Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs

# View logs for specific service
docker-compose logs api

# Validate compose file
docker-compose config

# Rebuild single service
docker-compose build api
```


## Environment Variables

Sensitive values should never be hardcoded in images. Pass them at runtime:

```bash
# From shell environment
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY expenses-api

# From .env file with docker-compose
docker-compose --env-file .env up
```

Docker Compose automatically reads `.env` in the same directory.


## Python Comparison

| Local Development | Docker |
|-------------------|--------|
| `python -m venv .venv` | `FROM python:3.12-slim` |
| `pip install -e .` | `RUN pip install -e .` |
| `.env` file | `-e VAR=value` or compose `environment` |
| `uvicorn app:app` | `CMD ["uvicorn", "app:app"]` |
| Multiple terminal windows | `docker-compose up` |


## Docker for the Expense Tracker

For our project, we will create:

1. **Dockerfile** - Multi-stage build for the FastAPI application
2. **docker-compose.yml** - Orchestrates API and optional Streamlit service
3. **.dockerignore** - Excludes unnecessary files

The result: anyone can clone the repo and run `docker-compose up` to start the entire stack.


## Further Reading

- [Docker Documentation: Getting Started](https://docs.docker.com/get-started/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
