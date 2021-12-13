from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from redisauthtoken.models import Token


class ObtainTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not request.session.session_key:
            request.session.create()
        request.session["user_id"] = user.id
        print("logging in " + str(user.id))
        session_key = request.session.session_key
        token, created = Token.objects.get_or_create(user=user, key=session_key)
        return Response({'token': token.key, 'refresh': token.refresh})


class SessionTestView(APIView):

    def get(self, request):
        print(request.user.id)
        print(request.user)
        print(request.session.get("key"))
        print(request.session.get("user_id"))
        # print(User.objects.get(pk=request.session.get("user_id")))
        print(request.session)
        return Response()
