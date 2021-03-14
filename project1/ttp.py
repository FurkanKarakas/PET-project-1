"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
import random
from typing import (
    Dict, List,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    MODULUS, share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.operationDict: Dict[str, Tuple[List[Share],
                                            List[Share], List[Share]]] = dict()

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        participantsList = sorted(list(self.participant_ids))
        index = participantsList.index(client_id)
        # If we have already calculated the shares
        if op_id in self.operationDict:
            a_shares, b_shares, c_shares = self.operationDict[op_id]
            return a_shares[index], b_shares[index], c_shares[index]
        # Else, calculate them here and return the relevant shares
        a = random.randrange(0, MODULUS)
        b = random.randrange(0, MODULUS)
        c = (a*b) % MODULUS
        a_shares = share_secret(a, len(self.participant_ids))
        b_shares = share_secret(b, len(self.participant_ids))
        c_shares = share_secret(c, len(self.participant_ids))
        self.operationDict[op_id] = a_shares, b_shares, c_shares
        print(f"\n\n\nTTP, a: {a}, b: {b}, c: {c}")
        print(a_shares, b_shares, c_shares, "\n\n\n")
        return a_shares[index], b_shares[index], c_shares[index]

    # Feel free to add as many methods as you want.
