from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import VarificationCode
from .utils import generate_verification_code, get_expiration_time
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
import uuid
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken



class SignupView(GenericAPIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = generate_verification_code()

        send_mail(
            subject='this is your verification code', 
            message=f'{otp} is your verification code',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        print('email',user.email)

        VarificationCode.objects.create(
            user=user,
            code=otp,
            purpose='email_verification',
            expired_at=get_expiration_time()
        )
    
        return Response({"user_id": str(user.id)}, status=201)


class ResendVerification(GenericAPIView):
    def post(self, request):
        user = User.objects.filter(id=request.data.get('user_id')).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
        
        otp = generate_verification_code()

        send_mail(
            subject='this is your verification code', 
            message=f'{otp} is your verification code',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        print('email',user.email)
        
        VarificationCode.objects.create(
            user=user,
            code=otp,
            purpose='email_verification',
            expired_at=get_expiration_time()
        )
        return Response({'message': 'check your email and saw that a code went this email'},status=400)


class VerifyEmailView(GenericAPIView):

    def post(self, request):
        id = request.data.get('user_id')
        if id == None:
            return({'error': 'id is invalid'})
        user = User.objects.get(id = id)
        
        otp = VarificationCode.objects.filter(
            user= user,
            code= request.data.get('verification_code'),
            purpose= 'email_verification',
            expired_at__gte=now()
        ).last()

        if not otp:
            print('inviled otp', otp)
            return Response({'error': 'Inviled code'},status=404)
        user.is_verified=True
        user.save()
        otp.delete()
        refresh = RefreshToken.for_user(user)
        print('refresh',refresh)
        return Response({
            'message': 'email verification is successfully.',
            'access_token': str(refresh.access_token),
            'access_token_valid_till': int((now()+refresh.access_token.lifetime).timestamp() * 1000),
            'refresh_token': str(refresh),
            'user_id': str(user.id),
            'user_role': user.role
        })


class SignInViwe(GenericAPIView):
    serializer_class = SignInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=400)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'access_token_valid_till': int((now()+ refresh.access_token.lifetime).timestamp() * 1000),
            'refresh_token': str(refresh),
            'user_id': str(user.id),
            'user_role': user.role
        })
    


class SignOutView(GenericAPIView):
    serializer_class = SignOutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        tokens = OutstandingToken.objects.filter(user_id=user_id)

        if not tokens.exists():
            return Response({'error': 'No active session found'}, status=404)

        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return Response({'message': 'Successfully signed out'}, status=204)



class ForgotPasswordView(GenericAPIView):
    
    def post(self, request):
        user = (User.objects.filter(email=request.data.get('email')).first() or
                User.objects.filter(phone_number=request.data.get('phone_number')).first() or
                User.objects.filter(username=request.data.get('username')).first())
        if not user:
            return Response({'error': 'Invalid user details'})
        
        otp = generate_verification_code()
        send_mail(
            subject='this code is your forgot password verificaiton code',
            message=f'{otp} is your forgot password varification code',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        code = VarificationCode.objects.create(
            user= user,
            code= otp,
            purpose= "password_reset",
            expired_at= get_expiration_time()
        )

        return Response({
            "user_id": str(user.id),
            "expires_at": int(code.expired_at.timestamp() * 1000)
        })
        

class VerificationResetCodeView(GenericAPIView):

    def post(self, request):
        user = User.objects.get(id=request.data.get('user_id'))

        otp = VarificationCode.objects.filter(
            user=user,
            code=request.data.get('verification_code'),
            purpose='password_reset',
            expired_at__gte=now()
        ).last()
        if not otp:
            return Response({
                'error': 'user_id Invalid'
            },status=404)
        otp.secret_key = uuid.uuid4()
        otp.save()

        return Response({
            "secret_key": str(otp.secret_key)
        })
    
class ResetPasswordView(GenericAPIView):

    def post(self, request):
        user = User.objects.get(id=request.data.get('user_id'))
        
        otp = VarificationCode.objects.filter(
            user = user,
            purpose = 'password_reset',
            secret_key = request.data.get('secret_key')
        ).last()

        if not otp:
            return Response({'error': 'Invalid secret_key'})
        user.set_password(request.data.get('password'))
        user.save()
        otp.delete

        return Response({'message': 'success your reset password'},status=202)
    



class RefreshTokenView(GenericAPIView):
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        token = OutstandingToken.objects.filter(user_id=user_id).order_by('-created_at').first()

        if not token:
            return Response({'error': 'No active refresh token found'}, status=404)

        refresh = RefreshToken(token.token)

        return Response({
            'access_token': str(refresh.access_token),
            'access_token_valid_till': int((now()+refresh.access_token.lifetime).timestamp()*1000)
        })
