from rest_framework import serializers
from .models import Room, Word, UserWord

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class UserWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWord
        fields = '__all__'
