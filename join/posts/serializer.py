
from posts.models import Post
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post Model.
    
    Converts model`s objects to JSON and back.
    """
    class Meta:
        model = Post  # работает с моделью Post
        fields = ['title', 'anons', 'text', 'group', 'author']
        # Указываем поля модели, с которыми будет работать сериализатор;
        # поля модели, не указанные в перечне, сериализатор будет игнорировать.
