from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneNumberAuthBackend:
    """
    Custom authentication backend.
    Allows users to log in using their phone numbers.
    """
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(phone_number=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None