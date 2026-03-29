# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-XX-XX

### Added

- **Core client** — `MarketoClient` with resource-based API access
- **Authentication** — OAuth 2.0 `client_credentials` flow with automatic token refresh
- **Rate limiting** — Dual-tier sliding window (100/20s) and daily counter (50k/day)
- **Retry logic** — Exponential backoff for transient errors (5xx, 429, auth, network)
- **Pagination** — Transparent token-based and offset-based pagination
- **Error handling** — Structured exception hierarchy mapping all Marketo error codes

#### Resources
- `client.leads` — Get, create/update, delete, merge, describe
- `client.activities` — Query activities, get activity types, paging tokens
- `client.campaigns` — Get, trigger, schedule smart campaigns
- `client.programs` — Browse, create, update, clone, get members
- `client.lists` — Get, add/remove leads, check membership
- `client.folders` — Navigate folder tree, create, get contents
- `client.tokens` — Get, create/update, delete My Tokens
- `client.custom_objects` — List types, describe, CRUD operations
- `client.bulk_import` — CSV upload, job polling, failure/warning retrieval
- `client.bulk_extract` — Lead and activity export with job lifecycle

#### Configuration
- `MarketoConfig` dataclass with all settings
- Environment variable support via `MarketoClient.from_env()`
- Configurable retries, timeouts, rate limits, and logging

#### Documentation
- Full API reference for all 10 resources
- Guides: installation, quickstart, configuration, authentication
- Guides: error handling, rate limiting, pagination, retry logic
- Cookbook: bulk operations, Salesforce sync patterns, common recipes
- Migration guide from other libraries

#### Testing
- Unit tests for config, exceptions, and rate limiter
- GitHub Actions CI workflow (Python 3.9–3.12)
- Linting (ruff), formatting (black), type checking (mypy)
