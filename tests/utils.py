import os

DIR_NAME = os.path.dirname(os.path.realpath(__file__))


def build_relative_glob(path):
    return DIR_NAME + path


def build_relative(path):
    return os.path.join(DIR_NAME, path)
