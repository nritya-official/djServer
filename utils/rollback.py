from contextlib import contextmanager

@contextmanager
def rollback(rollback_func):
    """
        Context manager to execute rollback_func when the decorated function 
        encounters an exception.
        If rollback_func raises an exception, that exception will 
        be propagated; otherwise, the original exception will be re-raised.

        To pass arguments to rollback_func, use functools.partial
    """
    try:
        yield
    except:
        rollback_func()
        raise

