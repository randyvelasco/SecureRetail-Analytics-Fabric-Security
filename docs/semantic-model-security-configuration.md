# Semantic Model Security Configuration

**Workspace:** `SecureRetail Analytics`  
**Semantic model:** `sm_secure_retail`  
**Inspection tool:** Tabular Editor 2  
**Backup status:** Partial — the Retail Dynamic RLS expression, the absence of a row filter on Executive Access, and the listed OLS permissions have been inspected in the live model.

## Roles

- `Retail Dynamic RLS`
- `Executive Access`

## Retail Dynamic RLS — row filter

The following DAX expression was copied from Tabular Editor 2:

```dax
VAR CurrentUser = LOWER(USERPRINCIPALNAME())
RETURN
    COUNTROWS(
        FILTER(
            silver_user_region,
            LOWER(silver_user_region[UserEmail]) = CurrentUser
                && silver_user_region[RegionKey] = gold_dim_region[RegionKey]
        )
    ) > 0
```

### Interpretation

1. Gets the current user's sign-in identity using `USERPRINCIPALNAME()` and normalizes it to lowercase.
2. Filters `silver_user_region` to rows where `UserEmail` matches the current user and `RegionKey` matches the current `gold_dim_region` row.
3. Returns `TRUE` when at least one matching user-to-region mapping exists.

The effective result depends on the model's table relationships, permissions, and the access path used. The expression alone does not establish end-to-end security.

## Executive Access — row filter

**Observed in Tabular Editor 2:** No row filter is configured for this role.

This means the role does not apply a role-specific RLS filter on the inspected tables. In the intended setup, Executive Access can therefore see all rows available to the semantic model, subject to other model restrictions and the effective permissions/access path. Confirm role membership is limited to intended executive users.

## Object-level security (OLS)

**Observed in Tabular Editor 2:** The following column permissions are configured:

| Column | Retail Dynamic RLS | Executive Access |
|---|---|---|
| `Email` | None | Read |
| `Phone` | None | Read |
| `Cost` | None | Read |

`None` is intended to prevent users in the Retail Dynamic RLS role from accessing these columns through the semantic model; `Read` permits users in Executive Access to access them, subject to other applicable restrictions and permissions.

## Export and safety notes

- This file documents configuration; it does not deploy or modify the semantic model.
- Review this document against the current live model after changes to roles or permissions.
- Do not commit credentials, tokens, passwords, API keys, personal data, or tenant secrets.
- This is a partial backup, not a complete export of the semantic model or its permissions.
- The OLS settings documented here do not by themselves prove that sensitive data is protected through every access path. Review the Lakehouse/OneLake permissions and Direct Lake access configuration separately.
