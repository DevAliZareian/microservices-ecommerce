from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)
from accounts.services import auth_service
from accounts.selectors.user_selector import get_user_by_id, get_user_by_username
from shared.common.responses import success_response, error_response
from shared.common.exceptions import NotFoundError


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.validated_data.pop('password2', None)
        user = auth_service.register_user(**serializer.validated_data)
        data = {"id": user.id, "username": user.username, "email": user.email}
        return success_response(data=data, http_status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        return success_response(
            data=serializer.validated_data, http_status=status.HTTP_200_OK
        )


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        return success_response(
            data=serializer.validated_data, http_status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user, context={'request': request}).data
        return success_response(data=data)

    def patch(self, request):
        try:
            profile = request.user.profile
        except Exception:
            return error_response(
                errors={'detail': 'User profile not found'},
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return success_response(data=serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return error_response(
                errors=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        auth_service.change_user_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password'],
        )
        return success_response(data={"detail": "Password changed successfully."})


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        try:
            if user_id == 'me':
                user = request.user
            else:
                user = get_user_by_id(int(user_id))
            data = UserSerializer(user).data
            return success_response(data=data)
        except NotFoundError as e:
            return error_response(
                errors={'detail': str(e)},
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except (ValueError, TypeError):
            return error_response(
                errors={'detail': 'Invalid user ID'},
                http_status=status.HTTP_400_BAD_REQUEST,
            )


class UserByUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = get_user_by_username(username)
            data = UserSerializer(user).data
            return success_response(data=data)
        except NotFoundError as e:
            return error_response(
                errors={'detail': str(e)},
                http_status=status.HTTP_404_NOT_FOUND,
            )
