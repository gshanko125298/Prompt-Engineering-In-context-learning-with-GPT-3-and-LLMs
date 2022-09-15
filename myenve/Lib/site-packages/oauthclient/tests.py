import datetime
import json
import mock

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils.timezone import now

from oauthclient.client import OAuth2Client
from oauthclient.models import Provider, Token

TOKEN_RESPONSE = """{
    "access_token": "5jXpYvhHXg8JZxF2UcDukyrBLr1C25iA",
    "expires_in": 3723,
    "restricted_to": [],
    "refresh_token": "eqg7QPesl9vgawmCSMcf8pMeQO46Djy4cJPl85W8iTuKuymaGkXd4h9IFXUdL9bA",
    "token_type": "bearer"
}"""

AUTH_CODE_PARAMS = {
    "state": "cb68eab2bb83ad7c7a41b46da0c5ebea9c6bb67c",
    "code": "h5r3QjA0IUwTGAB1zLSAjPOFZRTEd6zZ"
}


class AuthCodeLogicTestCase(TestCase):
    @mock.patch('oauthclient.client.requests')
    def test_auth_code(self, requests_mock):
        code = AUTH_CODE_PARAMS['code']

        response = mock.Mock()
        response.json.return_value = json.loads(TOKEN_RESPONSE)
        requests_mock.post.return_value = response

        provider = mock.Mock()
        token = mock.Mock()

        OAuth2Client(provider, token).set_token_from_auth_code(code)

        _args, __kwargs = token.set_data.call_args
        token_data = _args[0]

        self.assertEqual(token_data, response.json.return_value)

    @mock.patch('oauthclient.client.requests')
    def test_get(self, requests_mock):
        provider = mock.Mock()

        token = mock.Mock()
        token.is_expired = False
        token.access_token = 'access_token'

        url = 'https://example.com/'
        headers = {
            'Authorization': 'Bearer access_token'
        }

        OAuth2Client(provider, token).get(url)

        requests_mock.get.assert_called_with(url, headers=headers)

    @mock.patch('oauthclient.client.OAuth2Client.refresh_token')
    @mock.patch('oauthclient.client.requests')
    def test_get_expired_token(self, requests_mock, refresh_token_mock):
        provider = mock.Mock()

        token = mock.Mock()
        token.is_expired = True
        token.access_token = 'access_token'

        url = 'https://example.com/'
        headers = {
            'Authorization': 'Bearer access_token'
        }

        OAuth2Client(provider, token).get(url)

        requests_mock.get.assert_called_with(url, headers=headers)

        refresh_token_mock.assert_called_with()

    @mock.patch('oauthclient.client.OAuth2Client.refresh_token')
    def test_get_access_token(self, refresh_token_mock):
        provider = mock.Mock()
        token = mock.Mock(access_token='token', is_expired=False)

        access_token = OAuth2Client(provider, token).get_access_token()

        self.assertEqual('token', access_token)

        self.assertEqual(0, refresh_token_mock.call_count)

    @mock.patch('oauthclient.client.OAuth2Client.refresh_token')
    def test_get_access_token_expired(self, refresh_token_mock):
        provider = mock.Mock()
        token = mock.Mock(access_token='token', is_expired=True)

        access_token = OAuth2Client(provider, token).get_access_token()

        self.assertEqual('token', access_token)

        self.assertEqual(1, refresh_token_mock.call_count)

    def test_get_authentication_url(self):
        redirect_uri = 'http://example.com/auth_code'
        provider = mock.Mock(
            auth_url='http://example.com/authenticate',
            client_id='client_id',
        )
        token = mock.Mock(uuid='uuid')

        url = OAuth2Client(provider, token).get_authentication_url(redirect_uri)

        expected = ('http://example.com/authenticate'
                    '?response_type=code'
                    '&client_id=client_id'
                    '&state=uuid'
                    '&redirect_uri=http://example.com/auth_code')

        self.assertEqual(expected, url)

    @mock.patch('oauthclient.client.requests')
    def test_refresh_token(self, requests_mock):
        response = mock.Mock()
        response.json.return_value = json.loads(TOKEN_RESPONSE)
        requests_mock.post.return_value = response

        token_url = 'http://example.com/token'
        provider = mock.Mock(
            client_id='id',
            client_secret='secret',
            token_url=token_url
        )

        token = mock.Mock(refresh_token='refresh')

        request_data = {
            'client_id': provider.client_id,
            'client_secret': provider.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
        }

        OAuth2Client(provider, token).refresh_token()

        _args, __kwargs = token.set_data.call_args
        token_data = _args[0]

        self.assertEqual(token_data, response.json.return_value)

        requests_mock.post.assert_called_with(token_url, data=request_data)

    @mock.patch('oauthclient.client.requests')
    def test_revoke_token(self, requests_mock):
        revoke_url = 'http://example.com/revoke'
        provider = mock.Mock(
            client_id='id',
            client_secret='secret',
            revoke_url=revoke_url
        )
        token = mock.Mock()

        request_data = {
            'client_id': provider.client_id,
            'client_secret': provider.client_secret,
            'token': token.refresh_token,
        }

        OAuth2Client(provider, token).revoke_token()

        token.revoke.assert_called_with()

        requests_mock.post.assert_called_with(revoke_url, data=request_data)


class ProviderMixin(object):
    def get_provider(self):
        return Provider.objects.create(
            name='provider',
            client_id='id',
            client_secret='secret',
            auth_url='https://example.com/auth',
            token_url='https://example.com/token',
            uuid='af539cefe3b444f68c45de5e2a1c8090'
        )

    def get_token(self, name, provider):
        return Token.objects.create(
            name=name,
            provider=provider
        )


class OAuthClientTestCase(TestCase, ProviderMixin):
    def test_authenticate_redirect(self):
        client = Client()

        provider = self.get_provider()
        token = self.get_token('test token', provider)

        url = reverse('oauthclient:authenticate', kwargs=dict(token_uuid=str(token.uuid)))

        response = client.get(url)

        self.assertEqual(302, response.status_code)

        expected = ('https://example.com/auth'
                    '?response_type=code'
                    '&client_id=id'
                    '&state={}'
                    '&redirect_uri=http://testserver/oauthclient/auth_code').format(token.uuid)

        self.assertEqual(expected, response.get('location'))

    @mock.patch('oauthclient.client.requests')
    def test_auth_code_view(self, requests_mock):
        token_json = {
            'access_token': 'access',
            'expires_in': 3600,
            'refresh_token': 'refresh',
            'token_type': 'bearer'
        }

        requests_mock.post.return_value.json.return_value = token_json
        client = Client()

        provider = self.get_provider()
        token = self.get_token('Test token', provider=provider)

        url = reverse('oauthclient:auth_code')

        response = client.get(url, {'state': token.uuid, 'code': 'code'})

        self.assertEqual(302, response.status_code)

        token_url = reverse('oauthclient:token', kwargs={'uuid': token.uuid})

        self.assertEqual(True, (response._headers['location'][1]).endswith(token_url))


class TokenTestCase(TestCase, ProviderMixin):
    def test_from_token_data(self):
        token_data = json.loads(TOKEN_RESPONSE)

        provider = self.get_provider()
        token = Token(name='test token', provider=provider)

        token.set_data(token_data)

        self.assertEqual(True, token.id is not None)

    def test_update_existing_token(self):
        token_data = json.loads(TOKEN_RESPONSE)

        provider = self.get_provider()
        token = Token(name='test token', provider=provider)

        token_data['access_token'] = 'access'
        token_data['refresh_token'] = 'refresh'

        token.set_data(token_data)

        # ensure the data was updated in the database
        refreshed_token = Token.objects.get(pk=token.id)

        self.assertEqual('access', refreshed_token.access_token)
        self.assertEqual('refresh', refreshed_token.refresh_token)

    def test_revoke_token(self):
        token_data = json.loads(TOKEN_RESPONSE)

        provider = self.get_provider()
        token = Token(name='test token', provider=provider)

        token.set_data(token_data)

        self.assertEqual(1, provider.token_set.count())

        token.revoke()

        self.assertEqual(0, provider.token_set.count())

    @mock.patch('oauthclient.models.now')
    def test_token_is_not_expired(self, now_mock):
        """
        Ensure the token is not expried
        """
        token = Token(expires_in=3600)

        self.assertEqual(False, token.is_expired)

    @mock.patch('oauthclient.models.now')
    def test_token_is_expired(self, now_mock):
        """
        Ensure the token is expried
        """
        expires_in = 3600

        token = Token(expires_in=expires_in)
        token.modified = now()-datetime.timedelta(seconds=expires_in)

        self.assertTrue(True, token.is_expired)
