"""
Benchmarking tests
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


def performanceTestFunction():
    a = Secret()
    b = Secret()

    parties = {
        "Alice": {a: 1},
        "Bob": {b: 1},
    }

    N = 999
    expr = None
    for _ in range((N+1)//2):
        if expr is None:
            expr = a*b
        else:
            expr *= a*b
    expected = 1
    suite(parties, expr, expected)


def test_benchmark(benchmark):
    benchmark.pedantic(performanceTestFunction, rounds=25)
