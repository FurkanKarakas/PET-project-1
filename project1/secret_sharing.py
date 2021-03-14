"""
Secret sharing scheme.
"""

from expression import Expression, Scalar, Secret
from typing import List, Optional
import random

MODULUS = 7919


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value: int):
        # Adapt constructor arguments as you wish
        self.value = value
        self.bn = value

    def __repr__(self):
        # Helps with debugging.
        return f"Share({self.value})"

    def __add__(self, other):
        return Share((self.value+other.value) % MODULUS)

    def __sub__(self, other):
        return Share((self.value-other.value) % MODULUS)

    def __mul__(self, other):
        return Share((self.value*other.value) % MODULUS)

    def __bytes__(self):
        return int_to_bytes(self.value)


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = list()
    for _ in range(num_shares-1):
        shares.append(Share(random.randrange(0, MODULUS)))
    totalSum = sum(share.value for share in shares) % MODULUS
    shareAtZero = Share((secret-totalSum) % MODULUS)
    shares.insert(0, shareAtZero)
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum(share.value for share in shares) % MODULUS


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


# Feel free to add as many methods as you want.
