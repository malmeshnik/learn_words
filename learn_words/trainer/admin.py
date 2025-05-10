from django.contrib import admin
from .models import (Room, 
                     Word, 
                     UserWord, 
                     SentenceTemplate,
                     SentencesTranslate,
                     Chapter,
                     Section,
                     N1,
                     N2,
                     N3,
                     N4,
                     N5,
                     N6,
                     N7,
                     N8,
                     N9,
                     N10)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)
    list_select_related = ('user',)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'en', 'ru', 'room', 'user', 'is_admin_word')
    search_fields = ('en', 'ru', 'room__name', 'user__username')
    list_filter = ('is_admin_word', 'room', 'user')
    list_select_related = ('room', 'user')


@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word', 'is_learned')
    search_fields = ('user__username', 'word__en')
    list_filter = ('is_learned',)
    list_select_related = ('user', 'word')


@admin.register(SentenceTemplate)
class SentenceTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'template', 'translate', 'created_at')
    search_fields = ('template', 'translate')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(SentencesTranslate)
class SentencesTranslateAdmin(admin.ModelAdmin):
    list_display = ('id', 'sentence_en', 'sentence_ru')
    search_fields = ('sentence_en', 'sentence_ru')
    list_filter = ('sentence_en',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)
    list_select_related = ('user',)


@admin.register(N1)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N2)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N3)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N4)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N5)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N6)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N7)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N8)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N9)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)

@admin.register(N10)
class N1Admin(admin.ModelAdmin):
    list_display = ('id', 'word')
    search_fields = ('word',)