from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # User detail
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/me/', views.UserDetailView.as_view(), {'user_id': 'me'}, name='user-me'),
    path('users/by-username/<str:username>/', views.UserByUsernameView.as_view(), name='user-by-username'),
]