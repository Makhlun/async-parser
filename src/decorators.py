
import asyncio
import functools
import logging
import aiohttp

logger = logging.getLogger(__name__)

def retry(times=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(1, times+1):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError)  as e:
                    last_error = e
                    status_code = None
                    if isinstance(last_error, aiohttp.ClientResponseError):
                        status_code = last_error.status

                    wait = retry_wait_for(status_code, last_error)
                    
                    logger.warning(f"{func.__name__} ran with attempt {i}/{times} with error: {repr(last_error)}")
                    if i<times:
                        await asyncio.sleep(delay * 2**(i-1) + wait)
            raise last_error
        return wrapper
    return decorator


def retry_wait_for(status_code, e):
    wait = None
    if status_code is not None:
        if status_code>=400 and status_code<500:
            if status_code != 429:
                raise e
            wait = e.headers.get("Retry-After")

        if wait is not None:
            try:
                additional_delay = int(wait)
                logger.warning(f"Waiting for {additional_delay} seconds required.")
                return additional_delay
            except (ValueError, TypeError) as err:
                logger.warning(f"Error in converting {wait}. Except with {err}. Additional delay set to 0.")
    return 0

def rate_limit(delay = 2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args,**kwargs):
            await asyncio.sleep(delay)
            return await func(*args,**kwargs)
        return wrapper
    return decorator


    