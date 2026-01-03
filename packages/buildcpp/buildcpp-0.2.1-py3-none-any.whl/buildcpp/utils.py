import os
import fnmatch
from pathlib import Path


def find_files(directory, pattern, recursive=False):
    matches = []

    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            if fnmatch.fnmatch(filename, pattern):
                matches.append(os.path.join(directory, filename))

    return [Path(match) for match in matches]


def find_directories(directory, pattern, recursive=False):
    matches = []

    if recursive:
        for root, dirnames, _ in os.walk(directory):
            for dirname in fnmatch.filter(dirnames, pattern):
                matches.append(os.path.join(root, dirname))
    else:
        for dirname in os.listdir(directory):
            if fnmatch.fnmatch(dirname, pattern):
                matches.append(os.path.join(directory, dirname))

    return [Path(match) for match in matches]


if __name__ == '__main__':
    print(find_files(r'src', '*.py'))
    print(find_files(r'src', '*.py', True))
    print(find_directories(r'src', '*', True))
