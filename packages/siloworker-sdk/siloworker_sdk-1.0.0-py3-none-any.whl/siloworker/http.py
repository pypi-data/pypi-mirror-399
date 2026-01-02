"""HTTP client for SiloWorker API."""

import time
from typing import Any, Dict, Optional, Union
import requests

from .exceptions import SiloWorkerError, AuthenticationError, RateLimitError, ValidationError


class HttpClient:
    """HTTP client for SiloWorker API with retry logic and error handling."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.siloworker.dev",
        timeout: int = 30,
        retries: int = 3,
        debug: bool = False
    ) -> None:
        if not api_key:
            raise ValidationError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.debug = debug
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "siloworker-python-sdk/1.0.0"
        })
    
    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None
    ) -> Any:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{path}"
        timeout = timeout or self.timeout
        max_retries = retries if retries is not None else self.retries
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if self.debug:
                    print(f"[SiloWorker SDK] {method} {url}", data or "")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data and method in ("POST", "PUT", "PATCH") else None,
                    timeout=timeout
                )
                
                if self.debug:
                    print(f"[SiloWorker SDK] Response {response.status_code}")
                
                if not response.ok:
                    raise self._create_error_from_response(response)
                
                # Handle different content types
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return response.json()
                else:
                    return response.text
                    
            except requests.RequestException as e:
                last_error = SiloWorkerError(f"Request failed: {str(e)}")
                
                # Don't retry on client errors (4xx) except rate limits
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    if 400 <= status_code < 500 and status_code != 429:
                        raise last_error
                
                # Don't retry on the last attempt
                if attempt == max_retries:
                    raise last_error
                
                # Exponential backoff
                delay = min(1.0 * (2 ** attempt), 10.0)
                time.sleep(delay)
            
            except SiloWorkerError as e:
                # Don't retry on client errors except rate limits
                if e.status_code and 400 <= e.status_code < 500 and e.status_code != 429:
                    raise e
                
                last_error = e
                if attempt == max_retries:
                    raise e
                
                # Exponential backoff
                delay = min(1.0 * (2 ** attempt), 10.0)
                time.sleep(delay)
        
        if last_error:
            raise last_error
        
        raise SiloWorkerError("Request failed after all retries")
    
    def _create_error_from_response(self, response: requests.Response) -> SiloWorkerError:
        """Create appropriate error from HTTP response."""
        try:
            data = response.json()
            message = data.get("error", f"HTTP {response.status_code} error")
            details = data.get("details")
        except ValueError:
            message = response.text or f"HTTP {response.status_code} error"
            details = None
        
        if response.status_code == 401:
            return AuthenticationError(message)
        elif response.status_code == 429:
            return RateLimitError(message)
        elif response.status_code == 400:
            return ValidationError(message, details)
        else:
            return SiloWorkerError(message, response.status_code)
    
    def get(self, path: str, **kwargs: Any) -> Any:
        """Make GET request."""
        return self.request("GET", path, **kwargs)
    
    def post(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Make POST request."""
        return self.request("POST", path, data, **kwargs)
    
    def put(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Make PUT request."""
        return self.request("PUT", path, data, **kwargs)
    
    def delete(self, path: str, **kwargs: Any) -> Any:
        """Make DELETE request."""
        return self.request("DELETE", path, **kwargs)
