# SecureRetail Analytics — Security Test Report

**Project:** Microsoft Fabric RLS/OLS portfolio project  
**Workspace:** `SecureRetail Analytics`  
**Semantic model:** `sm_secure_retail`  
**Last updated:** 28 October 2026

## Objective

Validate regional row-level security (RLS), sensitive-column object-level security (OLS), and tested direct-source access restrictions for five consumer accounts.

## Configuration under test

- Semantic-model roles: `Retail Dynamic RLS`, `Executive Access`.
- Semantic-model RLS: lowercased `USERPRINCIPALNAME()` is matched against the user-to-region mapping and applied through `gold_dim_region[RegionKey]`.
- Retail role OLS: `Email`, `Phone`, and `Cost` = None.
- Executive role OLS: `Email`, `Phone`, and `Cost` = Read.
- Regional scopes: `regionmanager1` = keys 1–3 (Luzon); `regionmanager2` = keys 4–6 (Visayas); `regionmanager3` = keys 7–9 (Mindanao); `exec1` = keys 1–9.
- Direct Lake semantic-model connection: workspace identity authentication; Entra ID SSO for DirectQuery and Direct Lake is disabled.
- The workspace identity remains in the Lakehouse OneLake `DefaultReader` role so the semantic model can access its source.
- Consumer accounts were removed from the Lakehouse `DefaultReader` role. The tested consumers can still use the report through the semantic model but are restricted from direct Lakehouse access in the tests recorded below.

## Results

### Semantic-model/report tests

| Account | Expected behavior | Observed result | Outcome |
|---|---|---|---|
| `analyst1` | Configured limited regional scope; sensitive columns hidden | Limited to Rizal/Cainta (RegionKey 2); `Email`, `Phone`, and `Cost` inaccessible | Pass |
| `regionmanager1` | Luzon only | Intended Luzon scope (keys 1–3) observed | Pass |
| `regionmanager2` | Visayas only | Intended Visayas scope (keys 4–6) observed | Pass |
| `regionmanager3` | Mindanao only | Intended Mindanao scope (keys 7–9) observed | Pass |
| `exec1` | All regions; sensitive columns readable | All nine regions and intended protected-column access observed | Pass |

### Direct-source access tests

| Test path | Accounts tested | Observed result | Outcome |
|---|---|---|---|
| Direct Lakehouse tables/files | All five consumer accounts listed below | Direct access was restricted after consumers were removed from `DefaultReader` | Pass for tested access attempts |
| SQL analytics endpoint | `analyst1`, `regionmanager1`, `regionmanager2`, `regionmanager3`, `exec1` | Access was restricted for all five accounts | Pass for tested access attempts |
| Semantic-model/report access after source restrictions | All five consumer accounts | Reports continued to load with the expected role-specific behavior | Pass |

**Summary:** All five consumer-account scenarios passed the reported semantic-model/report checks. Direct Lakehouse and SQL analytics endpoint access were also reported as restricted for all five consumer accounts.

## Workspace identity authorized users

At the last review, the workspace identity's **Authorized users** list showed `randy1` with **Can edit members** and the five consumer entries (`Analyst`, `Exec1`, `RM_Luzon`, `RM_Visayas`, `RM Mindanao`) with **Can use identity**. No removal control was visible in the interface. This list has not been changed as part of the tests recorded here.

## Important caveats

This report documents observed test results; it is not a complete end-to-end security certification.

- The workspace identity has broad Lakehouse `DefaultReader` membership to support the current working source-access configuration. A future least-privilege review could evaluate a dedicated OneLake role limited to the required Gold tables, but any change should be tested before adoption.
- Semantic-model OLS and RLS are distinct from OneLake/Lakehouse permissions. The results above describe the specific accounts and access attempts tested; they do not prove every possible API, export, connection, or alternate access path is secure.
- The workspace identity authorized-user list still contains the five consumer entries with **Can use identity**. No removal control was found, and no change to that list is claimed.
- No fresh live test was run as part of this documentation update; results are based on the user's reported tests.

## Recommended follow-up

1. Keep the current working permissions stable unless making a deliberate, reversible change.
2. Evaluate least-privilege OneLake access for the workspace identity in a controlled test, preserving access to the Gold tables required by the semantic model.
3. If the workspace identity authorized-user list must be narrowed, confirm the supported management method before changing permissions.
4. Re-run positive and negative tests after permission, role, connection, or model changes.
5. Store only sanitized evidence in GitHub; never commit credentials, tokens, API keys, personal data, or tenant secrets.
