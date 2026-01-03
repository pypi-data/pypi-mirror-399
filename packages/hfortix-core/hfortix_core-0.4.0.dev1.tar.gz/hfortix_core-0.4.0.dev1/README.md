# HFortix Core

Core foundation package for HFortix - Python SDK for Fortinet products.

## Installation

```bash
pip install hfortix-core
```

## What's Included

- **Exception System**: Common exception hierarchy for all Fortinet SDKs
- **HTTP Client Framework**: Base HTTP client with retry, circuit breaker, and async support
- **Type Definitions**: Shared type aliases and protocols

## Usage

This package is typically used as a dependency by product-specific packages:
- `hfortix-fortios`
- `hfortix-fortimanager`
- `hfortix-fortianalyzer`

For most users, install the product-specific package or the meta-package `hfortix`.
