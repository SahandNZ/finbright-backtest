import os


def create_directory(path: str) -> bool:
    tokens = path.split('/')[:-1]
    parents = ['/'.join(tokens[:index + 1]) for index in range(1, len(tokens))]
    for parent_dir in parents:
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
