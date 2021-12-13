from django.contrib.auth.backends import ModelBackend


class FinvestBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print("Authenticate is called", username, password)
        user = super(FinvestBackend, self).authenticate(request, username=username, password=password, **kwargs)
        if user:
            return user
        return

    def get_user(self, user_id):
        print(">>>>", user_id)
        return super(FinvestBackend, self).get_user(user_id)
