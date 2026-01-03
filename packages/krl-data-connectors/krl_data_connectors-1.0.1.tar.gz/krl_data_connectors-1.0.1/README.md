# KRL Data Connectors

> **Version:** 1.0.0  
> **License:** Apache-2.0 (Open Core), Custom (Pro/Enterprise)  
> **Python:** ≥3.9  
> **Status:** Production

---

## SECTION A — Executive & Strategic Overview

### What This Repository Does

KRL Data Connectors is the **unified data access layer** for the Khipu Intelligence Platform. It provides:

1. **76 Production Connectors** — Verified implementation across socioeconomic, demographic, health, and policy data
2. **3-Tier Access Model** — Community (free, 12 connectors), Professional (paid, 49 connectors), Enterprise (custom, 15 connectors)
3. **42 Billing Modules** — License validation, usage tracking, and quota enforcement (~40K LOC)
4. **Unified API Surface** — Consistent type-safe interfaces across all connectors

### Verified Connector Count (December 2025)

| Tier | Connectors | Status |
|------|------------|--------|
| Community | 12 | ✅ Open source (Apache-2.0) |
| Professional | 49 | ✅ Licensed (subscription) |
| Enterprise | 15 | ✅ Licensed (custom agreement) |
| **Total** | **76** | **Production** |

### Why It Matters to the Business

This repository is **the product** for data-focused customers. Revenue comes from:
- **Pro subscriptions** — Access to 49 Professional connectors + enhanced limits
- **Enterprise contracts** — Access to 15 Enterprise connectors + dedicated support
- **TCU consumption** — Usage-based pricing for data volume

### Current Maturity Level: **PRODUCTION**

| Criterion | Status |
|-----------|--------|
| All 76 connectors implemented | ✅ Yes |
| Base connector architecture | ✅ Stable |
| Billing integration | ✅ 42 modules |
| Type safety | ✅ Complete |
| Test coverage | ⚠️ Reported 0% in coverage.xml |
| PyPI published | ⚠️ Depends on unpublished krl-types |

### Strategic Dependencies

- **Upstream:** krl-premium-backend (proxies all connector requests)
- **Downstream:** krl-types (NOT on PyPI — CRITICAL RISK)
- **Peer:** krl-model-zoo-pro (models consume connector data)

### Known Gaps Blocking Scale

1. **krl-types not on PyPI** — `pip install krl-data-connectors` will fail if pyproject.toml declares krl-types dependency
2. **Billing modules duplicated** — 42 modules here, 40 in krl-premium-backend, must be kept in sync
3. **Test coverage unclear** — coverage.xml exists but shows 0%; actual coverage unknown

---

## SECTION B — Product, Marketing & Sales Intelligence

### Customer-Visible Capabilities

| Tier | Connectors | Domains | Key Sources |
|------|------------|---------|-------------|
| Community | 12 | 8 | FRED, BLS, Census ACS, BEA, World Bank |
| Professional | 49 | 21 | GDELT, NIH, FDA, HRSA, SEC, Treasury, USDA |
| Enterprise | 15 | 6 | Airbyte, Firecrawl, AI/ML integrations |

### Connector Categories (Verified)

| Category | Connectors | Tier Mix |
|----------|------------|----------|
| Economic & Financial | 8 | C/P/E |
| Demographic & Labor | 6 | C/P |
| Health & Wellbeing | 8 | C/P/E |
| Environmental & Climate | 6 | C/P/E |
| Education | 5 | C/P |
| Political & Governance | 4 | P |
| Science & Research | 4 | P |
| Business & Commerce | 4 | P |
| Housing & Urban | 4 | P |
| Media & News | 3 | P |
| Agriculture | 3 | P |
| AI & Web Scraping | 8 | E |
| Other specialized | 13 | P/E |

### Capabilities Safe to Reference in Sales

✅ **Can claim:**
- "76 production-ready data connectors"
- "27+ data domains covered"
- "Unified API across all data sources"
- "Community tier with 12 free connectors"
- "Type-safe Python interfaces"
- "Configurable caching with TTL"

❌ **Cannot claim (not verified):**
- ">78% test coverage" — coverage.xml shows 0%
- "2,098 automated tests" — not verified in codebase
- "99.9% uptime SLA" — no SLA infrastructure

### Differentiators vs Commodity Solutions

1. **Domain-specific connectors** — Not generic HTTP; tailored to each data source
2. **Tier-based access** — Single codebase, license-gated capabilities
3. **Billing integration** — Built-in usage tracking and quota enforcement
4. **Policy-research focus** — Connectors designed for causal inference workflows

---

## SECTION C — Engineering & Development Brief

### Tech Stack (Verified from pyproject.toml)

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | ≥3.9 |
| HTTP | httpx | ≥0.25.0 |
| Schema | Pydantic | ≥2.0 |
| Data | pandas | ≥2.0 |
| Caching | redis | ≥4.0 |
| Type hints | Complete | Yes |

### Repository Structure

```
krl-data-connectors/
├── src/krl_data_connectors/
│   ├── __init__.py              # Package entry
│   ├── base_connector.py        # Abstract base class
│   ├── licensed_connector_mixin.py
│   │
│   ├── community/               # 12 free connectors
│   │   ├── bls_basic.py
│   │   ├── census_acs_public.py
│   │   ├── fred_basic.py
│   │   ├── demographic/
│   │   ├── economic/
│   │   ├── education/
│   │   ├── environmental/
│   │   ├── financial/
│   │   ├── geographic/
│   │   └── health/
│   │
│   ├── professional/            # 49 paid connectors
│   │   ├── fred_full.py
│   │   ├── agricultural/
│   │   ├── business/
│   │   ├── civic/
│   │   ├── cultural/
│   │   ├── demographic/
│   │   ├── economic/
│   │   ├── education/
│   │   ├── energy/
│   │   ├── environmental/
│   │   ├── events/
│   │   ├── financial/
│   │   ├── health/
│   │   ├── housing/
│   │   ├── labor/
│   │   ├── local_gov/
│   │   ├── media/
│   │   ├── mobility/
│   │   ├── political/
│   │   ├── recreation/
│   │   ├── science/
│   │   └── social/
│   │
│   ├── enterprise/              # 15 enterprise connectors
│   │   ├── ai/                  # AI/ML integrations
│   │   ├── airbyte/             # ETL platform
│   │   ├── crime/
│   │   ├── environmental/
│   │   ├── health/
│   │   └── social_services/
│   │
│   ├── core/                    # Infrastructure
│   │   ├── billing/             # 42 billing modules (~40K LOC)
│   │   ├── cache/
│   │   ├── config/
│   │   ├── license/
│   │   └── logging/
│   │
│   └── utils/
│
├── tests/                       # Test suite
├── docs/                        # Documentation
├── examples/                    # Usage examples
├── config/                      # Configuration templates
├── infra/                       # Infrastructure as code
└── pyproject.toml               # Package definition
```

### How to Run (Development)

```bash
# 1. Clone and create environment
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors
python -m venv .venv && source .venv/bin/activate

# 2. Install in development mode
pip install -e ".[dev]"

# 3. Run tests
pytest tests/ -v

# 4. Run linting
make lint

# 5. Use a connector
python -c "
from krl_data_connectors.community import FREDBasicConnector
connector = FREDBasicConnector(api_key='your_key')
data = connector.fetch('GDP')
print(data.head())
"
```

### Configuration

```python
# Connector configuration
from krl_data_connectors import ConnectorConfig

config = ConnectorConfig(
    cache_backend="redis",           # or "memory", "disk"
    cache_ttl=3600,                   # seconds
    retry_attempts=3,
    timeout=30,
)

# With license (Pro/Enterprise)
from krl_data_connectors.professional import FREDFullConnector

connector = FREDFullConnector(
    api_key="your_api_key",
    license_key="your_krl_license",
    config=config,
)
```

### Key Integration Points

| Integration | Method | Notes |
|-------------|--------|-------|
| Backend → Connectors | Python import | Direct library usage |
| License validation | krl-types enums | ⚠️ Not on PyPI |
| Usage tracking | core/billing/ | 42 modules |
| Caching | Redis or memory | Configurable TTL |

### Known Refactor Targets

1. **Remove krl-types dependency** — Or publish krl-types to PyPI
2. **Consolidate billing with backend** — Eliminate duplication
3. **Add test coverage** — Current coverage unknown/0%

---

## SECTION D — Operational & Governance Notes

### Environment Assumptions

- **Development:** No license required; Community tier only
- **Production:** License key required for Pro/Enterprise connectors
- **CI/CD:** Tests should run in Community tier (no secrets)

### Security Considerations

1. **API keys** — Stored in environment variables, never logged
2. **License validation** — Server-side validation via backend
3. **Rate limiting** — Implemented per connector to respect upstream limits
4. **Credential isolation** — Multiple config sources supported

### Compliance Implications

- **Data licensing:** Each data source has its own terms
- **API rate limits:** Respect upstream provider limits
- **PII handling:** Some connectors access demographic data; review handling

### Ownership

- **Team:** KR-Labs Engineering
- **Package:** krl-data-connectors (NOT yet on PyPI due to krl-types)
- **Escalation:** engineering@krlabs.dev

### Maintenance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| krl-types not on PyPI | CRITICAL | Publish or inline types |
| Billing duplication | HIGH | Consolidate with backend |
| Upstream API changes | MEDIUM | Monitor for breaking changes |
| Test coverage unknown | MEDIUM | Add comprehensive tests |

---

## Quick Reference

```python
# Community tier (free)
from krl_data_connectors.community import (
    FREDBasicConnector,
    BLSBasicConnector,
    CensusACSPublicConnector,
)

# Professional tier (licensed)
from krl_data_connectors.professional import (
    FREDFullConnector,
    GDELTConnector,
    NIHReporterConnector,
)

# Enterprise tier (licensed)
from krl_data_connectors.enterprise import (
    AirbyteConnector,
    FirecrawlConnector,
)

# Fetch data
connector = FREDBasicConnector(api_key="your_key")
gdp_data = connector.fetch("GDP", start_date="2020-01-01")
```

---

*Last updated: December 14, 2025 — Forensic audit verified counts*
