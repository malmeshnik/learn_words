from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.section, name='index'),
    path('edit_section/', views.edit_section, name='edit_section'),
    path('delete_section/', views.delete_section, name='delete_section'),
    path('add_section/', views.add_section, name='add_section'),
    path('chapters/<int:section_id>', views.chapter, name='chapters'),
    path('rooms/<int:chapter_id>', views.room, name='rooms'),
    path('edit_chapter/', views.edit_chapter, name='edit_chapter'),
    path('delete_chapter/', views.delete_chapter, name='delete_chapter'),
    path('add_chapter/', views.add_chapter, name='add_chapter'),
    path('add_room/', views.add_room, name='add_room'),
    path('rooms/room/<int:room_id>/', views.room_words, name='room_words'),
    path('rooms/room/user/<int:room_id>', views.user_room_words, name='user_room_words'),
    path('add_word/', views.add_word, name='add_word'),
    path('add-selected-words/', views.add_selected_words, name='add_selected_words'),
    path('add_selected_categories/', views.add_selected_categories, name='add_selected_categories'),
    path("learn/", views.learn_words, name="learn_words"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.choose_category, name='categories'),
    path('add_word_to_category/', views.add_word_to_category, name='add_word_to_category'),
    path('save_user_settings/', views.save_user_settings, name='save_user_settings'),
    path('delete_room_word/', views.delete_room_word, name='delete_room_word'),
    path('edit_word/', views.edit_room_word, name='edit_word'),
    path('delete_word_simple/', views.delete_word_simple, name='delete_word_simple'),
    path('edit_word_simple/', views.edit_word_simple, name='edit_word_simple'),
    path('delete_room/', views.delete_room, name='delete_room'),
    path('edit_room/', views.edit_room, name='edit_room'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)