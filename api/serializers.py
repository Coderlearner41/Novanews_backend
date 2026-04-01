from rest_framework import serializers
from .models import SavedArticle

class SavedArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedArticle
        fields = '__all__'  # This tells Django to convert every column in the table to JSON
        read_only_fields = ['user', 'saved_at'] # Flutter shouldn't be able to edit these directly