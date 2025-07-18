from functools import cache
import time

def timer(func):
    def wrapper(*args, **kwargs):
        # Use an attribute to track recursion depth
        if not hasattr(wrapper, "depth"):
            wrapper.depth = 0
        is_outermost = wrapper.depth == 0
        wrapper.depth += 1
        if is_outermost:
            start_time = time.perf_counter()
        result = func(*args, **kwargs)
        wrapper.depth -= 1
        if is_outermost:
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            print(f"Function '{func.__name__}' executed in {elapsed:.6f} seconds.")
        return result
    return wrapper

@timer
@cache
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(30)) # with cache 0.000055 seconds, without cache 1.89 seconds
