# KRL Open Core

> **Version:** 0.1.0  
> **License:** MIT  
> **Python:** ≥3.9  
> **Status:** Production

---

## SECTION A — Executive & Strategic Overview

### What This Repository Does

KRL Open Core is the **foundation library** shared across all KRL packages. It provides:

1. **Configuration Management** — Environment variables and YAML config
2. **Structured Logging** — JSON-formatted logging with correlation IDs
3. **Caching** — File-based and Redis caching with TTL
4. **API Client Base** — Reusable HTTP client with retry logic
5. **Utilities** — Date parsing, validation, decorators

### Why It Matters to the Business

This repository is **infrastructure code**. Every other KRL package depends on these utilities:
- Consistent logging across all services
- Shared configuration patterns
- Reusable caching layer
- Common HTTP client behavior

### Current Maturity Level: **PRODUCTION**

| Criterion | Status |
|-----------|--------|
| Core utilities implemented | ✅ Yes |
| Logging stable | ✅ Yes |
| Caching stable | ✅ Yes |
| Test coverage | ⚠️ Not measured |
| PyPI published | ⚠️ Not yet |

### Strategic Dependencies

- **Upstream:** None (this is the foundation)
- **Downstream:** All other KRL packages

### Known Gaps

1. **Not on PyPI** — Manual installation required
2. **Test coverage unknown** — No coverage.xml found

---

## SECTION B — Product, Marketing & Sales Intelligence

### Core Utilities

| Utility | Purpose | Status |
|---------|---------|--------|
| `config` | Configuration management | ✅ |
| `logging` | Structured JSON logging | ✅ |
| `cache` | Redis/file caching | ✅ |
| `http` | HTTP client with retries | ✅ |
| `decorators` | Common decorators | ✅ |
| `validation` | Input validation | ✅ |

### Not Customer-Facing

This is infrastructure code. It is not directly visible to customers but affects all KRL products.

---

## SECTION C — Engineering & Development Brief

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python ≥3.9 |
| Config | pydantic-settings |
| Logging | structlog |
| HTTP | httpx |
| Cache | redis |

### Repository Structure

```
krl-open-core/
├── src/
│   └── krl_core/
│       ├── config/         # Configuration management
│       ├── logging/        # Structured logging
│       ├── cache/          # Caching utilities
│       ├── http/           # HTTP client
│       └── utils/          # Common utilities
│
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Build scripts
└── pyproject.toml          # Package definition
```

### How to Run

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Usage Example

```python
from krl_core.config import get_config
from krl_core.logging import get_logger
from krl_core.cache import Cache

# Configuration
config = get_config()

# Logging
logger = get_logger(__name__)
logger.info("Starting process", correlation_id="abc123")

# Caching
cache = Cache(backend="redis")
cache.set("key", "value", ttl=3600)
```

---

## SECTION D — Operational & Governance Notes

### Maintenance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Not on PyPI | MEDIUM | Publish to PyPI |
| Coverage unknown | MEDIUM | Add coverage measurement |
| Breaking changes | HIGH | Version carefully |

### Ownership

- **Team:** KR-Labs Engineering
- **Package:** krl-core (planned PyPI name)
- **Escalation:** engineering@krlabs.dev

---

*Last updated: December 14, 2025 — Forensic audit*
