# Fabric artifacts

This directory is reserved for sanitized, version-controlled Microsoft Fabric project artifacts.

## Suggested contents

- `notebooks/`: exported notebook source, such as validation or data preparation notebooks.
- `sql/`: table definitions, validation queries, and other reusable SQL scripts.
- `semantic-model/`: sanitized semantic-model metadata or supported source-format files.
- `pipelines/`: pipeline definitions or documentation.
- `evidence/`: redacted screenshots or test evidence, if appropriate.

Create subdirectories as needed; keep exported artifacts separate from explanatory documentation.

## Before committing

- Remove access tokens, passwords, API keys, connection strings containing secrets, and personal information.
- Do not include production or tenant-sensitive data.
- Verify that identifiers and configuration values are safe to publish.
- Prefer small reproducible source files over screenshots where possible.
- Document the export method and date.

**Current state:** This is a placeholder guide only. Actual Fabric workspace artifacts have not yet been exported or committed here. README documentation does not back up or recreate the live Fabric workspace.
