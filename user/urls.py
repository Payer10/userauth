from django.urls import path
from .views import SignupView, ResendVerification, VerifyEmailView, SignInViwe, ForgotPasswordView, VerificationResetCodeView, ResetPasswordView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('resend-verification/', ResendVerification.as_view(), name='resend_verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('signin-user/', SignInViwe.as_view(), name="user-signin"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verification-forgot/', VerificationResetCodeView.as_view(), name='verify-forgot'),
    path('reset-password/', ResetPasswordView.as_view(), name="reset_password")
]

