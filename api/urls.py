from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'), # Built-in view!

    # --- Article URLs ---
    path('articles/', views.SavedArticleListCreate.as_view(), name='article-list-create'),
    path('articles/<int:pk>/', views.SavedArticleDelete.as_view(), name='article-delete'),
]