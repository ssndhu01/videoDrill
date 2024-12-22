from common.models import AccountTokens
from rest_framework import authentication
from rest_framework import exceptions

class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')
        print("in here")
        if not auth:
            return None

            
        try:
            token = auth.split(' ')[1]
            account = AccountTokens.objects.get(access_token=token).account
        except AccountTokens.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid Token')

        return (account, None)
