import datetime

from django.db import models
from django.utils.timezone import now

from model_utils.models import TimeStampedModel
from uuidfield import UUIDField


class Provider(TimeStampedModel):
    uuid = UUIDField(auto=True)

    name = models.CharField(max_length=32)
    client_id = models.CharField(max_length=32)
    client_secret = models.CharField(max_length=32)
    auth_url = models.URLField()
    token_url = models.URLField()
    revoke_url = models.URLField()

    def __unicode__(self):
        return unicode(self.name)

    @property
    def token(self):
        return self.token_set.get()


class Token(TimeStampedModel):
    uuid = UUIDField(auto=True)

    provider = models.ForeignKey('Provider')

    name = models.CharField(max_length=32)

    access_token = models.CharField(max_length=64, blank=True)
    expires_in = models.IntegerField(default=0)
    refresh_token = models.CharField(max_length=128, blank=True)
    token_type = models.CharField(max_length=32, default='bearer')

    def __unicode__(self):
        return unicode(self.name)

    @property
    def expires(self):
        return self.modified + datetime.timedelta(seconds=self.expires_in)

    @property
    def is_expired(self):
        return now() >= self.expires

    def revoke(self):
        """
        Deletes the token
        :return: None
        """
        self.delete()

    def set_data(self, token_data):
        """
        Sets the token using the given data

        :param token_data: dictionary from OAuth2Client.set_token_from_auth_code()
        :return: None
        """
        self.access_token = token_data['access_token']
        self.expires_in = token_data['expires_in']
        self.refresh_token = token_data['refresh_token']
        self.token_type = token_data['token_type']

        self.save()


class TokenRestrictedTo(models.Model):
    token = models.ForeignKey('Token', related_name='restricted_to')
    value = models.CharField(max_length=256)
