"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""


from secret_sharing import reconstruct_secret, share_secret


def test():
    print(share_secret(10, 3))
    print(reconstruct_secret(share_secret(10, 3)))


if __name__ == "__main__":
    test()
