from azure.core.credentials import TokenCredential, AccessToken

# Helper class for service principal authentication
class BearerTokenCredential(TokenCredential):
    """
    A helper class for service principal authentication using a static bearer token.

    This wrapper is required to authenticate to the Blob and Filesystem clients.
    We generate a bearer access token in Azure Data Factory (ADF), but the Azure SDK
    requires this credential to be of type a TokenCredential: https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python.

    Attributes:
        token (str): The static bearer token used for authentication.
    """
    def __init__(self, token: str):
        """
        Initializes the BearerTokenCredential with the ADF generated bearer token for service principal authentication to the ADLS.

        Args:
            token (str): The bearer token to be used for authentication.
        """
        self.token = token

    def get_token(self, *scopes) -> AccessToken:
        """
        Retrieves an AccessToken object for authentication.

        Args:
            *scopes: The scopes for which the token is requested. These are ignored
                     in this implementation because the token is static.

        Returns:
            AccessToken: An AccessToken object with the static token and a default
                         expiration time of 3600 seconds.
        """
        return AccessToken(self.token, expires_on=3600)

def strtobool(val: str) -> bool:
    " Convert a string representation of truth to a boolean."
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"invalid truth value {val!r}")