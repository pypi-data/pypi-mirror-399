import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(2, 3)


import time
import functools

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        print(f"[TIME] {func.__name__} took {duration:.2f} ms")
        return result
    return wrapper

@timed
def slow_operation():
    time.sleep(0.2)
    return "done"

slow_operation()

import functools
from collections import defaultdict

_call_counts = defaultdict(int)

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _call_counts[func.__name__] += 1
        result = func(*args, **kwargs)
        return result
    return wrapper

@count_calls
def compute(x):
    return x * x

for i in range(5):
    compute(i)

print("[PROFILE] call counts:", dict(_call_counts))
