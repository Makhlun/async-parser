
import time
import functools
import logging
import requests

logger = logging.getLogger(__name__)

def retry(times=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, times+1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_error = e
                    status_code = None
                    if last_error.response is not None:
                        status_code = last_error.response.status_code

                    wait = retry_wait_for(status_code, last_error)
                    
                    logger.warning(f"{func.__name__} ran with attempt {i}/{times} with error: {repr(last_error)}")
                    if i<times:
                        time.sleep(delay * 2**(i-1) + wait)
            raise last_error
        return wrapper
    return decorator


def retry_wait_for(status_code, e):
    wait = None
    if status_code is not None:
        if status_code>=400 and status_code<500:
            if status_code != 429:
                raise e
            wait = e.response.headers.get("Retry-After")

        if wait is not None:
            try:
                additional_delay = int(wait)
                logger.warning(f"Waiting for {additional_delay} seconds required.")
                return additional_delay
            except (ValueError, TypeError) as err:
                logger.warning(f"Error in converting {wait}. Except with {err}. Additional delay set to 0.")
    return 0
