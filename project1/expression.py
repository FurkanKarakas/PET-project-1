"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional


ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
        self,
        id: Optional[bytes] = None
    ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id
        self.containsSecret = True

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mult(self, other)

    def __hash__(self):
        return hash(self.id)

    # Feel free to add as many methods as you like.


class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
        self,
        value: int,
        id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)
        self.containsSecret = False

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
        self,
        value: Optional[int] = None,
        id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )

    # Feel free to add as many methods as you like.


# Feel free to add as many classes as you like.
class Add(Expression):
    """Add two expressions together. Inherits the base `Expression` class."""

    def __init__(
        self,
        leftExpression: Expression,
        rightExpression: Expression,
        id: Optional[bytes] = None
    ):
        super().__init__(id)
        self.leftExpression = leftExpression
        self.rightExpression = rightExpression
        self.containsSecret = self.leftExpression.containsSecret or self.rightExpression.containsSecret

    def __repr__(self):
        return f"({self.leftExpression.__repr__()} + {self.rightExpression.__repr__()})"


class Sub(Expression):
    """Subtract two expressions from one another. Inherits the base `Expression` class."""

    def __init__(
        self,
        leftExpression: Expression,
        rightExpression: Expression,
        id: Optional[bytes] = None
    ):
        super().__init__(id)
        self.leftExpression = leftExpression
        self.rightExpression = rightExpression
        self.containsSecret = self.leftExpression.containsSecret or self.rightExpression.containsSecret

    def __repr__(self):
        return f"({self.leftExpression.__repr__()} - {self.rightExpression.__repr__()})"


class Mult(Expression):
    """Multiply two expressions together. Inherits the base `Expression` class."""

    def __init__(
        self,
        leftExpression: Expression,
        rightExpression: Expression,
        id: Optional[bytes] = None
    ):
        super().__init__(id)
        self.leftExpression = leftExpression
        self.rightExpression = rightExpression
        self.containsSecret = self.leftExpression.containsSecret or self.rightExpression.containsSecret

    def __repr__(self):
        return f"{self.leftExpression.__repr__()} * {self.rightExpression.__repr__()}"
