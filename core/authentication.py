import jwt

from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from rest_framework import exceptions

from core.utils import jwt_decode_handler, jwt_get_user_from_payload

from user_mgmt.models import UserMaster


class JSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwe_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
            user = self.authenticate_credentials(payload)

            return user, jwt_value
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.NotAcceptable(msg)
        except jwt.InvalidTokenError:
            raise exceptions.NotAcceptable()

    def get_jwe_value(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        elif len(auth) > 1:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.PermissionDenied(msg)

        return auth[0].decode('utf-8')

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's username.
        """
        User = get_user_model()
        user_id = jwt_get_user_from_payload(payload)

        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.NotAcceptable(msg)

        try:
            user = UserMaster.objects.get(id=user_id)
        except UserMaster.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.NotAcceptable(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.NotAcceptable(msg)

        return user

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """

        return 'Invalid Token. Kindly refresh the token.'
