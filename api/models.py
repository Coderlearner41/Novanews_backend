from django.db import models
from django.contrib.auth.models import User

class SavedArticle(models.Model):
    # This links the saved article to the specific user who saved it
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_articles')
    
    # Original article data we get from the Flutter app
    title = models.CharField(max_length=500)
    source_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=2000)
    image_url = models.URLField(max_length=2000, null=True, blank=True)
    published_at = models.CharField(max_length=100, null=True, blank=True)
    
    # The Gemini AI summary we generated in Flutter
    ai_summary = models.TextField()
    
    # Automatically records exactly when the user clicked the bookmark button
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - saved by {self.user.username}"