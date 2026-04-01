from rest_framework import generics, permissions
from .models import SavedArticle
from .serializers import SavedArticleSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# 1. Endpoint to GET all saved articles, or POST a new one
class SavedArticleListCreate(generics.ListCreateAPIView):
    serializer_class = SavedArticleSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can do this

    def get_queryset(self):
        # SECURITY: Only return articles saved by the specific user making the request
        return SavedArticle.objects.filter(user=self.request.user).order_by('-saved_at')

    def perform_create(self, serializer):
        # When saving a new article, automatically assign it to the logged-in user
        serializer.save(user=self.request.user)

# 2. Endpoint to DELETE a saved article
class SavedArticleDelete(generics.DestroyAPIView):
    serializer_class = SavedArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # SECURITY: Ensure a user can only delete their own articles
        return SavedArticle.objects.filter(user=self.request.user)


# 3. Endpoint for User Registration (Sign Up)
class RegisterUser(APIView):
    permission_classes = [permissions.AllowAny] # Anyone can access the signup page

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Generate their unique token
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'username': user.username
        }, status=status.HTTP_201_CREATED)