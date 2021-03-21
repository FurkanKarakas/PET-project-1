"""
Custom application test suite. The participants are:
1. Alice
2. Bob
3. Charlie
4. David
5. Eve
6. Frank
7. Gerald
It is known that Gerald will participate.
It is known that David participates if and only if Charlie participates.
It is known that if Frank participates, then Eve won't participate.
The circuit representation is:
f(a,b,c,d,e,f) = a+b+(c*d)*2+f+e*(1-f)+G where G is 1 (Scalar)
"""

import time
from multiprocessing import Process, Queue

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

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


a = Secret()
b = Secret()
c = Secret()
d = Secret()
e = Secret()
f = Secret()
G = Scalar(1)
togetherCharlieDavid = Scalar(2)
expr = a + b + (c*d)*togetherCharlieDavid + f + e*(Scalar(1)-f) + G


def test_application1():
    parties = {
        "Alice": {a: 1},
        "Bob": {b: 1},
        "Charlie": {c: 0},
        "David": {d: 1},
        "Eve": {e: 1},
        "Frank": {f: 1},
    }

    expected = 1+1+(0*1)*2+1+1*(1-1)+1
    suite(parties, expr, expected)


def test_application2():
    parties = {
        "Alice": {a: 0},
        "Bob": {b: 0},
        "Charlie": {c: 0},
        "David": {d: 1},
        "Eve": {e: 0},
        "Frank": {f: 1},
    }

    expected = 0+0+(0*1)*2+1+0*(1-1)+1
    suite(parties, expr, expected)


def test_application3():
    parties = {
        "Alice": {a: 1},
        "Bob": {b: 0},
        "Charlie": {c: 1},
        "David": {d: 1},
        "Eve": {e: 1},
        "Frank": {f: 0},
    }

    expected = 1+0+(1*1)*2+0+1*(1-0)+1
    suite(parties, expr, expected)


if __name__ == "__main__":
    test_application1()
