def find_files(directory, pattern, recursive=False):
    import os
    import fnmatch
    matches = []

    if recursive:
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            if fnmatch.fnmatch(filename, pattern):
                matches.append(os.path.join(directory, filename))

    return matches