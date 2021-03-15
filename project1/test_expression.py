"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar


# Example test, you can adapt it to your needs.
def test_expr_construction():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c * Scalar(4) + Scalar(3)
    assert repr(
        expr) == "((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3))"


def test():
    a = Secret(1)
    b = Secret(2)
    expr = a+b+(a+b)
    assert repr(expr) == "((Secret(1) + Secret(2)) + (Secret(1) + Secret(2)))"


def testMult():
    a = Scalar(5)
    b = Secret(2)
    expr = a*b
    assert repr(expr) == "Scalar(5) * Secret(2)"


def testSub():
    a = Scalar(5)
    b = Secret()
    expr = a-b
    assert repr(expr) == "(Scalar(5) - Secret())"


def testContainExpression():
    a = Scalar(5)
    b = Secret()
    expr1 = a-b
    assert expr1.containsSecret
    expr2 = a+b
    assert expr2.containsSecret
    expr3 = a
    assert not expr3.containsSecret
    expr4 = b
    assert expr4.containsSecret
    expr5 = a*b
    assert expr5.containsSecret


if __name__ == "__main__":
    testContainExpression()
