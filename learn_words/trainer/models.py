from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class VoicePreferenceType(models.TextChoices):
    TTS = 'tts', 'Default TTS'
    OWN = 'own', 'Own Recordings'
    OTHER_USER = 'other_user', 'Other User Recording'

class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    repeat_count = models.SmallIntegerField(default=1)
    pause_between = models.FloatField(default=1)
    delay_before_translation = models.FloatField(default=0.5)
    hide_translation = models.BooleanField(default=False)
    playback_speed = models.FloatField(default=1, null=False, blank=False)
    lesson_repeat_count = models.SmallIntegerField(default=1)
    use_own_recordings_if_available = models.BooleanField(default=False) # Will be deprecated by voice_preference_type

    voice_preference_type = models.CharField(
        max_length=10,
        choices=VoicePreferenceType.choices,
        default=VoicePreferenceType.TTS
    )
    preferred_other_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_by_users',
        help_text="The user whose voice recordings are preferred, if voice_preference_type is 'other_user'."
    )

class Section(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='chapters', blank=True, null=True)

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

class SentencesTranslate(models.Model):
    sentence_en = models.CharField(max_length=255)
    sentence_ru = models.CharField(max_length=255)

    def __str__(self):
        return self.sentence_ru

class N1(models.Model):
    word = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='N1', null=True, blank=True)

    def __str__(self):
        return self.word

class WordRecording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    recording = models.FileField(upload_to='word_recordings/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.word.en} - Recording"

class UserSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.content_object}"
    
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