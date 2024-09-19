from .auth import AuthTokenLink
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pydantic import field_validator
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Any, Callable, Awaitable, Dict, Type
import jwt
from rath.operation import Operation


class SignLocalLink(AuthTokenLink):
    """SignLocalLink

    SignLocalLink is a link is a type of AuthTokenLink that
    crated a JWT token using a local private key,
    and sends it to the next link.

    """

    private_key: rsa.RSAPrivateKey

    @field_validator("private_key", mode="before")
    def must_be_valid_pem_key(cls: Type["SignLocalLink"], v: Any) -> rsa.RSAPrivateKey:
        """Validates that the private key is a valid PEM key"""
        try:
            try:
                if isinstance(v, str):
                    with open(v, "rb") as f:
                        v = f.read()
            except Exception as e:
                raise ValueError("Could not read file") from e

            key = serialization.load_pem_private_key(
                v, password=None, backend=default_backend()
            )

            # Check if it is an RSA key
            if not isinstance(key, rsa.RSAPrivateKey):
                raise ValueError("PEM key is not an RSA Private key.")

            return key
        except Exception as e:
            raise ValueError(f"Not a valid PEM key. {str(e)}")

    async def aretrieve_payload(self, operation: Operation) -> Dict[str, Any]:
        """Abstract method to retrieve the payload to sign

        Implement this method to retrieve the payload to sign.

        Parameters
        ----------
        operation : Operation
            The operation to sign

        Returns
        -------
        Dict[str, Any]
            The payload to sign by jwt with the private key

        """
        raise NotImplementedError("Please implement this method.")

    async def aload_token(self, operation: Operation) -> str:
        """Loads the token to send to the next link

        This method will call the aretrieve_payload method to retrieve the payload to sign,
        and then sign it with the private key. Please implement the aretrieve_payload method
        to retrieve the payload to sign.

        Parameters
        ----------
        operation : Operation
            The operation to sign

        Returns
        -------
        str
            The token to send to the next link

        """

        payload = await self.aretrieve_payload(operation)
        token = jwt.encode(payload, key=self.private_key, algorithm="RS256")  # type: ignore
        # rsa.RSAPrivateKey should be correctly typed in pyjwt
        return token

    async def arefresh_token(self, operation: Operation) -> str:
        """Refreshes the token

        This method is not implemented for SignLocalLink, as it is not needed.
        (Local certificates should not expire)
        """

        raise NotImplementedError


class ComposedSignTokenLink(SignLocalLink):
    """ComposedSignTokenLink

    ComposedSignTokenLink is a SignLocalLink that
    uses a payload retriever to retrieve the payload
    to sign, enables the user to use a custom payload
    retriever., without having to implement the entire
    SignLocalLink.
    """

    payload_retriever: Callable[[Operation], Awaitable[Dict]]
    """ The payload retriever to use to retrieve the payload to sign"""

    async def aretrieve_payload(self, operation: Operation) -> Dict[str, Any]:
        """Wraps the payload_retriever method"""
        return await self.payload_retriever(operation)
