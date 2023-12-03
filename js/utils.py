import random
import string


def get_parts(string):
    if len(string) == 1:
        return string

    num_parts = random.randint(1, int(len(string) / 2))
    split_indices = sorted(random.sample(range(1, len(string)), num_parts - 1))
    parts = [string[i:j] for i, j in zip([0] + split_indices, split_indices + [None])]
    return parts


def generate_unique_sequence(length):
    sequence = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return sequence