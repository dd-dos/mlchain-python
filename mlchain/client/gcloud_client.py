import google.auth.transport.requests
import google.oauth2.id_token
import requests

from . import Client


class GcloudClient(Client):
    def __init__(self, api_key=None, api_address=None, serializer='json', timeout=5 * 60, headers={}, type='http',
                 name: str = "", version: str = "", check_status=False):
        self.id_token = self._get_oauth2_token(api_address)
        self.headers = {"Authorization": f"Bearer {self.id_token}"}
        Client.__init__(self, api_key=api_key, api_address=api_address, serializer=serializer, timeout=timeout, headers=self.header, type=type,
                        name=name, version=version, check_status=check_status)

    def _get_oauth2_token(self, url):
        """
        new_request creates a new HTTP request with IAM ID Token credential.
        This token is automatically handled by private Cloud Run (fully managed)
        and Cloud Functions.
        """

        auth_req = google.auth.transport.requests.Request()
        target_audience = url

        id_token = google.oauth2.id_token.fetch_id_token(auth_req, target_audience)

        return id_token