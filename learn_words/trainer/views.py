from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404, render, redirect
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.apps import apps
from gtts import gTTS
from pathlib import Path
import requests
import random
import re

from .models import (Room, 
                     Word,
                     UserSettings,
                     SentenceTemplate,
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

@login_required(login_url='/login/')
def room(request):
    rooms = Room.objects.filter(user__isnull=True)
    user_rooms = Room.objects.filter(user=request.user)
    return render(request, 'rooms.html', context={
        'rooms': rooms,
        'user_rooms': user_rooms
        })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Невірний логін або пароль')
        
    return render(request, 'login.html')
    
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Користувач з таким логіном вже існує')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('/')
        
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def add_room(request):
    if request.method == "POST":
        room_name = request.POST.get('name')
        exist_room = Room.objects.filter(name=room_name, user=request.user).exists()
        
        if exist_room:
            return JsonResponse({"success": False, "error": "Room is required"})
        else:
            user_room = Room.objects.create(name=room_name, user=request.user)
            return JsonResponse({"success": True, 'room_name': user_room.name, "room_id": user_room.id})
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@login_required
def room_words(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    words = Word.objects.filter(room=room, user__isnull = True)

    user_words = Word.objects.filter(room=room, user=request.user)

    return render(request, 
                  'room_words.html', 
                  {
                      'room': room, 
                      'words': words,
                      'user_words': user_words})

@login_required
def user_room_words(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    admin_words = Word.objects.filter(room=room_id, user__isnull = True)
    user_words = Word.objects.filter(room=room_id, user=request.user)

    return render(request,
                  'room_words.html',
                  {
                      'room': room,
                      'words': admin_words,
                      'user_words': user_words
                  })

    

@login_required
@csrf_exempt 
def add_word(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        word_en = request.POST.get('en')  
        word_ru = get_translate(word_en)
        
        room = get_object_or_404(Room, id=room_id)

        exist_word = Word.objects.filter(room=room, en=word_en).exists()

        if exist_word:
            return JsonResponse({"success": False, "error": "Word is required"})
        else:
            word = Word.objects.create(room=room, en=word_en, ru=word_ru, user=request.user)
            return JsonResponse({
                "success": True,
                "id": word.id,
                "en": word.en,
                "ru": word.ru 
            })

@login_required
def delete_room_word(request):
    body = request.body.decode('utf-8')
    data = json.loads(body)
    word_id = data.get('wordId')
    print(word_id)

    Word.objects.filter(id=word_id).delete()

    return JsonResponse({'success': True})

@csrf_exempt
@login_required
def edit_room_word(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            word_id = data.get('wordId')
            en = data.get('en')
            ru = get_translate(en)

            if not word_id or not en:
                return JsonResponse({'success': False, 'error': 'Не всі дані передані'})

            word = Word.objects.get(id=word_id, user=request.user)  # якщо є прив'язка до користувача
            word.en = en
            word.ru = ru
            word.save()

            return JsonResponse({
                'success': True,
                'word': {
                    'id': word.id,
                    'en': word.en,
                    'ru': word.ru,
                }
            })
        
        except Word.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Слово не знайдено'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Тільки POST запити дозволені'})
    
def get_category_model(category_id):
    from django.apps import apps
    try:
        return apps.get_model('trainer', f'N{category_id}')
    except LookupError:
        return None
        
@csrf_exempt
@login_required
def edit_word_simple(request):
    data = json.loads(request.body)
    word_id = data.get('word_id')
    category_id = data.get('category_id')
    new_word = data.get('word')

    Model = get_category_model(category_id)
    if not Model:
        return JsonResponse({'success': False, 'error': 'Модель не знайдено'})

    try:
        word = Model.objects.get(id=word_id)
        word.word = new_word
        word.save()
        return JsonResponse({'success': True})
    except Model.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Слово не знайдено'})

@csrf_exempt
@login_required
def delete_word_simple(request):
    data = json.loads(request.body)
    word_id = data.get('word_id')
    category_id = data.get('category_id')

    print(category_id)

    Model = get_category_model(category_id)
    if not Model:
        return JsonResponse({'success': False, 'error': 'Модель не знайдено'})

    try:
        word = Model.objects.get(id=word_id)
        print(word)
        word.delete()
        return JsonResponse({'success': True})
    except Model.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Слово не знайдено'})


@csrf_exempt
def add_selected_words(request):
    if request.method == "POST":
        body = request.body.decode('utf-8')
        print(body)
        data = json.loads(body)
        word_ids = data.get('word_ids', [])

        request.session['selected_words'] = word_ids
        request.session.modified = True

        return JsonResponse({"success": True}, status=200)
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@csrf_exempt
def add_word_to_category(request):
    if request.method == "POST":
        data = json.loads(request.body)
        word_text = data.get('word')
        category_id = data.get('category_id')
        model_name = f"N{category_id}"

        try:
            Model = apps.get_model('trainer', model_name)
            new_word = Model.objects.create(word=word_text, user=request.user)
            return JsonResponse({"success": True, 'word_id': new_word.id})
        except Exception as e:
            return JsonResponse({"success": False, 'error': str(e)})
        
    return JsonResponse({'success': False, "error": 'Invalid method'})


def learn_words(request):
    selected_word_ids = request.session.get('selected_words', [])
    selected_words_by_category = request.session.get('selected_categories', {})
    words = Word.objects.filter(id__in=selected_word_ids)
    
    # Отримуємо налаштування користувача
    user_settings = UserSettings.objects.filter(user=request.user).first()
    
    sentences = SentenceTemplate.objects.all()
    word_dict = {}

    # Якщо налаштування не знайдено, створюємо нові
    if not user_settings:
        user_settings = save_user_settings(request)
        user_settings = UserSettings.objects.filter(user=request.user).first()

    # Створюємо словник для категорій
    for category_id, ids in selected_words_by_category.items():
        model_name = f"N{category_id}"
        try:
            Model = apps.get_model(app_label='trainer', model_name=model_name)
            word_dict[category_id] = list(Model.objects.filter(id__in=ids))
            print(f"Категорія {category_id}: знайдено {len(word_dict[category_id])} слів")
        except LookupError:
            print(f"Модель {model_name} не знайдена!")
            word_dict[category_id] = []

    result_words = []
    result_sentences = []
    
    # Перевіряємо, що є вибрані слова
    if not words:
        print("Немає вибраних слів")
    
    for word in words:
        generate_mp3_if_needed(word.id, word.en, 'en', 'en')
        generate_mp3_if_needed(word.id, word.ru, 'ru', 'ru')
        result_words.append({
            'id': word.id,
            'en': word.en,
            'ru': word.ru,
        })
        
        # Для кожного слова беремо відповідні речення
        sentence_count = 0
        for sentence in sentences:
            if sentence_count >= 2:  # Обмеження на 2 речення для слова
                break
                
            template = sentence.template
            # Вилучаємо плейсхолдери з шаблону (як в оригінальному коді)
            placeholders = [word[1:-1] for word in re.findall(r'\{[^{}]+\}', template)]
            
            replaced_en = template
            replacements = {}
            
            # Замінюємо спочатку {word} на поточне слово
            replaced_en = replaced_en.replace('{word}', word.en)
            
            # Спробуємо заповнити всі плейсхолдери
            has_unfilled = False
            for placeholder in placeholders:
                if placeholder == 'word':  # Пропускаємо, оскільки вже замінили
                    continue
                    
                if placeholder in word_dict and word_dict[placeholder]:
                    category_word = random.choice(word_dict[placeholder])
                    replacements[placeholder] = category_word.word
                    replaced_en = replaced_en.replace(f"{{{placeholder}}}", category_word.word)
                else:
                    print(f"Не знайдено слів для категорії '{placeholder}'")
                    has_unfilled = True
            
            # Перевіряємо чи залишились незаповнені плейсхолдери
            if not has_unfilled and not re.search(r'\{[^{}]+\}', replaced_en):
                if replaced_en not in [s['template'] for s in result_sentences]:
                    # Переклад + озвучка
                    text_ru = get_translate(replaced_en)
                    generate_sentence_mp3(replaced_en, word, 'en', sentence.id)
                    generate_sentence_mp3(text_ru, word, 'ru', sentence.id)
                    
                    # Додаємо у результат
                    result_sentences.append({
                        'id': sentence.id,
                        'template': replaced_en,
                        'translate': text_ru
                    })
                    sentence_count += 1
            else:
                print(f"Речення пропущено: {replaced_en} (є незаповнені плейсхолдери)")

    print(f"Додано {len(result_words)} слів і {len(result_sentences)} речень")
    
    return render(request, 'learn_words.html', {
        'words': result_words,
        'sentence': result_sentences,
        'user_settings': user_settings,
    })

def save_user_settings(request):
    if request.method == 'POST':
        # Перетворюємо байтовий потік в JSON
        try:
            data = json.loads(request.body)
        except:
            data = {}

        # Отримуємо налаштування користувача
        user_settings = data.get('user_settings', {})
        print(user_settings)

        repeat_count = user_settings.get('repetitions', 1)
        pause_between = float(user_settings.get('pauseBetween', 1000)) / 1000
        delay_before_translation = float(user_settings.get('delayBeforeTranslation', 500)) / 1000
        hide_translation = user_settings.get('hide_translation', False)
        playback_speed = float(user_settings.get('playbackSpeed', 1))

        print(repeat_count, pause_between, delay_before_translation, hide_translation)

        # Оновлюємо або створюємо нові налаштування
        user_settings_instance, created = UserSettings.objects.update_or_create(
            user=request.user,
            defaults={
                'repeat_count': repeat_count,
                'pause_between': pause_between,
                'delay_before_translation': delay_before_translation,
                'hide_translation': hide_translation,
                'playback_speed': playback_speed
            }
        )

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def choose_category(request):
    categories = [
        {
            "id": 1,
            "name": "Займенник",
            "words": N1.objects.all() 
        },
        {
            "id": 2,
            "name": "Глагол",
            "words": N2.objects.all() 
        },
        {
            "id": 3,
            "name": "Где",
            "words": N3.objects.all() 
        },
        {
            "id": 4,
            "name": "Когда",
            "words": N4.objects.all() 
        },
        {
            "id": 5,
            "name": "5",
            "words": N5.objects.all() 
        }
    ]

    return render(request, "choose_categories.html", {"categories": categories})

@csrf_exempt
def add_selected_categories(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            words_by_category = data.get("words_by_category", {})

            # Debug:
            print("Отримано:", words_by_category)

            # Збереження в сесію або обробка для БД
            request.session["selected_categories"] = words_by_category

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})

def generate_mp3_if_needed(word_id, text, lang, subfolder):
    filename = f'media/audio/{subfolder}/{word_id}.mp3'
    path = Path(filename)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tts = gTTS(text=text, lang=lang)
        tts.save(str(path))

def generate_sentence_mp3(sentence, word, lang, sentence_id):
    file_path = f"media/audio/sentence/{lang}/sentence_{sentence_id}_{word.id}_{lang}.mp3"
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=sentence, lang=lang)
    tts.save(file_path)

def get_translate(text: str) -> str:
    url = "https://google-translate-official.p.rapidapi.com/translate"

    payload = {
        "texte": text,
        "source": "auto",
        "to_lang": "ru"
    }
    headers = {
        "x-rapidapi-key": "99220db1a8mshe97ffbd5e65a6cbp14cfeejsn6155e9e7d15b",
        "x-rapidapi-host": "google-translate-official.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    translate = response.json().get('translation_data').get('translation')

    return translate

