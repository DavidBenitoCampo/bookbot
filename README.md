<div align="center">

# 📚 BookBot

### Full-Stack Text Analysis Platform with DevOps Best Practices

[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.8%E2%80%933.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

*A production-ready text analysis platform showcasing modern DevOps practices: containerization, CI/CD pipelines, infrastructure automation, and microservices architecture.*

[Architecture](#-architecture) • [DevOps Features](#-devops-features) • [Quick Start](#-quick-start) • [CI/CD](#-cicd-pipeline) • [Docker](#-docker-infrastructure)

</div>

---

## 🎯 Project Overview

This project solves a real problem: **analyzing and extracting insights from large text documents** (books, reports, manuscripts). It combines a Python analysis engine, a REST API, and a modern web dashboard—all containerized and deployed with industry-standard DevOps practices.

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | Python 3.12 + FastAPI | RESTful API for text analysis |
| **Frontend** | Next.js 15 + React 19 | Real-time analytics dashboard |
| **CLI Tool** | Python + Click | Batch processing & automation |
| **Infrastructure** | Docker + Compose | Multi-container orchestration |
| **CI/CD** | GitHub Actions | Automated testing & deployment |
| **Testing** | Pytest + Coverage | Unit & integration tests |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION STACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Next.js    │    │   FastAPI    │    │   BookBot    │      │
│  │   Frontend   │───▶│   Backend    │    │     CLI      │      │
│  │   :3000      │    │   :8000      │    │   (batch)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Docker Compose Network                  │      │
│  │              (bookbot-network)                       │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       CI/CD PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│  Push/PR  ──▶  Lint  ──▶  Test (Matrix)  ──▶  Build  ──▶  Docker│
│                │           │                    │           │   │
│            Black/Flake8  3.9-3.12           Package      Image  │
│            MyPy          Coverage           Artifacts    Cache  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ DevOps Features

<table>
<tr>
<td width="50%">

### 🐳 Containerization
- **Multi-stage Dockerfiles** for optimized images
- **Docker Compose** orchestration (4 services)
- **Healthchecks** for service monitoring
- **Volume mounts** for development workflow
- **Podman compatible** for rootless containers

</td>
<td width="50%">

### 🔄 CI/CD Pipeline
- **GitHub Actions** with matrix testing
- **Python 3.9-3.12** compatibility testing
- **Automated linting** (Black, Flake8, MyPy)
- **Code coverage** with Codecov integration
- **Docker image** build & cache optimization

</td>
</tr>
<tr>
<td>

### 🧪 Testing & Quality
- **Pytest** with coverage reporting
- **Type hints** with MyPy validation
- **Code formatting** with Black
- **Containerized test runner** for isolation
- **Multi-Python version** matrix testing

</td>
<td>

### 🛠️ Automation
- **Makefile** for common operations
- **Release workflow** for versioning
- **Build artifacts** with artifact upload
- **Package distribution** (PyPI-ready)
- **Clean separation** of concerns

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (v2+)
- *Or* Python 3.9+ and Node.js 18+

### One-Command Start

```bash
# Clone and start the full stack
git clone https://github.com/DavidBenitoCampo/bookbot.git
cd bookbot

# Start all services (API + Frontend)
docker-compose up -d

# Access the application
# Frontend Dashboard: http://localhost:3000
# API Documentation: http://localhost:8000/docs
```

### Development Workflow

```bash
# Using Makefile shortcuts
make install-dev    # Install all dependencies
make test           # Run test suite
make lint           # Run linters
make docker         # Build Docker image
make docker-run     # Run in container
```

---

## 🔄 CI/CD Pipeline

### Pipeline Stages

```yaml
# .github/workflows/ci.yml
jobs:
  test:      # Matrix testing: Python 3.9, 3.10, 3.11, 3.12
  lint:      # Black, Flake8, MyPy
  build:     # Package build + Twine check
  docker:    # Docker image build + cache
```

### Features

| Stage | Tool | Purpose |
|-------|------|---------|
| **Testing** | Pytest | Unit & integration tests with coverage |
| **Formatting** | Black | PEP 8 compliant code formatting |
| **Linting** | Flake8 | Code quality & style checking |
| **Type Check** | MyPy | Static type analysis |
| **Package** | Build/Twine | Python package validation |
| **Container** | Docker Buildx | Multi-arch image builds with caching |

### Triggers

- ✅ **Push** to `main` or `develop` branches
- ✅ **Pull Requests** to `main` branch
- ✅ **Release tags** for production deployments

---

## 🐳 Docker Infrastructure

### Multi-Container Architecture

```yaml
services:
  api:           # FastAPI backend (port 8000)
  web:           # Next.js frontend (port 3000)
  bookbot:       # CLI tool (profile: cli)
  bookbot-test:  # Test runner (profile: test)
```

### Dockerfile Strategy

| Dockerfile | Purpose | Optimizations |
|------------|---------|---------------|
| `Dockerfile` | Production CLI | Multi-stage, minimal base |
| `Dockerfile.api` | FastAPI backend | Uvicorn, healthcheck |
| `Dockerfile.test` | Test runner | Dev dependencies, coverage |
| `web/Dockerfile.dev` | Frontend dev | Hot reload, volumes |

### Commands

```bash
# Build all images
docker-compose build

# Start full stack (API + Frontend)
docker-compose up -d

# Run CLI in container
docker-compose --profile cli run --rm bookbot books/frankenstein.txt

# Run tests in container
docker-compose --profile test run --rm bookbot-test

# View logs
docker-compose logs -f api

# Check health status
docker-compose ps
```

---

## 🧪 Testing Strategy

### Local Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest tests/ -v --cov=src/bookbot --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py -v
```

### Containerized Testing

```bash
# Run tests in isolated container
docker-compose --profile test run --rm bookbot-test

# Custom test command
docker-compose --profile test run --rm bookbot-test \
  pytest tests/ -v --tb=long --cov=src/bookbot
```

---

## 📁 Project Structure

```
bookbot/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline (test, lint, build, docker)
│       └── release.yml         # Release automation
├── api/
│   └── main.py                 # FastAPI application
├── web/                        # Next.js frontend
│   ├── app/                    # App router pages
│   ├── components/             # React components
│   └── Dockerfile.dev          # Development container
├── src/bookbot/                # Python library
│   ├── analyzer.py             # Core analysis engine
│   ├── report.py               # Report generation
│   └── visualizer.py           # Chart generation
├── tests/                      # Test suites
├── Dockerfile                  # Production CLI image
├── Dockerfile.api              # API server image
├── Dockerfile.test             # Test runner image
├── docker-compose.yml          # Multi-container orchestration
├── Makefile                    # Development automation
├── pyproject.toml              # Package configuration
└── requirements.txt            # Python dependencies
```

---

## 🛠️ Technologies Used

### Infrastructure & DevOps
- **Docker** & **Docker Compose** - Containerization
- **GitHub Actions** - CI/CD automation
- **Makefile** - Task automation

### Backend
- **Python 3.12** - Core language
- **FastAPI** - REST API framework
- **Pytest** - Testing framework
- **Black/Flake8/MyPy** - Code quality

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization

---

## 📊 Metrics & Monitoring

### Healthchecks

```yaml
# API healthcheck in docker-compose.yml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Coverage Reporting

- **Codecov** integration for coverage tracking
- **HTML reports** for local development
- **XML export** for CI integration

---

## 🤝 Contributing

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/bookbot.git
cd bookbot

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, then test
make lint
make test

# Commit and push
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature

# Open Pull Request
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with DevOps Best Practices** 🚀

[Docker](https://www.docker.com/) • [GitHub Actions](https://github.com/features/actions) • [Python](https://www.python.org/) • [Next.js](https://nextjs.org/)

**[David Benito Campo](https://github.com/DavidBenitoCampo)**

</div>
