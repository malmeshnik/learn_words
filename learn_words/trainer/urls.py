from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.room, name='index'),
    path('add_room/', views.add_room, name='add_room'),
    path('room/<int:room_id>/', views.room_words, name='room_words'),
    path('room/user/<int:room_id>', views.user_room_words, name='user_room_words'),
    path('add_word/', views.add_word, name='add_word'),
    path('add-selected-words/', views.add_selected_words, name='add_selected_words'),
    path('add_selected_categories/', views.add_selected_categories, name='add_selected_categories'),
    path("learn/", views.learn_words, name="learn_words"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.choose_category, name='categories'),
    path('add_word_to_category/', views.add_word_to_category, name='add_word_to_category'),
    path('save_user_settings/', views.save_user_settings, name='save_user_settings')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)