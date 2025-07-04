def simple_decorator(func):
    def wrapper():
        print("Before the function call.")
        func()
        print("After the function call.")
    return wrapper

@simple_decorator
def say_hello():
    print("Hello, World!")

say_hello()
