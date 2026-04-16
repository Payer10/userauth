import random
from django.utils import timezone
from datetime import timedelta


def generate_verification_code():
    return str(random.randint(100000, 999999))

def get_expiration_time(days=1):
    return timezone.now() + timedelta(days=days)
