import hashlib
import random
import string


def generate_string(
    size: int = 20,
    chars: str = string.ascii_uppercase + string.ascii_lowercase + string.digits,
) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


def generate_md5(input_text: str | None = None) -> str:
    if input_text is None:
        input_text = generate_string()
    return hashlib.md5(input_text.encode('utf-8')).hexdigest()
