import os
import functools
from threading import Timer

sep="---------------------------------------------------------------------------------------------"

def find_by_ext(path, *args):
    fullname = os.path.split(path)[-1]
    if len(fullname.split("."))==2:
        name,ext = fullname.split(".")
        for arg in args:
            if ext == arg:
                print(sep)
                print(path.replace(fullname,''))
                print(fullname)
    if len(fullname.split("."))==1:
        name = fullname

def no_doubles(lst):
    return list(set(lst))

def do_in_list(lst, func, *args):
    for path in lst:
        func(path, *args)

def do_in_dir(path, func, *args):
    for root, dirs, files in os.walk(path):
        for fullname in files:
            path = os.path.join(root, *dirs, fullname)
            func(path, *args)

def debounce(timeout: float):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.func.cancel()
            wrapper.func = Timer(timeout, func, args, kwargs)
            wrapper.func.start()
        wrapper.func = Timer(timeout, lambda: None)
        return wrapper
    return decorator
