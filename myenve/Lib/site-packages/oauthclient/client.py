import logging
import requests

from requests.exceptions import HTTPError


class OAuth2Client(object):
    def __init__(self, provider, token):
        self.logger = logging.getLogger(__name__)

        self.provider = provider
        self.token = token

    def delete(self, *args, **kwargs):
        """
        Wrapper around OAuth2Client.request() for DELETE requests
        :return: OAuth2Client.request() return value
        """
        return self.request(requests.delete, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Wrapper around OAuth2Client.request() for GET requests
        :return: OAuth2Client.request() return value
        """
        return self.request(requests.get, *args, **kwargs)

    def get_access_token(self):
        if self.token.is_expired:
            self.refresh_token()

        return self.token.access_token

    def get_authentication_url(self, redirect_uri):
        params = {
            'auth_url': self.provider.auth_url,
            'client_id': self.provider.client_id,
            'state': self.token.uuid,
            'redirect_uri': redirect_uri,
        }

        return ('{auth_url}'
                '?response_type=code'
                '&client_id={client_id}'
                '&state={state}'
                '&redirect_uri={redirect_uri}'.format(**params))

    def set_token_from_auth_code(self, code):
        """
        Requests a token from the given auth code payload
        :return: Token model instance
        """
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'code': code,
        }

        response = requests.post(self.provider.token_url, data=payload)
        response.raise_for_status()

        return self.token.set_data(response.json())

    def post(self, *args, **kwargs):
        """
        Wrapper around OAuth2Client.request() for POST requests
        :return: OAuth2Client.request() return value
        """
        return self.request(requests.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Wrapper around OAuth2Client.request() for POST requests
        :return: OAuth2Client.request() return value
        """
        return self.request(requests.put, *args, **kwargs)

    def refresh_token(self):
        """
        Refreshes the token in the given provider
        :return: Token instance
        """
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'refresh_token': self.token.refresh_token,
        }

        response = requests.post(self.provider.token_url, data=payload)

        try:
            response.raise_for_status()
        except HTTPError, exc:
            self.logger.error('Unable to refresh token: {}'.format(exc))
            self.logger.error(response.content)

            raise

        return self.token.set_data(response.json())

    def request(self, request_handler, *args, **kwargs):
        """
        Makes an authorized HTTP request and returns a requests response

        :param request_handler: requests method such as .get(), .post(), etc.
        :param args: arguments taken by the requests method
        :param kwargs: keyword arguments taken by the requests method
        :param _include_auth_header: Whether to inject the Authorization header. Default=True
        :return: requests Response instance
        """
        # prefixed with `_` because it's not passed along to requests
        include_auth_header = kwargs.pop('_include_auth_header', True)
        if include_auth_header:
            # set the access token request header
            access_token = self.get_access_token()
            kwargs.setdefault('headers', {}).update({
                'Authorization': 'Bearer {}'.format(access_token),
            })

        self.logger.debug('request_handler={}, args={}, kwargs={}'.format(request_handler, args, kwargs))

        response = request_handler(*args, **kwargs)

        try:
            response.raise_for_status()
        except HTTPError, exc:
            self.logger.error(response.text)
            raise

        return response

    def revoke_token(self):
        """
        Revokes the token in the given provider
        """
        'client_id=CLIENT_ID&client_secret=CLIENT_SECRET&token=1234'

        payload = {
            'client_id': self.provider.client_id,
            'client_secret': self.provider.client_secret,
            'token': self.token.refresh_token,
        }

        self.post(
            self.provider.revoke_url,
            data=payload,
            _include_auth_header=False
        )

        return self.token.revoke()
