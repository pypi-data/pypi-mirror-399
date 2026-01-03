# Planly Python SDK

Official Python SDK for [Planly](https://planly.dev) subscription validation.

## Installation

```bash
pip install planly
```

## Quick Start

```python
from planly import Planly

# Initialize the client
client = Planly("pln_your_api_key")

# Check subscription
result = client.check("user@example.com")

if result.valid:
    print(f"Active subscription: {result.plan_name}")
else:
    print("No active subscription")
```

## Features

- **Built-in Caching**: Configurable TTL to reduce API calls
- **Auto Retries**: Exponential backoff for reliability  
- **Type Hints**: Full IDE support with type annotations
- **Thread-Safe**: Safe for multi-threaded applications

## Configuration

```python
client = Planly(
    api_key="pln_your_api_key",
    cache_ttl=300,      # Cache for 5 minutes (default)
    max_retries=3,      # Retry attempts (default)
    timeout=10,         # Request timeout in seconds (default)
)
```

## API Reference

### `check(customer_email, use_cache=True, force_refresh=False)`

Returns a `SubscriptionResult` with:
- `valid`: bool - Whether subscription is active
- `status`: str - 'active', 'trial', 'grace_period', 'expired', 'canceled'
- `plan_name`: str - Name of the subscription plan
- `current_period_end`: str - When the current period ends
- `days_remaining`: int - Days until expiration

### `is_valid(customer_email)`

Quick boolean check. Returns `True` if subscription is valid.

### `invalidate(customer_email)`

Remove a specific email from the cache.

### `clear_cache()`

Clear all cached results.

## License

MIT