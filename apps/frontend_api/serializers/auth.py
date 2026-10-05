"""Stadium Pass — Serializers authentification."""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class OrganizationMiniSerializer(serializers.Serializer):
    """Infos minimales sur l'organisation (pour le front)."""
    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    organization = OrganizationMiniSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'email', 'first_name', 'last_name',
            'phone', 'role', 'full_name',
            'is_organizer',
            'organization',
            'date_joined',
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'password_confirm',
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte existe déjà avec cet email.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.',
            })
        try:
            validate_password(data['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            role=User.Role.SUPPORTER,
            **validated_data,
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Ajoute les infos utilisateur à la réponse du login."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data