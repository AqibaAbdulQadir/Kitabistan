import time

def call_with_backoff(func, max_retries=3, base_delay=1, max_delay=10):
    """Call a function with exponential backoff on failure."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = min(base_delay * (2 ** attempt), max_delay)
            time.sleep(delay)