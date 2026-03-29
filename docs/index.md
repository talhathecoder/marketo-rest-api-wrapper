# Marketo REST API Wrapper — Documentation

Welcome to the documentation for `marketo-rest-api-wrapper`, a comprehensive Python wrapper for the [Marketo REST API](https://developers.marketo.com/rest-api/).

---

## Getting Started

- [Installation & Setup](guides/installation.md)
- [Quick Start](guides/quickstart.md)
- [Configuration](guides/configuration.md)
- [Authentication](guides/authentication.md)

## Core Concepts

- [Error Handling](guides/error-handling.md)
- [Rate Limiting](guides/rate-limiting.md)
- [Pagination](guides/pagination.md)
- [Retry Logic](guides/retry-logic.md)

## API Reference

Complete reference for every resource class, method, parameter, and return type.

| Resource | Description | Reference |
|----------|-------------|-----------|
| `MarketoClient` | Main client entry point | [client.md](api/client.md) |
| `client.leads` | Lead database CRUD | [leads.md](api/leads.md) |
| `client.activities` | Activity log queries | [activities.md](api/activities.md) |
| `client.campaigns` | Smart campaign triggers | [campaigns.md](api/campaigns.md) |
| `client.programs` | Program management | [programs.md](api/programs.md) |
| `client.lists` | Static list operations | [lists.md](api/lists.md) |
| `client.folders` | Folder tree navigation | [folders.md](api/folders.md) |
| `client.tokens` | My Token management | [tokens.md](api/tokens.md) |
| `client.custom_objects` | Custom object CRUD | [custom-objects.md](api/custom-objects.md) |
| `client.bulk_import` | Bulk CSV import | [bulk-import.md](api/bulk-import.md) |
| `client.bulk_extract` | Bulk data export | [bulk-extract.md](api/bulk-extract.md) |

## Guides

- [Bulk Operations Cookbook](guides/bulk-operations.md)
- [Salesforce Sync Patterns](guides/salesforce-sync.md)
- [Common Recipes](guides/recipes.md)
- [Migrating from Other Libraries](guides/migration.md)

## Project

- [Contributing](../CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [License](../LICENSE)
