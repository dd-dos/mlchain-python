from mlchain import mlconfig
from mlchain.base import logger
from mlchain import mlconfig

from .grpc_client import GrpcClient
from .http_client import HttpClient


class Client(HttpClient, GrpcClient):
    def __init__(self, api_key=None, api_address=None, serializer='json', timeout=5 * 60, headers={}, type='http',
                 name: str = "", version: str = "", check_status=False):
        assert isinstance(type, str), "type model must be a string"
        self._api_key = api_key
        self._api_address = api_address
        self._serializer = serializer
        self._timeout = timeout
        if mlconfig.platform == 'gcloud':
            _token = self._get_gcloud_oauth2_token()
            self._headers = headers.update({"Authorization": f"Bearer {_token}"})
        else:
            self._headers = headers
        self._type = type
        if self._type.lower() == 'http':
            HttpClient.__init__(self, api_key=api_key, api_address=api_address, serializer=serializer,
                                timeout=timeout, headers=self._headers, name=name, version=version,
                                check_status=check_status)
        elif self._type.lower() == 'grpc':
            GrpcClient.__init__(self, api_key=api_key, api_address=api_address, serializer=serializer,
                                timeout=timeout, headers=self._headers, name=name, version=version,
                                check_status=check_status)
        else:
            raise Exception("type must be http or grpc")

    def model(self, name: str = "", version: str = "", check_status=False):
        logger.warning(
            "function .model is deprecated and will be remove in the next version")
        if self._type.lower() == 'http':
            return HttpClient(api_key=self._api_key, api_address=self._api_address, serializer=self._serializer,
                              timeout=self._timeout, headers=self._headers, name=name, version=version,
                              check_status=check_status)
        if self._type.lower() == 'grpc':
            return GrpcClient(api_key=self._api_key, api_address=self._api_address, serializer=self._serializer,
                              timeout=self._timeout, headers=self._headers, name=name, version=version,
                              check_status=check_status)

    def _get_gcloud_oauth2_token(self):
        """
        new_request creates a new HTTP request with IAM ID Token credential.
        This token is automatically handled by private Cloud Run (fully managed)
        and Cloud Functions.
        """
        import google.auth.transport.requests
        import google.oauth2.id_token

        auth_req = google.auth.transport.requests.Request()
        target_audience = self._api_address

        id_token = google.oauth2.id_token.fetch_id_token(auth_req, target_audience)
        if len(id_token) > 0:
            logger.info(f"Got oauth2 token: {id_token}")
        else:
            logger.info("Oauth2 token is missing.")

        return id_token


def get_model(name):
    config = mlconfig.get_client_config(name)
    timeout = config.timeout
    if timeout is not None:
        try:
            timeout = int(timeout)
        except:
            raise ValueError("timeout must be an integer")
    client_type = mlconfig.type or 'http'
    if config.ckeck_status is None:
        check_status = False
    elif isinstance(config.check_status, str) and config.check_status.lower() in ['y', 'yes', 'true', 't']:
        check_status = True
    elif isinstance(config.check_status, (int, float)) and config.check_status > 0:
        check_status = True
    else:
        check_status = False
    return Client(api_key=config.api_key, api_address=config.api_address,
                  serializer=config.serializer or 'json', timeout=timeout, type=client_type, check_status=check_status)
