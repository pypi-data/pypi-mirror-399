"""
Planly Python SDK
=================
A simple, lightweight SDK for validating subscriptions with Planly.

Features:
- Built-in caching with configurable TTL
- Automatic retries with exponential backoff
- Type hints for IDE support
- Thread-safe caching

Installation:
    Save this file as planly.py in your project, or:
    pip install planly  (coming soon)

Usage:
    from planly import Planly
    
    client = Planly("pln_your_api_key")
    result = client.check("user@example.com")
    
    if result.valid:
        print("Access granted!")
"""

import requests
import time
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Any
from functools import wraps


@dataclass
class SubscriptionResult:
    """Result of a subscription validation check."""
    valid: bool
    status: Optional[str] = None
    plan_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    current_period_end: Optional[str] = None
    trial_end_date: Optional[str] = None
    grace_period_end: Optional[str] = None
    days_remaining: Optional[int] = None
    amount_cents: Optional[int] = None
    currency: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubscriptionResult":
        return cls(
            valid=data.get("valid", False),
            status=data.get("status"),
            plan_name=data.get("plan_name"),
            customer_email=data.get("customer_email"),
            customer_name=data.get("customer_name"),
            current_period_end=data.get("current_period_end"),
            trial_end_date=data.get("trial_end_date"),
            grace_period_end=data.get("grace_period_end"),
            days_remaining=data.get("days_remaining"),
            amount_cents=data.get("amount_cents"),
            currency=data.get("currency"),
            message=data.get("message"),
            error=data.get("error"),
        )


class PlanlyCache:
    """Thread-safe in-memory cache with TTL support."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[SubscriptionResult]:
        with self._lock:
            if key in self._cache:
                result, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    return result
                del self._cache[key]
        return None
    
    def set(self, key: str, value: SubscriptionResult) -> None:
        with self._lock:
            self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
    
    def invalidate(self, email: str) -> None:
        with self._lock:
            if email in self._cache:
                del self._cache[email]


class PlanlyError(Exception):
    """Base exception for Planly SDK errors."""
    pass


class PlanlyAPIError(PlanlyError):
    """Raised when the API returns an error."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class PlanlyNetworkError(PlanlyError):
    """Raised when a network error occurs."""
    pass


class Planly:
    """
    Planly SDK client for subscription validation.
    
    Args:
        api_key: Your Planly API key (starts with 'pln_')
        cache_ttl: Cache duration in seconds (default: 300 = 5 minutes)
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 10)
        base_url: API base URL (default: https://api.planly.dev)
    
    Example:
        client = Planly("pln_your_api_key")
        result = client.check("user@example.com")
        
        if result.valid:
            print(f"Active subscription: {result.plan_name}")
        else:
            print("No active subscription")
    """
    
    BASE_URL = "https://api.planly.dev"
    
    def __init__(
        self,
        api_key: str,
        cache_ttl: int = 300,
        max_retries: int = 3,
        timeout: int = 10,
        base_url: str = None,
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self._cache = PlanlyCache(ttl_seconds=cache_ttl)
    
    def check(
        self, 
        customer_email: str, 
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> SubscriptionResult:
        """
        Check if a customer has a valid subscription.
        
        Args:
            customer_email: The customer's email address
            use_cache: Whether to use cached results (default: True)
            force_refresh: Force a fresh API call, ignoring cache (default: False)
        
        Returns:
            SubscriptionResult with validation details
        
        Raises:
            PlanlyAPIError: If the API returns an error
            PlanlyNetworkError: If a network error occurs
        """
        if not customer_email:
            raise ValueError("Customer email is required")
        
        # Check cache first
        if use_cache and not force_refresh:
            cached = self._cache.get(customer_email)
            if cached is not None:
                return cached
        
        # Make API request with retries
        result = self._make_request(customer_email)
        
        # Cache the result
        if use_cache:
            self._cache.set(customer_email, result)
        
        return result
    
    def _make_request(self, customer_email: str) -> SubscriptionResult:
        """Make API request with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/validate",
                    params={
                        "api_key": self.api_key,
                        "customer_email": customer_email,
                    },
                    timeout=self.timeout,
                )
                
                if response.status_code == 200:
                    return SubscriptionResult.from_dict(response.json())
                elif response.status_code == 401:
                    raise PlanlyAPIError("Invalid API key", 401)
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise PlanlyAPIError(
                        f"API error: {response.text}", 
                        response.status_code
                    )
                    
            except requests.exceptions.Timeout:
                last_error = PlanlyNetworkError("Request timed out")
            except requests.exceptions.ConnectionError:
                last_error = PlanlyNetworkError("Connection failed")
            except requests.exceptions.RequestException as e:
                last_error = PlanlyNetworkError(str(e))
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)
        
        raise last_error or PlanlyNetworkError("Request failed after retries")
    
    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
    
    def invalidate(self, customer_email: str) -> None:
        """Invalidate cache for a specific customer."""
        self._cache.invalidate(customer_email)
    
    def is_valid(self, customer_email: str) -> bool:
        """
        Quick check if a customer has valid access.
        
        This is a convenience method that returns just True/False.
        Use check() if you need more details.
        """
        return self.check(customer_email).valid


# Convenience function for simple use cases
def check_subscription(customer_email: str, api_key: str) -> SubscriptionResult:
    """
    One-liner subscription check (no caching).
    
    For repeated checks, create a Planly client instance instead.
    """
    client = Planly(api_key, cache_ttl=0)
    return client.check(customer_email)
