"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
import time
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Add, Expression, Mult, Scalar,
    Secret, Sub
)
from protocol import ProtocolSpec
from secret_sharing import(
    int_from_bytes, reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """
    # secretIdDict is the dictionary to map IDs of secrets (base64-encoded) to client IDs (str).
    secretIdDict = dict()
    # shareDict is the dictionary to store the secret shares retrieved from other clients
    shareDict = dict()

    def __init__(
        self,
        client_id: str,
        server_host: str,
        server_port: int,
        protocol_spec: ProtocolSpec,
        value_dict: Dict[Secret, int]
    ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        secret, secretVal = list(self.value_dict.items())[0]
        # Publish the IDs of the secrets so that clients know which secret belongs to who
        self.comm.publish_message("IDs of secrets", secret.id)
        # Make sure that everyone can publish before reading
        time.sleep(1)
        for client_id in self.protocol_spec.participant_ids:
            secretValC = self.comm.retrieve_public_message(
                client_id, "IDs of secrets")
            self.secretIdDict[secretValC.decode("utf-8")] = client_id
        numClients = len(self.protocol_spec.participant_ids)
        secretShares = share_secret(secretVal, numClients)
        # Send the shares privately
        for i, client_id in enumerate(self.protocol_spec.participant_ids):
            self.comm.send_private_message(
                client_id, self.client_id, bytes(secretShares[i]))
        # Give some time
        time.sleep(1)
        # Obtain the privately sent shares
        for client_id in self.protocol_spec.participant_ids:
            shareBytes = self.comm.retrieve_private_message(client_id)
            self.shareDict[client_id] = int_from_bytes(shareBytes)
        time.sleep(1)
        share = self.process_expression(self.protocol_spec.expr)
        # Broadcast the result
        self.comm.publish_message("Final", bytes(share))
        # Wait a little
        time.sleep(1)
        # Read the responses
        responseShares = list()
        for client_id in self.protocol_spec.participant_ids:
            shareFinal = self.comm.retrieve_public_message(client_id, "Final")
            shareFinal = int_from_bytes(shareFinal)
            shareFinal = Share(shareFinal)
            responseShares.append(shareFinal)
        # Reconstruct the result
        result = reconstruct_secret(responseShares)
        return result

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:

    def process_expression(self, expr: Expression) -> Share:
        if isinstance(expr, Add):
            # Process the `Add` expression based on its left and right expressions
            if isinstance(expr.leftExpression, Scalar) and isinstance(expr.rightExpression, Scalar):
                # If the current client is the first client
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) + self.process_expression(expr.rightExpression)
                # Otherwise, don't add the scalar values
                return Share(0) + Share(0)
            if isinstance(expr.leftExpression, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) + self.process_expression(expr.rightExpression)
                return Share(0) + self.process_expression(expr.rightExpression)
            if isinstance(expr.rightExpression, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) + self.process_expression(expr.rightExpression)
                return self.process_expression(expr.leftExpression) + Share(0)
            return self.process_expression(expr.leftExpression) + self.process_expression(expr.rightExpression)

        if isinstance(expr, Sub):
            # Process the `Sub` expression based on its left and right expressions
            if isinstance(expr.leftExpression, Scalar) and isinstance(expr.rightExpression, Scalar):
                # If the current client is the first client
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) - self.process_expression(expr.rightExpression)
                # Otherwise, don't subtract the scalar values
                return Share(0) - Share(0)
            if isinstance(expr.leftExpression, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) - self.process_expression(expr.rightExpression)
                return Share(0) - self.process_expression(expr.rightExpression)
            if isinstance(expr.rightExpression, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.leftExpression) - self.process_expression(expr.rightExpression)
                return self.process_expression(expr.leftExpression) - Share(0)
            return self.process_expression(expr.leftExpression) - self.process_expression(expr.rightExpression)

        if isinstance(expr, Mult):
            return self.process_expression(expr.leftExpression) * self.process_expression(expr.rightExpression)

        if isinstance(expr, Secret):
            if expr.value is not None:
                return Share(expr.value)
            # Get the ID of the secret
            secretId = expr.id.decode("utf-8")
            # Map it to the client ID
            client_id = self.secretIdDict[secretId]
            # Map it to the share
            shareVal = self.shareDict[client_id]
            # Finally, return it
            return Share(shareVal)

        if isinstance(expr, Scalar):
            return Share(expr.value)  # type: ignore

        return Share(-1)

    # Feel free to add as many methods as you want.


if __name__ == "__main__":
    print("Hello world!")
