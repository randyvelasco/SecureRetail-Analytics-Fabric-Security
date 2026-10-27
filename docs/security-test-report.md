# SecureRetail Analytics — Security Test Report

**Project:** Microsoft Fabric RLS/OLS portfolio project  
**Workspace:** `SecureRetail Analytics`  
**Semantic model:** `sm_secure_retail`  
**Test date:** 27 October 2026

## Objective

Validate configured regional row-level security (RLS) and sensitive-column object-level security (OLS) for five test accounts in the semantic-model/report path.

## Configuration under test

- Semantic-model roles: `Retail Dynamic RLS`, `Executive Access`
- RLS: lowercased `USERPRINCIPALNAME()` matched against the user-to-region mapping and applied through `gold_dim_region[RegionKey]`.
- Retail role OLS: `Email`, `Phone`, and `Cost` = None.
- Executive role OLS: `Email`, `Phone`, and `Cost` = Read.
- Regional scopes: manager 1 = keys 1–3 (Luzon); manager 2 = keys 4–6 (Visayas); manager 3 = keys 7–9 (Mindanao); executive = keys 1–9.

## Results

| Account | Expected behavior | Observed result | Outcome |
|---|---|---|---|
| `analyst1` | Configured limited regional scope; sensitive columns hidden | Validation returned Rizal/Cainta; protected columns inaccessible through semantic model | Pass for tested semantic-model path |
| `regionmanager1` | Luzon only | Matched configured regional scope | Pass |
| `regionmanager2` | Visayas only | Matched configured regional scope | Pass |
| `regionmanager3` | Mindanao only | Matched configured regional scope | Pass |
| `exec1` | All regions; sensitive columns readable | All-region and protected-column access behaved as expected | Pass |

**Summary:** 5/5 documented account scenarios passed for the semantic-model/report path tested.

## Important caveats

This is not a complete end-to-end security certification.

- The analyst was restored to the Lakehouse `DefaultReader` role to resolve a Direct Lake `Missing_References` error. That permission may permit access to underlying data outside semantic-model RLS/OLS.
- The separate OneLake `CLSRole` was deleted. OneLake-level column restrictions are not currently the active analyst control.
- The Direct Lake connection has SSO enabled. Its effective identity and the interaction with semantic-model RLS/OLS and direct data access require further validation.
- The tests cover the five documented accounts and observed paths only; they do not prove that all possible access paths are secure.

## Recommended follow-up

1. Test effective permissions through every supported access path, including direct Lakehouse/OneLake access and semantic-model/report access.
2. Review whether Lakehouse `DefaultReader` access is required and whether it conflicts with the intended security boundary.
3. Reassess OneLake security/CLS requirements and validate them independently of semantic-model OLS.
4. Re-run positive and negative tests after permission, role, connection, or model changes.
5. Store only sanitized evidence in GitHub; never commit credentials, tokens, API keys, personal data, or tenant secrets.

## Evidence note

This report records the project state and results previously observed on 27 October 2026. It does not include a fresh live test run or replace tenant-specific security review.
