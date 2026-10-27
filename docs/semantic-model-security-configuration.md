# Semantic Model Security Configuration

**Workspace:** `SecureRetail Analytics`  
**Semantic model:** `sm_secure_retail`  
**Source:** Inspected in Tabular Editor 2  
**Backup status:** Partial — the Retail Dynamic RLS expression below was copied from the live model. Executive Access filter metadata and role-level OLS properties still need to be inspected and recorded.

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

## Executive Access

The project configuration and prior semantic-model tests indicate that this role is intended to allow access to all nine configured regions. The exact deployed filter expression or absence of a filter has **not yet been captured in this document**. Inspect the live role in Tabular Editor 2 before treating that detail as exported.

## Object-level security (OLS)

Previously documented configuration:

| Column | Retail Dynamic RLS | Executive Access |
|---|---|---|
| `Email` | None | Read |
| `Phone` | None | Read |
| `Cost` | None | Read |

These permissions are recorded from prior project testing/configuration notes and still need to be rechecked in Tabular Editor 2 as part of this export.

## Export and safety notes

- This file documents configuration; it does not deploy or modify the semantic model.
- Review this document against the current live model after changes to roles or permissions.
- Do not commit credentials, tokens, passwords, API keys, personal data, or tenant secrets.
- This is a partial backup, not a complete export of the semantic model or its permissions.
