"""
Additional tests
"""

import time
from multiprocessing import Process, Queue
from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run
from secret_sharing import MODULUS

from smc_party import SMCParty


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue))
               for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr, expected):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict)
               for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)

    for result in results:
        assert result == expected


def test1():
    """
    f(a, b, c) = b + Scalar(100) + a - c - Scalar(5) + Scalar(4)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
        "Charlie": {charlie_secret: 8}
    }

    expr = bob_secret+Scalar(100)+alice_secret - \
        charlie_secret-Scalar(5)+Scalar(4)
    expected = 3+100+14-8-5+4
    suite(parties, expr, expected)


def test2():
    """
    f(a, b) = a * b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
    }

    expr = alice_secret*bob_secret
    expected = 14*3
    suite(parties, expr, expected)


def test3():
    """
    f(a, b, c) = a * b * c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
        "Charlie": {charlie_secret: 10},
    }

    expr = (alice_secret*bob_secret)*charlie_secret
    expected = 14*3*10
    suite(parties, expr, expected)


def test4():
    """
    f(a, b, c) = a * (b + c)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
        "Charlie": {charlie_secret: 10},
    }

    expr = alice_secret*(bob_secret+charlie_secret)
    expected = 14*(3+10)
    suite(parties, expr, expected)


def test5():
    """
    f(a, b, c, d) = K0 * K1
    """
    a = Secret()
    b = Secret()
    c = Secret()
    d = Secret()
    K0 = Scalar(15)
    K1 = Scalar(8)
    K2 = Scalar(7)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
        "Charlie": {c: 10},
        "David": {d: 11},
    }

    expr = K0 * K1
    expected = 15*8
    suite(parties, expr, expected)


def test6():
    """
    f(a, b) = K0 + K1
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(15)
    K1 = Scalar(8)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = K0 + K1
    expected = 15+8
    suite(parties, expr, expected)


def test7():
    """
    f(a, b) = K0 - K1
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(15)
    K1 = Scalar(8)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = K0 - K1
    expected = 15-8
    suite(parties, expr, expected)


def test8():
    """
    f(a, b) = K0
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(15)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = K0
    expected = 15
    suite(parties, expr, expected)


def test9():
    """
    f(a, b) = K0 * K1 * K2
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(15)
    K1 = Scalar(3)
    K2 = Scalar(4)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = K0*K1*K2
    expected = 15*3*4
    suite(parties, expr, expected)


def test10():
    """
    f(a, b) = a
    """
    a = Secret()
    b = Secret()

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = a
    expected = 14
    suite(parties, expr, expected)


def test11():
    """
    f(a, b, c) = b
    """
    a = Secret()
    b = Secret()
    c = Secret()

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
        "Charlie": {c: 17}
    }

    expr = b
    expected = 3
    suite(parties, expr, expected)


def test12():
    """
    f(a, b) = a * (K0 * K1)
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(5)
    K1 = Scalar(10)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = a * (K0 * K1)
    expected = 14*5*10
    suite(parties, expr, expected)


def test13():
    """
    f(a, b) = (a + b) * K0 * K1
    """
    a = Secret()
    b = Secret()
    K0 = Scalar(5)
    K1 = Scalar(10)

    parties = {
        "Alice": {a: 14},
        "Bob": {b: 3},
    }

    expr = (a + b) * K0 * K1
    expected = 17*5*10
    suite(parties, expr, expected)


if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    # test8()
    test13()
