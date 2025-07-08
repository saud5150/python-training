# def simple_decorator(func):
#     def wrapper():
#         print("Before the function call.")
#         func()
#         print("After the function call.")
#     return wrapper
#
# @simple_decorator
# def say_hello():
#     print("Hello, World!")
#
# say_hello()

# def repeat_decorator(times):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for _ in range(times):
#                 func(*args, **kwargs)
#         return wrapper
#     return decorator
#
# @repeat_decorator(3)
# def greet(name):
#     print(f"Hello, {name}!")
#
# greet("Alice")

import time

# def timer(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.perf_counter()
#         result = func(*args, **kwargs)
#         end_time = time.perf_counter()
#         elapsed = end_time - start_time
#         print(f"Function '{func.__name__}' executed in {elapsed:.6f} seconds.")
#         return result
#     return wrapper
#
# # Example usage:
# @timer
# def compute_sum(n):
#     return sum(range(n))
#
# compute_sum(1000000)
#
#
from functools import cache
#
#
# @cache
# def fibonacci(n):
#     if n <= 1:
#         return n
#     return fibonacci(n-1) + fibonacci(n-2)
#
# print(fibonacci(10))  # Output: 55
# print(fibonacci(20))  # Output: 6765

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

#print(fibonacci(30)) #without cache 1.89 seconds
print(fibonacci(30)) # with cache 0.000055 seconds
