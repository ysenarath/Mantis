import os


def resolve(path):
    root = join(dirname(abspath(__file__)), '..', '..')
    path_parts = split(path)
    if len(path_parts) > 0 and path_parts[0] == '.':
        path = join(root, *path_parts[1:])
    return path


def join(*args, **kwargs):
    return os.path.join(*args, **kwargs)


def dirname(*args, **kwargs):
    return os.path.dirname(*args, **kwargs)


def split(*args, **kwargs):
    return os.path.split(*args, **kwargs)


def abspath(*args, **kwargs):
    return os.path.abspath(*args, **kwargs)
