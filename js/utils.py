import random
import string


def get_parts(string):
    if len(string) == 1:
        return string

    num_parts = random.randint(1, int(len(string) / 2) + 1)
    split_indices = sorted(random.sample(range(1, len(string)), num_parts - 1))
    parts = [string[i:j] for i, j in zip([0] + split_indices, split_indices + [None])]
    return parts


def generate_unique_sequence(length):
    sequence = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return sequence


def generate_unique_random_numbers(k, n):
    unique_numbers = sorted(random.sample(range(n), k))
    return unique_numbers


def gen_name(all_identifier):
        name = '_0ib' + str(random.randint(10, 999)) + 'k' + str(random.randint(1000, 9999)) + 's'
        while name in all_identifier:
            name = '_0ib' + str(random.randint(10, 999)) + 'k' + str(random.randint(1000, 9999)) + 's'
        return name