# from rest_framework import serializers
# from .models import User

# class SignUpSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'email',
#             'username',
#             'is_terms_service',
#             'password1',
#             'password2',
#             # 'phone_number',
#             # 'phone_country_code',
#             # 'full_name',
#         ]
#         extra_kwargs = {
#             'password1': {'write_only': True},
#             'password2': {'write_only': True},
#         }

#     def create(self, validated_data):
#         password1 = validated_data.pop('password1')
#         password2 = validated_data.pop('password2')

#         if password1 != password2:
#             raise serializers.ValidationError("Passwords do not match")
        
#         if not validated_data.get('is_terms_service'):
#             raise serializers.ValidationError("You must agree to the terms of service")

#         user = User(**validated_data)
#         user.set_password(password1)
#         user.save()
#         return user
        


from rest_framework import serializers
from .models import User

class SignUpSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'is_terms_service',
            'password1',
            'password2',
        ]

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")

        if not attrs.get('is_terms_service'):
            raise serializers.ValidationError("You must agree to the terms of service")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user





class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    # phone_number = serializers.CharField(required=False)




    def validate(self, data):
        user = None
        if data.get('email'):
            user = User.objects.filter(email=data['email']).first()
        if data.get('username'):
            user = User.objects.filter(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_verified:
            raise serializers.ValidationError("User is not verified")
        
        # if data.get('phone_number'):
        #     user = User.objects.filter(phone_number=data['phone_number']).first()

        
        return user


class SignOutSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()



class RefreshTokenSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
