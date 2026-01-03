import time
import typing
import asyncio
import functools


# ==-----------------------------------------------------------------------------== #
# Decorators                                                                        #
# ==-----------------------------------------------------------------------------== #
def retry(function: typing.Callable | typing.Awaitable | None = None, *, retries: int = 1, retry_delay: int | float = 0.0):
    """Decorator, allows to retry function call if exception raises for several times."""

    # If retry times is invalid value
    if retries <= 0:
        raise Exception("retries argument have to be greated than `0`")

    # If retry interval is invalid value
    if retry_delay < 0:
        raise Exception("delay argument have to be greater or equals `0`")

    # Decorator outer wrapper
    @functools.wraps(function)
    def decorator(function: typing.Callable) -> typing.Callable | typing.Awaitable:
        """Decorator function."""

        # Wrapper for async version of function
        async def async_wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            """Inner wrapper."""

            # Last exception raised on coroutine call
            last_exception = None

            # Trying to call and return result on coroutine while succeed exceeded `retries` + 1 times
            for index, in range(retries + 1):

                try:
                    return await function(*args, **kwargs)

                except BaseException as error:

                    # Saving last exception raised on coroutine call
                    last_exception = error

                # If there a more extra retry call coroutine
                if index != retries:
                    await asyncio.sleep(retry_delay)

            # Raising last saved exception
            raise last_exception

        # Wrapper for sync version of function
        def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            """Inner wrapper."""

            # Last exception raised on coroutine call
            last_exception = None

            # Trying to call and return result on function while succeed exceeded `times` + 1 times
            for index in range(retries + 1):

                try:
                    return function(*args, **kwargs)

                except BaseException as error:

                    # Saving last exception raised on coroutine call
                    last_exception = error

                # If there a more extra retry call coroutine
                if index != retries:
                    time.sleep(retry_delay)

            # Raising last saved exception
            raise last_exception

        # Если функция асинхронная - возврат обёртки корутины, иначе синхронной обёртки
        return async_wrapper if asyncio.iscoroutinefunction(function) else sync_wrapper

    # If function decorated with arguments
    if function is None:
        return decorator

    # If function decorated without arguments
    return decorator(function)
