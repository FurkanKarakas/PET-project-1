"""
Unit tests for the trusted parameter generator.
Testing ttp is not obligatory.

MODIFY THIS FILE.
"""

from secret_sharing import MODULUS, reconstruct_secret
from ttp import TrustedParamGenerator
from secret_sharing import Share


def test():
    """Beaver triplet generation"""
    myTTP = TrustedParamGenerator()
    myTTP.add_participant("Alice")
    myTTP.add_participant("Bob")
    myTTP.add_participant("Charlie")
    sharesAlice = myTTP.retrieve_share("Alice", "")
    sharesBob = myTTP.retrieve_share("Bob", "")
    sharesCharlie = myTTP.retrieve_share("Charlie", "")
    a_reconstructed = Share(reconstruct_secret(
        [sharesAlice[0], sharesBob[0], sharesCharlie[0]]))
    b_reconstructed = Share(reconstruct_secret(
        [sharesAlice[1], sharesBob[1], sharesCharlie[1]]))
    c_reconstructed = Share(reconstruct_secret(
        [sharesAlice[2], sharesBob[2], sharesCharlie[2]]))
    print("Value a*b:", (a_reconstructed*b_reconstructed).value)
    print("Value c:", c_reconstructed.value)
    assert (a_reconstructed*b_reconstructed).value == c_reconstructed.value


def secretMult():
    """Sample x*y protocol"""
    myTTP = TrustedParamGenerator()
    myTTP.add_participant("Alice")
    myTTP.add_participant("Bob")
    a_0, b_0, c_0 = myTTP.retrieve_share("Alice", "")
    a_1, b_1, c_1 = myTTP.retrieve_share("Bob", "")

    a = a_0+a_1
    b = b_0+b_1
    c = c_0+c_1
    assert (a*b).value == c.value

    x = Share(10)
    y = Share(5)
    z = x*y
    # x
    x_0, x_1 = [Share(7), Share(3)]
    # y
    y_0, y_1 = [Share(1), Share(4)]
    # Alice's perspective
    aliceBroadcast = [x_0-a_0, y_0-b_0]
    # Bob's perspective
    bobBroadcast = [x_1-a_1, y_1-b_1]
    x_minus_a = aliceBroadcast[0]+bobBroadcast[0]
    y_minus_b = aliceBroadcast[1]+bobBroadcast[1]
    print(f"a: {a}, b: {b} c: {c}")
    assert (x-a).value == x_minus_a.value and (y-b).value == y_minus_b.value

    # Reconstruction
    z_0 = c_0+x_0*y_minus_b+y_0*x_minus_a-x_minus_a*y_minus_b
    z_1 = c_1+x_1*y_minus_b+y_1*x_minus_a
    assert z.value == (z_0+z_1).value


if __name__ == "__main__":
    # test()
    secretMult()
