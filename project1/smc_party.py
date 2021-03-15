"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import base64
from typing import Dict

from communication import Communication
from expression import (
    Add, Expression, Mult, Scalar,
    Secret, Sub
)
from protocol import ProtocolSpec
from secret_sharing import(
    int_from_bytes, int_to_bytes, reconstruct_secret,
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
        # *secretIdDict is the dictionary to map IDs of secrets (base64-encoded) to client IDs (str).
        self.secretIdDict: Dict[str, str] = dict()
        # *shareDict is the dictionary to store the secret shares retrieved from other clients
        self.shareDict: Dict[str, Share] = dict()
        # *tempClientId is the temporary identifier for the intermediate multiplications
        self.tempClientId = "0"
        # *tempBytes is the temporary bytes for the intermediate multiplications
        self.tempBytes = bytes(4)

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        # If the expression involves only scalars, just compute and return the result
        if not self.protocol_spec.expr.containsSecret:
            result = self.processScalars(self.protocol_spec.expr)
            return result.value

        secret, secretVal = list(self.value_dict.items())[0]
        # Publish the IDs of the secrets so that clients know which secret belongs to who
        self.comm.publish_message("IDs of secrets", secret.id)
        # Make sure that everyone can publish before reading
        # time.sleep(1)
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
        # time.sleep(1)
        # Obtain the privately sent shares
        for client_id in self.protocol_spec.participant_ids:
            shareBytes = self.comm.retrieve_private_message(client_id)
            self.shareDict[client_id] = Share(int_from_bytes(shareBytes))
        # time.sleep(1)
        share = self.process_expression(self.protocol_spec.expr)
        # Broadcast the result
        self.comm.publish_message("Final", bytes(share))
        # Wait a little
        # time.sleep(1)
        # Read the responses
        responseShares = list()
        for client_id in self.protocol_spec.participant_ids:
            shareFinal = self.comm.retrieve_public_message(client_id, "Final")
            shareFinal = int_from_bytes(shareFinal)
            shareFinal = Share(shareFinal)
            responseShares.append(shareFinal)
        # Reconstruct the result
        result = reconstruct_secret(responseShares)
        #print(f"\n\n\n{self.client_id}: result is: {result}\n\n\n")
        return result

    def processScalars(self, expr: Expression) -> Share:
        """Just process the scalars and return

        Args:
            expr (Expression): Expression involving scalars

        Returns:
            Share: The final result
        """
        if isinstance(expr, Scalar):
            return Share(expr.value)
        if isinstance(expr, Add):
            return self.processScalars(expr.leftExpression) + self.processScalars(expr.rightExpression)
        if isinstance(expr, Sub):
            return self.processScalars(expr.leftExpression) - self.processScalars(expr.rightExpression)
        if isinstance(expr, Mult):
            return self.processScalars(expr.leftExpression) * self.processScalars(expr.rightExpression)
        return Share(0)

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
            # ?Are the case structures too complicated? Can they be further simplified?
            # If the expression `Mult` involves secrets, we need to use "Beaver triplets"
            if isinstance(expr.leftExpression, Secret) and isinstance(expr.rightExpression, Secret):
                opId = ""
                # x is the client_id
                x = self.secretIdDict[expr.leftExpression.id.decode("utf-8")]
                opId += x
                # x is the share of the client_id
                x = self.shareDict[x]
                # y is the client_id
                y = self.secretIdDict[expr.rightExpression.id.decode("utf-8")]
                opId += y
                #print("\n\n\n", "OpId:", opId, "\n\n\n")
                # y is the share of client_id
                y = self.shareDict[y]
                share_a, share_b, share_c = self.comm.retrieve_beaver_triplet_shares(
                    opId)
                share_a, share_b, share_c = Share(
                    share_a), Share(share_b), Share(share_c)
                x_a_broadcast = x-share_a
                y_b_broadcast = y-share_b
                # Broadcast the computed shares
                opId_x_a = opId+"_x_a"
                opId_y_b = opId+"_y_b"
                self.comm.publish_message(
                    opId_x_a, int_to_bytes(x_a_broadcast.value))
                self.comm.publish_message(
                    opId_y_b, int_to_bytes(y_b_broadcast.value))
                # Wait so that everyone can read on time
                # time.sleep(1)
                # Read the shares
                x_a_sharesList = list()
                y_b_sharesList = list()
                for client_id in self.protocol_spec.participant_ids:
                    # x and a
                    share_x_a = self.comm.retrieve_public_message(
                        client_id, opId_x_a)
                    share_x_a = int_from_bytes(share_x_a)
                    share_x_a = Share(share_x_a)
                    x_a_sharesList.append(share_x_a)
                    # y and b
                    share_y_b = self.comm.retrieve_public_message(
                        client_id, opId_y_b)
                    share_y_b = int_from_bytes(share_y_b)
                    share_y_b = Share(share_y_b)
                    y_b_sharesList.append(share_y_b)
                # Reconstruct the x-a and y-b
                x_a_re = reconstruct_secret(x_a_sharesList)
                x_a_re = Share(x_a_re)
                y_b_re = reconstruct_secret(y_b_sharesList)
                y_b_re = Share(y_b_re)
                # 4th step: locally compute the share of z
                z = share_c + x * y_b_re + y * x_a_re
                # If I have the ID 0, add additional term -(x-a)(y-b)
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    z -= (x_a_re*y_b_re)
                # print(f"{self.client_id} share_a: {share_a}, share_b: {share_b}, share_c: {share_c} share_x: {x}, share_y: {y}, share_z: {z}, x-a: {x_a_re}, y-b: {y_b_re}")
                return z

            # Secret - Expression
            if isinstance(expr.leftExpression, Secret) and expr.rightExpression.containsSecret:
                right = self.process_expression(expr.rightExpression)
                # We need to register this
                b64encoded = base64.b64encode(self.tempBytes)
                newSecret = Secret(right.value, b64encoded)
                secretId = newSecret.id
                self.secretIdDict[secretId.decode("utf-8")] = self.tempClientId
                self.shareDict[self.tempClientId] = right
                # Increment the temporary values by 1
                self.tempClientId = str(int(self.tempClientId)+1)
                self.tempBytes = int_to_bytes(int_from_bytes(self.tempBytes)+1)
                #print(self.secretIdDict, self.shareDict)
                return self.process_expression(Mult(expr.leftExpression, newSecret))

            # Expression - Secret
            if expr.leftExpression.containsSecret and isinstance(expr.rightExpression, Secret):
                #print("\n\n\nHello world!\n\n\n")
                left = self.process_expression(expr.leftExpression)
                # We need to register this
                b64encoded = base64.b64encode(self.tempBytes)
                newSecret = Secret(left.value, b64encoded)
                secretId = newSecret.id
                self.secretIdDict[secretId.decode("utf-8")] = self.tempClientId
                self.shareDict[self.tempClientId] = left
                # Increment the temporary values by 1
                self.tempClientId = str(int(self.tempClientId)+1)
                self.tempBytes = int_to_bytes(int_from_bytes(self.tempBytes)+1)
                #print("\n\n\n", self.secretIdDict)
                #print(self.shareDict, "\n\n\n")
                return self.process_expression(Mult(newSecret, expr.rightExpression))

            # Expression - Expression
            if expr.leftExpression.containsSecret and expr.rightExpression.containsSecret:
                left = self.process_expression(expr.leftExpression)
                # We need to register this
                b64encoded = base64.b64encode(self.tempBytes)
                newSecret = Secret(left.value, b64encoded)
                secretId = newSecret.id
                self.secretIdDict[secretId.decode("utf-8")] = self.tempClientId
                self.shareDict[self.tempClientId] = left
                # Increment the temporary values by 1
                self.tempClientId = str(int(self.tempClientId)+1)
                self.tempBytes = int_to_bytes(int_from_bytes(self.tempBytes)+1)

                right = self.process_expression(expr.rightExpression)
                # We need to register this
                b64encoded = base64.b64encode(self.tempBytes)
                newSecret2 = Secret(right.value, b64encoded)
                secretId = newSecret2.id
                self.secretIdDict[secretId.decode("utf-8")] = self.tempClientId
                self.shareDict[self.tempClientId] = right
                # Increment the temporary values by 1
                self.tempClientId = str(int(self.tempClientId)+1)
                self.tempBytes = int_to_bytes(int_from_bytes(self.tempBytes)+1)
                return self.process_expression(Mult(newSecret, newSecret2))

            # Process further
            if not expr.leftExpression.containsSecret and not expr.rightExpression.containsSecret:
                return self.processScalars(expr)
            if not expr.leftExpression.containsSecret:
                return self.processScalars(expr.leftExpression) * self.process_expression(expr.rightExpression)
            if not expr.rightExpression.containsSecret:
                return self.process_expression(expr.leftExpression) * self.processScalars(expr.rightExpression)

            # Ideally, this should not happen
            return Share(0)

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
            return shareVal

        if isinstance(expr, Scalar):
            if expr.value is not None:
                return Share(expr.value)
            return Share(0)

        # This case shouldn't happen
        raise Exception(
            "Expression not recognized. Are you sure the input is correct?")

    # Feel free to add as many methods as you want.
