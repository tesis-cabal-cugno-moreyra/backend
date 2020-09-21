import random
import string


def get_random_alphanumeric_string(length) -> str:
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(length)))
