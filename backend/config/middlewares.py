from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

# from django.db import close_old_connections

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.backends import TokenBackend

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from urllib.parse import parse_qs


User = get_user_model()


class JWTAuthMiddlewareStack(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        await self.check_credentials(scope)
        return await self.inner(scope, receive, send)

    async def check_credentials(self, scope):
        token = await self._get_token(scope)
        if token:
            # Get the user by token
            scope["user"] = await self.get_user(token)
        else:
            scope["user"] = AnonymousUser()

    @staticmethod
    async def _get_token(scope):
        # Close old database connections to prevent usage of timed out connections
        # close_old_connections()

        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_key = headers[b'authorization'].decode()
            try:
                UntypedToken(token_key)
            except (InvalidToken, TokenError):
                return
        return token_key

    @staticmethod
    @database_sync_to_async
    def get_user(token):
        data = TokenBackend(algorithm="HS256").decode(token, verify=False)
        try:
            return User.objects.get(id=data["user_id"])

        except User.DoesNotExist:
            return AnonymousUser()
