# SecureRetail Analytics — Fabric Security Test Report

**Project:** Microsoft Fabric RLS/OLS portfolio project  
**Workspace:** `SecureRetail Analytics`  
**Semantic model:** `sm_secure_retail`  
**Repository:** `randyvelasco/SecureRetail-Analytics-Fabric-Security`  
**Last updated:** 20 November 2026  
**Report status:** Passed for the documented test scenarios

## 1. Objective

Validate dynamic Row-Level Security (RLS), sensitive-column Object-Level Security (OLS), and separation between Power BI semantic-model access and direct Lakehouse/SQL analytics endpoint access.

This report records observed results for five consumer accounts: one analyst, three regional managers, and one executive. It is a portfolio test record, not a formal security certification.

## 2. Test environment and data

| Component | Configuration |
|---|---|
| Fabric workspace | `SecureRetail Analytics` |
| Lakehouse | SecureRetail Lakehouse |
| Semantic model | `sm_secure_retail` |
| Storage | OneLake |
| Semantic model mode | Direct Lake |
| Security controls | Dynamic RLS and OLS |
| Source control | GitHub |

### Validated data volumes

| Table | Rows |
|---|---:|
| `silver_sales` | 20,000 |
| `silver_products` | 100 |
| `silver_customers` | 1,000 |
| `silver_regions` | 9 |
| `silver_dates` | 731 |
| `silver_user_region` | 21 |

The Gold layer contains `gold_fact_sales` (20,000 rows), `gold_dim_date` (731), `gold_dim_product` (100), `gold_dim_customer` (1,000), and `gold_dim_region` (9). Validation reported no key or orphan-record failures.

## 3. Security configuration

### 3.1 Dynamic RLS

The model uses `USERPRINCIPALNAME()` with a lowercased email match against `silver_user_region`. The mapping associates each consumer identity with one or more `RegionKey` values and filters `gold_dim_region`, propagating the filter to sales data.

| Account | Assigned scope |
|---|---|
| `analyst1` | Rizal/Cainta (RegionKey 2) |
| `regionmanager1` | Luzon (RegionKeys 1–3) |
| `regionmanager2` | Visayas (RegionKeys 4–6) |
| `regionmanager3` | Mindanao (RegionKeys 7–9) |
| `exec1` | All nine regions (RegionKeys 1–9) |

### 3.2 OLS

The semantic model has the roles `Retail Dynamic RLS` and `Executive Access`. Both have model Read permission.

| Role | Email | Phone | Cost |
|---|---|---|---|
| `Retail Dynamic RLS` | None | None | None |
| `Executive Access` | Read | Read | Read |

The analyst is subject to the restricted Retail role. The executive receives the Executive Access role for report consumption.

### 3.3 Lakehouse and Direct Lake access

The workspace identity remains in the Lakehouse OneLake `DefaultReader` role to provide the source access required by the Direct Lake semantic model. The `randy1` administrator account also retains its administrative access.

The `DefaultReader` data scope was narrowed to the five Gold tables and `silver_user_region`, which is required by the dynamic RLS expression. `silver_user_access` was removed. The report continued to load after this change and the analyst, executive, and three regional-manager report scenarios were re-tested successfully.

The five consumer accounts were removed from the Lakehouse `DefaultReader` role. Their Power BI report access is provided through the semantic model; it does not imply direct access to the underlying Lakehouse data.

## 4. Semantic-model and report test results

| Account | Expected behavior | Observed result | Outcome |
|---|---|---|---|
| `analyst1` | Only authorized region; sensitive columns hidden | Limited to Rizal/Cainta (RegionKey 2); Email, Phone, and Cost inaccessible | Pass |
| `regionmanager1` | Luzon only | RegionKeys 1–3 visible; other regions filtered | Pass |
| `regionmanager2` | Visayas only | RegionKeys 4–6 visible; other regions filtered | Pass |
| `regionmanager3` | Mindanao only | RegionKeys 7–9 visible; other regions filtered | Pass |
| `exec1` | All regions; sensitive columns readable | All nine regions visible; Email, Phone, and Cost accessible in the Power BI report | Pass |

**Result: 5 of 5 consumer report scenarios passed.**

## 5. Direct-source access test results

The direct-source checks are separate from the Power BI report tests.

| Access path | Consumer accounts | Observed result | Outcome |
|---|---|---|---|
| Direct Lakehouse tables/files | Analyst, all three regional managers, executive | Direct access remained restricted in the tested attempts | Pass |
| SQL analytics endpoint | Analyst, all three regional managers, executive | Direct query/access remained restricted in the tested attempts | Pass |
| Power BI semantic-model/report after source restrictions | All five consumers | Reports continued to load with the expected RLS/OLS behavior | Pass |

The executive's unrestricted reporting access is intentionally distinct from direct data-source access: the executive can see all nine regions and the designated sensitive columns through Power BI, while direct Lakehouse and SQL analytics endpoint access remains restricted.

**Result: Direct-source restrictions passed for the documented consumer access attempts.**

## 6. Workspace identity and permission considerations

The workspace identity is retained in Lakehouse `DefaultReader` for semantic-model source access. Consumer accounts are not members of that Lakehouse role.

An earlier review of the workspace identity's Authorized users list showed `randy1` with **Can edit members** and the five consumer entries (Analyst, Exec1, RM_Luzon, RM_Visayas, RM Mindanao) with **Can use identity**. The interface did not expose a removal control at that time. This report does not claim that those identity-authorized-user entries were removed or changed.

The Lakehouse role membership and the workspace identity's Authorized users list are separate permission surfaces and should not be conflated.

## 7. GitHub source control

The Fabric workspace was exported/synchronized to the repository. The latest recorded workspace Git status was **Synced**, with no pending changes; exported item folders and definition files were visible under `fabric/workspace`.

Repository: https://github.com/randyvelasco/SecureRetail-Analytics-Fabric-Security

Git synchronization preserves supported workspace item definitions. It should not be treated as a complete backup of every runtime setting, permission assignment, credential, secret, or external dependency.

## 8. Scope, limitations, and operational cautions

- Results apply to the named test accounts, configured roles, model relationships, and access paths actually tested. They do not certify every API, export, alternate connection, or possible data-exfiltration path.
- Semantic-model RLS/OLS and OneLake/Lakehouse permissions are separate security layers. Protecting report columns does not, by itself, protect raw source files.
- The workspace identity needs its retained Lakehouse access for the current Direct Lake design. Review that scope if the model architecture changes.
- Do not commit credentials, tokens, API keys, personal data, or tenant secrets. Sanitize screenshots before adding them to the public portfolio repository.
- Re-test after changes to model roles, relationships, workspace membership, Lakehouse permissions, identity settings, or source connections.

## 9. Final assessment

**Overall result: PASS for the documented test scenarios.**

The project demonstrates dynamic regional RLS, sensitive-column OLS, executive-wide Power BI reporting access, and separately restricted direct Lakehouse/SQL endpoint access for the tested consumer accounts. It also demonstrates source control of supported Fabric workspace definitions through GitHub.

The implementation and test evidence provide a practical demonstration of layered security in a Microsoft Fabric Direct Lake environment. This assessment is limited to the documented test scope and should not be represented as a comprehensive security audit.

---

**Project owner:** Randy Velasco  
**Report version:** 1.1  
**Last updated:** 20 November 2026
