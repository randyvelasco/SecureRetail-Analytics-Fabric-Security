# SecureRetail Analytics — Microsoft Fabric RLS/OLS

A portfolio project demonstrating dynamic row-level security (RLS) and object-level security (OLS) in a Microsoft Fabric semantic model for a sample retail analytics environment.

> **Security status:** The five documented accounts passed their tested semantic-model scenarios. This is not a claim of complete end-to-end security. Direct Lake, OneLake/Lakehouse permissions, and SSO remain areas for further validation.

## Project goals

- Implement dynamic regional RLS using the signed-in user's identity.
- Restrict sensitive columns with semantic-model OLS.
- Validate analyst, regional manager, and executive access.
- Document expected versus observed behavior and known limitations.
- Keep version-controlled documentation and sanitized project artifacts.

## Architecture

```text
Silver tables
    |
    v
Gold analytical tables
  - gold_fact_sales
  - gold_dim_date
  - gold_dim_product
  - gold_dim_customer
  - gold_dim_region
    |
    v
Microsoft Fabric Direct Lake semantic model
  sm_secure_retail
    |
    +-- Retail Dynamic RLS
    |     USERPRINCIPALNAME() + user-to-region mapping
    |     OLS: Email, Phone, Cost = None
    |
    +-- Executive Access
          All nine regions
          OLS: Email, Phone, Cost = Read
```

## Data model snapshot

| Gold table | Validated row count |
|---|---:|
| `gold_fact_sales` | 20,000 |
| `gold_dim_date` | 731 |
| `gold_dim_product` | 100 |
| `gold_dim_customer` | 1,000 |
| `gold_dim_region` | 9 |

These counts are validation snapshots and may change if sample data is regenerated.

## Semantic-model roles

### `Retail Dynamic RLS`
- Uses `USERPRINCIPALNAME()`, normalized to lowercase.
- Applies the configured user-to-region mapping and filters `gold_dim_region` through `RegionKey`.
- OLS permission for `Email`, `Phone`, and `Cost`: **None**.

### `Executive Access`
- Provides access to all nine configured regions.
- OLS permission for `Email`, `Phone`, and `Cost`: **Read**.

## Regional scope

| RegionKey | Region / area | Intended manager |
|---:|---|---|
| 1 | Luzon — Metro Manila / Manila | `regionmanager1` |
| 2 | Luzon — Rizal / Cainta | `regionmanager1` |
| 3 | Luzon — Pampanga / Angeles | `regionmanager1` |
| 4 | Visayas — Cebu / Cebu City | `regionmanager2` |
| 5 | Visayas — Iloilo / Iloilo City | `regionmanager2` |
| 6 | Visayas — Negros Occidental / Bacolod | `regionmanager2` |
| 7 | Mindanao — Davao del Sur / Davao City | `regionmanager3` |
| 8 | Mindanao — Misamis Oriental / Cagayan de Oro | `regionmanager3` |
| 9 | Mindanao — South Cotabato / General Santos | `regionmanager3` |

The table describes intended manager scopes. Enforcement is based on the configured user-region mapping.

## Security test summary

| Test account | Expected result | Observed result | Status |
|---|---|---|---|
| `analyst1` | Configured regional scope; `Email`, `Phone`, and `Cost` hidden | Limited-scope validation returned Rizal/Cainta; protected columns were inaccessible through the semantic model | PASS — semantic model |
| `regionmanager1` | Luzon only (keys 1–3) | Regional filtering matched configured scope | PASS |
| `regionmanager2` | Visayas only (keys 4–6) | Regional filtering matched configured scope | PASS |
| `regionmanager3` | Mindanao only (keys 7–9) | Regional filtering matched configured scope | PASS |
| `exec1` | All nine regions; protected columns readable | All-region and protected-column access behaved as expected | PASS |

**Result:** 5/5 documented accounts passed the tested semantic-model scenarios. This is not proof that every access path is secure.

See [`docs/security-test-report.md`](docs/security-test-report.md) for the test report and limitations.

## Known limitations and follow-up work

1. **Lakehouse / OneLake boundary:** The analyst was restored to the Lakehouse `DefaultReader` role to resolve a Direct Lake `Missing_References` issue. This may allow underlying data access outside semantic-model RLS/OLS.
2. **OneLake CLS:** The separate `CLSRole` was deleted. Semantic-model OLS tests passed, but OneLake-level column restrictions are not currently the active control for the analyst.
3. **Direct Lake and SSO:** The existing Direct Lake connection has SSO enabled. The interaction between connection identity, semantic-model RLS/OLS, and direct access needs further testing.
4. **Test coverage:** The five documented accounts passed tested scenarios. Alternate access routes, broader negative tests, and all effective permission combinations have not been certified.
5. **Secrets and data:** Never commit tokens, passwords, API keys, personal data, or unredacted tenant secrets.

## Repository structure

```text
.
├── README.md
├── .gitignore
├── docs/
│   └── security-test-report.md
└── fabric/
    └── README.md
```

Add sanitized SQL scripts, notebook source, pipeline definitions, semantic-model metadata, and screenshots under `fabric/` or `docs/` when available. These folders do not automatically back up the live Fabric workspace.

## Reproducibility notes

- Workspace: `SecureRetail Analytics`
- Semantic model: `sm_secure_retail`
- Storage/model approach: Microsoft Fabric Direct Lake over Gold-layer tables
- Test date: 27 October 2026
- Evidence basis: previously observed semantic-model tests and current configuration notes

This repository documents the tested state. Export and add the actual Fabric artifacts separately; this README does not recreate the workspace, model, data, role definitions, or permissions.

## Disclaimer

This is a learning and portfolio project using a sample retail dataset. Revalidate results after changes to roles, permissions, data, connections, or Fabric behavior.
