from oauthlib.oauth1 import RequestValidator

from ltilogin import setting
from ltilogin.models import LTIClient


class LTIRequestValidator(RequestValidator):
    """
    LTIRequestValidator.

    Supports only SignatureOnlyEndpoint
    """
    def __init__(self):
        self.__secrets = {}

    @property
    def safe_characters(self):
        """ Allow also '-' character used in some uuid examples out there. """
        return setting.SAFE_CHARACTERS  # set

    @property
    def client_key_length(self):
        """ Loosen limits. """
        return setting.KEY_LENGTH_RANGE

    @property
    def nonce_length(self):
        """ Loosen limits. """
        return setting.NONCE_LENGTH

    @property
    def enforce_ssl(self):
        """ Allow unsafe access when using limited network. """
        return False

    # used by: SignatureOnlyEndpoint
    @property
    def dummy_client(self):
        """
        Return dummy client key.
        This can't be valid key in database.
        All keys in database are at least 6 characters
        """
        return "DEAD"

    # used by: SignatureOnlyEndpoint
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request_token=None, access_token=None):
        """
        Should check if timestamp and nonce pair have been seen before.
        Here we trust the network and the client computer are completely secure.
        """
        return True

    # used by: SignatureOnlyEndpoint
    def validate_client_key(self, client_key, request):
        return self.get_client_secret(client_key, request) is not None

    # used by: SignatureOnlyEndpoint
    def get_client_secret(self, client_key, request):
        if client_key in self.__secrets:
            return self.__secrets[client_key]
        secret = LTIClient.query.get(client_key).secret
        if secret is None:
            if client_key == "DEAD":
                return "DEAD"
        self.__secrets[client_key] = secret
        return secret

    # used by: SignatureOnlyEndpoint
    def get_rsa_key(self, client_key, request):
        # No support for rsa keys
        return None
