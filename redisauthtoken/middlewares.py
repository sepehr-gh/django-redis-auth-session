from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import Model
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import get_authorization_header


class AuthenticationMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        user = SimpleLazyObject(lambda: self.get_user(request))
        request.user = user
        request._cached_user = user

    def get_user(self, request):
        user_model: Model = apps.get_model(settings.AUTH_USER_MODEL)
        try:
            user_id = request.session.get("user_id", None)
            user = user_model.objects.get(id=user_id)
        except Model.DoesNotExist:
            user = AnonymousUser()
        return user


class AuthorizationTokenSession(SessionMiddleware):
    """
    Instead of reading session id from COOKIE, we read it from Authorization header
    """

    keyword = 'Token'

    def __init__(self, get_response=None):
        super(AuthorizationTokenSession, self).__init__(get_response=get_response)

    def __get_session_key(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        token = None
        if len(auth) == 2:
            try:
                token = auth[1].decode()
            except UnicodeError:
                pass
        return token

    def process_request(self, request):
        request.session = self.SessionStore(self.__get_session_key(request))

    def process_response(self, request, response):
        try:
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response
        if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
            if response.status_code != 500:
                try:
                    request.session.save()
                except UpdateError:
                    raise SessionInterrupted(
                        "The request's session was deleted before the "
                        "request completed. The user may have logged "
                        "out in a concurrent request, for example."
                    )
        return response
