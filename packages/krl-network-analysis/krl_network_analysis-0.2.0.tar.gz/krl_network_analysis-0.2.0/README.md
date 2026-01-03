# KRL Network Analysis

> **Version:** 1.0.0  
> **License:** Apache-2.0  
> **Python:** ≥3.9  
> **Status:** Production ✅

---

## SECTION A — Executive & Strategic Overview

### What This Repository Does

KRL Network Analysis provides **economic network analysis** tools. It implements:

1. **Network Construction** — Build networks from economic data
2. **Centrality Analysis** — Identify key actors and bottlenecks
3. **Community Detection** — Discover economic clusters
4. **Shock Propagation** — Model cascading effects
5. **Supply Chain Risk** — Identify vulnerabilities

### Current Maturity Level: **PRODUCTION** ✅

| Criterion | Status |
|-----------|--------|
| Core network methods | ✅ Yes |
| Centrality analysis | ✅ Yes |
| Test coverage | ✅ **79.7%** (2166/2718 lines) |
| Branch coverage | ✅ **73.5%** (929/1264 branches) |
| Documentation | ✅ Yes |

**This is the best-tested repository in the KRL suite.**

### Strategic Dependencies

- **Upstream:** krl-premium-backend (API access)
- **Downstream:** None
- **Peer:** krl-geospatial-tools (network + spatial overlap)

### Known Gaps

1. **Coverage gap to 80%** — Close but not quite at target
2. **Branch coverage 73.5%** — Good but could improve

---

## SECTION B — Product, Marketing & Sales Intelligence

### Network Capabilities (Verified)

| Capability | Status |
|------------|--------|
| Economic network construction | ✅ |
| Centrality measures | ✅ |
| Community detection | ✅ |
| Temporal network analysis | ✅ |
| Shock propagation modeling | ✅ |
| Supply chain vulnerability | ✅ |
| Network visualization | ✅ |

### Capabilities Safe to Reference in Sales

✅ **Can claim:**
- "Economic network analysis"
- "Supply chain risk assessment"
- "Shock propagation modeling"
- "Input-output network analysis"
- "Trade network analysis"
- "~80% test coverage"

### Differentiators

1. **Economic focus** — Designed for economic networks, not generic graphs
2. **Supply chain analysis** — Built-in vulnerability detection
3. **Shock modeling** — Cascade effect simulation
4. **High quality** — Best test coverage in KRL suite

---

## SECTION C — Engineering & Development Brief

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python ≥3.9 |
| Graphs | networkx |
| Visualization | plotly, matplotlib |
| Data | pandas, numpy |
| Testing | pytest |

### How to Run

```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=src
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `construction/` | Build networks from data |
| `centrality/` | Centrality measures |
| `community/` | Community detection |
| `dynamics/` | Temporal analysis |
| `risk/` | Vulnerability assessment |
| `visualization/` | Network plots |

### Quality Metrics

```
Coverage: 79.7% (2166/2718 lines)
Branch:   73.5% (929/1264 branches)
```

---

## SECTION D — Operational & Governance Notes

### Maintenance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Coverage gap to 80% | LOW | Add edge case tests |
| Branch coverage gap | LOW | Improve conditional coverage |

### Ownership

- **Team:** KR-Labs Engineering
- **Escalation:** engineering@krlabs.dev

---

*Last updated: December 14, 2025 — Forensic audit verified 79.7% coverage*
