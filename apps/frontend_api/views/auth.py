"""Stadium Pass — Vues authentification."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers.auth import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue de login JWT retournant aussi les infos utilisateur."""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouveau supporter."""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Retourne l'utilisateur connecté."""
    return Response(UserSerializer(request.user).data)
