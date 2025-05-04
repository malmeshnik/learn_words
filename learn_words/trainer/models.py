from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    repeat_count = models.SmallIntegerField(default=1)
    pause_between = models.FloatField(default=1)
    delay_before_translation = models.FloatField(default=0.5)
    hide_translation = models.BooleanField(default=False)
    playback_speed = models.FloatField(default=1, null=False, blank=False)
    lesson_repeat_count = models.SmallIntegerField(default=1)

class Chapter(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Room(models.Model):
    name = models.CharField(max_length=255)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class Word(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='words')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    en = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True)
    is_admin_word = models.BooleanField(default=True)

    def __str__(self):
        return self.en
    
class UserWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='user_words')
    is_learned = models.BooleanField(default=False)

class SentenceTemplate(models.Model):
    template = models.CharField(max_length=255)
    translate = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.template

class N1(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N1', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N2(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N2', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N3(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N3', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N4(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N4', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N5(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N5', null=True, blank=True)

    def __str__(self):
        return self.word

class N6(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N6', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N7(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N7', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N8(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N8', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N9(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N9', null=True, blank=True)

    def __str__(self):
        return self.word
    
class N10(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N10', null=True, blank=True)

    def __str__(self):
        return self.word