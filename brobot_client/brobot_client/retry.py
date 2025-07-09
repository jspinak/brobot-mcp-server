"""Retry logic and decorators for the Brobot client."""

import time
import asyncio
import functools
import random
from typing import TypeVar, Callable, Optional, Tuple, Type
import logging

from .exceptions import BrobotClientError, BrobotTimeoutError, BrobotConnectionError

logger = logging.getLogger(__name__)

T = TypeVar('T')


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def should_retry(exception: Exception) -> bool:
    """
    Determine if an exception is retryable.
    
    Args:
        exception: The exception that occurred
        
    Returns:
        True if the operation should be retried
    """
    # Retry on connection and timeout errors
    if isinstance(exception, (BrobotConnectionError, BrobotTimeoutError)):
        return True
    
    # Don't retry on client errors (bad requests, etc.)
    return False


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    retry_condition: Optional[Callable[[Exception], bool]] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch (default: all)
        retry_condition: Function to determine if retry should occur
    """
    if exceptions is None:
        exceptions = (Exception,)
    
    if retry_condition is None:
        retry_condition = should_retry
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if not retry_condition(e) or attempt == max_attempts - 1:
                        raise
                    
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    logger.info(
                        f"Retrying {func.__name__} after {delay:.2f}s "
                        f"(attempt {attempt + 1}/{max_attempts}): {e}"
                    )
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if not retry_condition(e) or attempt == max_attempts - 1:
                        raise
                    
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    logger.info(
                        f"Retrying {func.__name__} after {delay:.2f}s "
                        f"(attempt {attempt + 1}/{max_attempts}): {e}"
                    )
                    await asyncio.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RetryableBrobotClient:
    """Mixin class that adds retry capabilities to Brobot clients."""
    
    def __init__(self, *args, max_retries: int = 3, **kwargs):
        """
        Initialize with retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            *args, **kwargs: Passed to parent class
        """
        super().__init__(*args, **kwargs)
        self.max_retries = max_retries
    
    def _with_retry(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
        """
        decorator = retry(max_attempts=self.max_retries)
        wrapped = decorator(func)
        return wrapped(*args, **kwargs)
    
    async def _with_retry_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
        """
        decorator = retry(max_attempts=self.max_retries)
        wrapped = decorator(func)
        return await wrapped(*args, **kwargs)