from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'role']
        read_only_fields = ['id']
        extra_kwargs = {
            'role': {'default': 'customer'}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_staff', 'is_superuser', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined', 'is_staff', 'is_superuser']


class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)