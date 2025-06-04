import json
import json # Ensured
import os # Ensured
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile # Ensured
from .models import Section, Chapter, Room, Word, UserSelection, UserSettings, WordRecording # Ensured WordRecording

class UserSelectionModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        # Line causing IntegrityError removed:
        # cls.word = Word.objects.create(en='test word', ru='тестовое слово', user=cls.user)
        # Correct setup for word_in_room is below and sufficient for tests using it.
        cls.section = Section.objects.create(name='Test Section', user=cls.user)
        cls.chapter = Chapter.objects.create(name='Test Chapter', section=cls.section, user=cls.user)
        cls.room = Room.objects.create(name='Test Room', chapter=cls.chapter, user=cls.user)
        cls.word_in_room = Word.objects.create(room=cls.room, en='word in room', ru='слово в комнате', user=cls.user)


    def test_create_user_selection_for_word(self):
        selection = UserSelection.objects.create(
            user=self.user,
            content_object=self.word_in_room
        )
        self.assertEqual(selection.content_object, self.word_in_room)
        self.assertIsNotNone(selection.created_at)
        self.assertIsNotNone(selection.updated_at)
        self.assertEqual(str(selection), f"{self.user.username} - {self.word_in_room.en}")

    def test_create_user_selection_for_section(self):
        selection = UserSelection.objects.create(
            user=self.user,
            content_object=self.section
        )
        self.assertEqual(selection.content_object, self.section)
        self.assertEqual(str(selection), f"{self.user.username} - {self.section.name}")


class UpdateSelectionViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='viewtestuser', password='password123')
        cls.section = Section.objects.create(name='Sample Section') # Admin section
        # Line causing IntegrityError removed:
        # cls.word = Word.objects.create(en='sample word', ru='пример слова', is_admin_word=True)
        # Correct setup for test_word is below and sufficient.
        admin_user = User.objects.create_user(username='admin', password='password')
        s = Section.objects.create(name="Admin Section")
        c = Chapter.objects.create(name="Admin Chapter", section=s)
        r = Room.objects.create(name="Admin Room", chapter=c)
        cls.test_word = Word.objects.create(room=r, en="test word for view", ru="тест", is_admin_word=True)


    def setUp(self):
        self.client = Client()
        self.client.login(username='viewtestuser', password='password123')
        self.update_url = reverse('update_selection')

    def test_update_selection_login_required(self):
        self.client.logout()
        response = self.client.post(self.update_url, data={}, content_type='application/json')
        self.assertEqual(response.status_code, 302) # Redirects to login
        self.assertIn(reverse('login'), response.url)


    def test_update_selection_post_only(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'Invalid request method')

    def test_update_selection_missing_data(self):
        payloads = [
            {"item_id": self.test_word.id, "item_type": "word"}, # Missing is_checked
            {"item_id": self.test_word.id, "is_checked": True},  # Missing item_type
            {"item_type": "word", "is_checked": True},         # Missing item_id
        ]
        for payload in payloads:
            response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['error'], 'Missing data')

    def test_update_selection_invalid_item_type(self):
        payload = {"item_id": self.test_word.id, "item_type": "invalidtype", "is_checked": True}
        response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid item type', response.json()['error'])

    def test_update_selection_item_not_found(self):
        payload = {"item_id": 99999, "item_type": "word", "is_checked": True} # Non-existent word ID
        response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Word not found', response.json()['error']) # Based on view's error message

    def test_select_item_success(self):
        payload = {"item_id": self.test_word.id, "item_type": "word", "is_checked": True}
        response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'created')
        self.assertTrue(UserSelection.objects.filter(user=self.user, object_id=self.test_word.id).exists())

    def test_select_item_already_exists(self):
        # First, select the item
        UserSelection.objects.create(user=self.user, content_object=self.test_word)

        payload = {"item_id": self.test_word.id, "item_type": "word", "is_checked": True}
        response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'exists')

    def test_deselect_item_success(self):
        # First, select the item
        UserSelection.objects.create(user=self.user, content_object=self.test_word)
        self.assertTrue(UserSelection.objects.filter(user=self.user, object_id=self.test_word.id).exists())

        payload = {"item_id": self.test_word.id, "item_type": "word", "is_checked": False}
        response = self.client.post(self.update_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'deleted')
        self.assertFalse(UserSelection.objects.filter(user=self.user, object_id=self.test_word.id).exists())

class DeleteSelectedWordsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1del', password='password123')
        cls.user2 = User.objects.create_user(username='user2del', password='password123')

        # Room setup for words
        section = Section.objects.create(name='Del Section')
        chapter = Chapter.objects.create(name='Del Chapter', section=section)
        room = Room.objects.create(name='Del Room', chapter=chapter)

        cls.word1_user1 = Word.objects.create(room=room, en='word1_user1', ru='w1u1', user=cls.user1)
        cls.word2_user1 = Word.objects.create(room=room, en='word2_user1', ru='w2u1', user=cls.user1)
        cls.word_user2 = Word.objects.create(room=room, en='word_user2', ru='wu2', user=cls.user2)
        cls.admin_word = Word.objects.create(room=room, en='admin_word_del', ru='awd', is_admin_word=True) # No specific user

    def setUp(self):
        self.client = Client()
        self.client.login(username='user1del', password='password123')
        self.delete_url = reverse('delete_selected_words')

    def test_delete_selected_words_login_required(self):
        self.client.logout()
        response = self.client.post(self.delete_url, data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_delete_selected_words_post_only(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'Invalid request method')

    def test_delete_selected_words_missing_ids(self):
        response = self.client.post(self.delete_url, data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid or missing word_ids')

    def test_delete_selected_words_empty_ids_list(self):
        payload = {"word_ids": []}
        response = self.client.post(self.delete_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid or missing word_ids')

    def test_delete_selected_words_invalid_id_format(self):
        payload = {"word_ids": ["abc", self.word1_user1.id]}
        response = self.client.post(self.delete_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid word ID format in list.')

    def test_delete_selected_words_success_own_words(self):
        payload = {"word_ids": [str(self.word1_user1.id), str(self.word2_user1.id)]} # IDs from JS are strings
        response = self.client.post(self.delete_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 2)
        self.assertFalse(Word.objects.filter(id=self.word1_user1.id).exists())
        self.assertFalse(Word.objects.filter(id=self.word2_user1.id).exists())
        self.assertTrue(Word.objects.filter(id=self.word_user2.id).exists()) # Ensure other user's word is safe
        self.assertTrue(Word.objects.filter(id=self.admin_word.id).exists()) # Ensure admin word is safe

    def test_delete_selected_words_mixed_ownership_and_admin(self):
        # Attempt to delete one owned word, one word owned by another user, and one admin word
        payload = {"word_ids": [str(self.word1_user1.id), str(self.word_user2.id), str(self.admin_word.id)]}
        response = self.client.post(self.delete_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 1) # Only self.word1_user1 should be deleted
        self.assertFalse(Word.objects.filter(id=self.word1_user1.id).exists())
        self.assertTrue(Word.objects.filter(id=self.word_user2.id).exists()) # User2's word should remain
        self.assertTrue(Word.objects.filter(id=self.admin_word.id).exists()) # Admin word should remain

    def test_delete_non_existent_word_ids(self):
        payload = {"word_ids": [str(self.word1_user1.id), "99999"]} # 99999 is a non-existent ID
        response = self.client.post(self.delete_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200) # The view itself doesn't error on non-existent IDs, filter just won't find them
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 1) # Only self.word1_user1 is deleted
        self.assertFalse(Word.objects.filter(id=self.word1_user1.id).exists())


class CheckboxStateTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='checkboxtestuser', password='password123')

        # Full hierarchy for the word
        cls.section = Section.objects.create(name='CB Section', user=cls.user)
        cls.chapter = Chapter.objects.create(name='CB Chapter', section=cls.section, user=cls.user)
        cls.room = Room.objects.create(name='CB Room', chapter=cls.chapter, user=cls.user)
        cls.word = Word.objects.create(room=cls.room, en='checkbox word', ru='чекбокс слово', user=cls.user)
        cls.admin_word_in_room = Word.objects.create(room=cls.room, en='admin checkbox word', ru='админ чекбокс', is_admin_word=True)

    def setUp(self):
        self.client = Client()
        self.client.login(username='checkboxtestuser', password='password123')
        # URL for the room_words page where the word is displayed
        self.room_words_url = reverse('room_words', args=[self.room.id])

    def test_checkbox_checked_for_selected_user_word(self):
        # Create a UserSelection for the user's own word
        UserSelection.objects.create(user=self.user, content_object=self.word)

        response = self.client.get(self.room_words_url)
        self.assertEqual(response.status_code, 200)

        # More robust check for the specific checkbox being checked
        # Check if data-item-id="word.id" is followed by "checked" within the same input tag
        # This is still a bit brittle but better than just checking for "checked" anywhere.
        # Note: The class list in the expected HTML should match exactly what's rendered.
        # Let's assume it's "word-checkbox item-checkbox"

        # For user_words list
        # Looking for <input ... data-item-id="self.word.id" ... checked>
        response_content = response.content.decode('utf-8')

        # Construct a pattern that's specific enough
        # Ensure attributes can be in any order within the input tag by using lookaheads if needed,
        # or by parsing more carefully. For now, a targeted string:
        checkbox_html_pattern = f'<input class="word-checkbox item-checkbox" type="checkbox" name="selected_words" value="{self.word.id}" data-item-type="word" data-item-id="{self.word.id}" checked>'

        # A less fragile way is to find the input tag by a unique attribute like data-item-id,
        # then check if 'checked' is in that tag's string representation.

        # Find the specific input tag for self.word (user word)
        # This assumes word.id is unique enough on the page for this test.
        # The list of user_words is separate in the template.

        # We search for the input tag related to self.word.id
        # A simple way to check: find the input tag and see if 'checked' is in its definition.
        # This can be made more robust with HTML parsing libraries if needed.
        word_checkbox_marker = f'data-item-id="{self.word.id}"'

        # Split the content by this marker. If the word exists, we'll get multiple parts.
        parts = response_content.split(word_checkbox_marker)
        self.assertTrue(len(parts) > 1, f"Checkbox for word ID {self.word.id} not found in response.")

        # The 'checked' attribute should be in the part of the string that defines this specific checkbox.
        # The part *before* the next opening tag '>' of this input element.
        input_tag_relevant_part = parts[1].split('>')[0]
        self.assertIn('checked', input_tag_relevant_part,
                      f"Checkbox for word ID {self.word.id} was expected to be checked. Part: {input_tag_relevant_part}")


    def test_checkbox_not_checked_for_unselected_user_word(self):
        # No UserSelection for self.word
        response = self.client.get(self.room_words_url)
        self.assertEqual(response.status_code, 200)
        response_content = response.content.decode('utf-8')

        word_checkbox_marker = f'data-item-id="{self.word.id}"'
        parts = response_content.split(word_checkbox_marker)
        self.assertTrue(len(parts) > 1, f"Checkbox for word ID {self.word.id} not found.")

        input_tag_relevant_part = parts[1].split('>')[0]
        self.assertNotIn('checked', input_tag_relevant_part,
                         f"Checkbox for word ID {self.word.id} was expected NOT to be checked. Part: {input_tag_relevant_part}")

    def test_checkbox_checked_for_selected_admin_word(self):
        # Create a UserSelection for the admin word
        UserSelection.objects.create(user=self.user, content_object=self.admin_word_in_room)

        response = self.client.get(self.room_words_url)
        self.assertEqual(response.status_code, 200)
        response_content = response.content.decode('utf-8')

        admin_word_checkbox_marker = f'data-item-id="{self.admin_word_in_room.id}"'
        parts = response_content.split(admin_word_checkbox_marker)
        self.assertTrue(len(parts) > 1, f"Checkbox for admin word ID {self.admin_word_in_room.id} not found.")

        input_tag_relevant_part = parts[1].split('>')[0]
        self.assertIn('checked', input_tag_relevant_part,
                      f"Checkbox for admin word ID {self.admin_word_in_room.id} was expected to be checked. Part: {input_tag_relevant_part}")


# Imports for VoiceRecordingTests (ensure these are at the top of the file with other imports)
# from django.core.files.uploadedfile import SimpleUploadedFile
# from .models import WordRecording (Word, Room, Chapter, Section should be there)
# import os (if manual file cleanup is used)

class VoiceRecordingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser_rec', password='password123')
        # Create Section and Chapter if Room requires them
        cls.section = Section.objects.create(name='Test Rec Section')
        cls.chapter = Chapter.objects.create(name='Test Rec Chapter', section=cls.section)
        cls.room = Room.objects.create(name='Test Rec Room', chapter=cls.chapter)
        cls.word = Word.objects.create(room=cls.room, en='hello_rec', ru='привет_rec')
        cls.word_no_recording = Word.objects.create(room=cls.room, en='world_rec', ru='мир_rec')
        cls.other_recordist = User.objects.create_user(username='other_recordist_user', password='password123')
        cls.word2 = Word.objects.create(room=cls.room, en='bye_rec', ru='пока_rec')


        # URL for upload view
        cls.upload_url = reverse('upload_word_recording', args=[cls.word.id])
        cls.room_words_url = reverse('room_words', args=[cls.room.id])

    def test_word_recording_creation(self):
        audio_content = b'dummy audio data'
        audio_file = SimpleUploadedFile("test_audio.webm", audio_content, content_type="audio/webm")

        recording = WordRecording.objects.create(
            user=self.user,
            word=self.word,
            recording=audio_file
        )
        self.assertEqual(WordRecording.objects.count(), 1)
        self.assertEqual(recording.user, self.user)
        self.assertEqual(recording.word, self.word)
        self.assertTrue(recording.recording.name.startswith('word_recordings/test_audio'))

        # Cleanup
        if hasattr(recording.recording, 'path'):
            import os
            if os.path.exists(recording.recording.path):
                os.remove(recording.recording.path)
        recording.delete()

    def test_upload_recording_unauthenticated(self):
        client = Client() # New client for unauthenticated request
        response = client.post(self.upload_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_upload_recording_authenticated_success(self):
        self.client.login(username='testuser_rec', password='password123')
        audio_content = b'new audio data'
        audio_file = SimpleUploadedFile("upload_test.webm", audio_content, content_type="audio/webm")

        initial_recording_count = WordRecording.objects.count()

        response = self.client.post(self.upload_url, {'recording': audio_file})

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertEqual(WordRecording.objects.count(), initial_recording_count + 1)

        recording = WordRecording.objects.get(user=self.user, word=self.word)
        self.assertTrue(recording.recording.url)
        self.assertEqual(json_response['recording_url'], recording.recording.url)

        if hasattr(recording.recording, 'path'):
            import os
            if os.path.exists(recording.recording.path):
                os.remove(recording.recording.path)
        recording.delete()

    def test_upload_recording_missing_file(self):
        self.client.login(username='testuser_rec', password='password123')
        response = self.client.post(self.upload_url, {})
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'No recording file provided.')

    def test_upload_recording_invalid_word_id(self):
        self.client.login(username='testuser_rec', password='password123')
        invalid_url = reverse('upload_word_recording', args=[99999])
        audio_content = b'audio for invalid word'
        audio_file = SimpleUploadedFile("invalid.webm", audio_content, content_type="audio/webm")
        response = self.client.post(invalid_url, {'recording': audio_file})
        self.assertEqual(response.status_code, 404)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'Word not found.')

    def test_room_words_view_context_with_recording(self):
        self.client.login(username='testuser_rec', password='password123')

        audio_content = b'context test audio'
        audio_file = SimpleUploadedFile("context_audio.webm", audio_content, content_type="audio/webm")
        user_recording = WordRecording.objects.create(
            user=self.user,
            word=self.word,
            recording=audio_file
        )

        response = self.client.get(self.room_words_url)
        self.assertEqual(response.status_code, 200)

        found_word_in_context = None
        # Words created by users (like self.word) are expected in 'user_words' if the view logic is standard
        # or if it's an admin word that the user has interacted with.
        # Given self.word was created without user=self.user, it would be a general word.
        # Let's adjust the test assumption: self.word is a general word.
        # If self.word was user-specific, it would be in response.context['user_words']

        # Test word (self.word) is a general word in this setup
        for word_obj in response.context['words']:
            if word_obj.id == self.word.id:
                found_word_in_context = word_obj
                break
        # If it could also be a user word (e.g. if user added it)
        if not found_word_in_context and 'user_words' in response.context:
           for word_obj in response.context['user_words']:
               if word_obj.id == self.word.id:
                   found_word_in_context = word_obj
                   break

        self.assertIsNotNone(found_word_in_context, f"Test word (ID: {self.word.id}) not found in context lists.")
        self.assertTrue(hasattr(found_word_in_context, 'user_recording_url'),
                        f"Word (ID: {self.word.id}) missing 'user_recording_url' attribute.")
        self.assertEqual(found_word_in_context.user_recording_url, user_recording.recording.url)

        word_without_rec_in_context = None
        for word_obj in response.context['words']:
            if word_obj.id == self.word_no_recording.id:
                word_without_rec_in_context = word_obj
                break
        if not word_without_rec_in_context and 'user_words' in response.context:
            for word_obj in response.context['user_words']:
                if word_obj.id == self.word_no_recording.id:
                    word_without_rec_in_context = word_obj
                    break

        self.assertIsNotNone(word_without_rec_in_context, f"Word_no_recording (ID: {self.word_no_recording.id}) not found in context.")
        self.assertTrue(hasattr(word_without_rec_in_context, 'user_recording_url'),
                        f"Word (ID: {self.word_no_recording.id}) missing 'user_recording_url' attribute.")
        self.assertIsNone(word_without_rec_in_context.user_recording_url)

        if hasattr(user_recording.recording, 'path'):
            # import os # Already imported at top
            if os.path.exists(user_recording.recording.path):
                os.remove(user_recording.recording.path)
        user_recording.delete()

    def test_save_user_settings_use_own_recordings(self):
        self.client.login(username=self.user.username, password='password123')

        # Test saving True
        response_true = self.client.post(
            reverse('save_user_settings'),
            json.dumps({
                'user_settings': {
                    'useOwnRecordings': True,
                    'repetitions': 1,
                    'pauseBetween': 1000,
                    'delayBeforeTranslation': 500,
                    'hide_translation': False,
                    'playbackSpeed': 1,
                    'lessonRepeatCount': 1
                }
            }),
            content_type='application/json'
        )
        self.assertEqual(response_true.status_code, 200)
        self.assertTrue(response_true.json()['success'])
        user_settings = UserSettings.objects.get(user=self.user)
        self.assertTrue(user_settings.use_own_recordings_if_available)

        # Test saving False
        response_false = self.client.post(
            reverse('save_user_settings'),
            json.dumps({
                'user_settings': {
                    'useOwnRecordings': False,
                    'repetitions': 1,
                    'pauseBetween': 1000,
                    'delayBeforeTranslation': 500,
                    'hide_translation': False,
                    'playbackSpeed': 1,
                    'lessonRepeatCount': 1
                }
            }),
            content_type='application/json'
        )
        self.assertEqual(response_false.status_code, 200)
        self.assertTrue(response_false.json()['success'])
        user_settings = UserSettings.objects.get(user=self.user) # Re-fetch
        self.assertFalse(user_settings.use_own_recordings_if_available)

    def test_learn_words_view_context_audio_urls(self):
        self.client.login(username=self.user.username, password='password123')

        # Scenario 1: User prefers own recordings, and a recording exists
        user_settings, _ = UserSettings.objects.update_or_create(
            user=self.user,
            defaults={'use_own_recordings_if_available': True}
        )

        audio_content = b'my own voice'
        audio_file = SimpleUploadedFile("my_audio.webm", audio_content, content_type="audio/webm")
        my_recording = WordRecording.objects.create(
            user=self.user,
            word=self.word,
            recording=audio_file
        )

        session = self.client.session
        session['selected_words'] = [self.word.id]
        session['is_random'] = False
        session['selected_categories'] = {}
        session['is_random_order'] = {}
        session.save()

        response = self.client.get(reverse('learn_words'))
        self.assertEqual(response.status_code, 200)

        result_words_context = response.context.get('words')
        self.assertIsNotNone(result_words_context)
        self.assertEqual(len(result_words_context), 1)

        word_data = result_words_context[0]
        self.assertEqual(word_data['id'], self.word.id)
        self.assertEqual(word_data['user_recording_url'], my_recording.recording.url)
        self.assertTrue(word_data['tts_en_url'])
        self.assertTrue(word_data['tts_ru_url'])

        if hasattr(my_recording.recording, 'path'):
            # import os # Already imported
            if os.path.exists(my_recording.recording.path):
                os.remove(my_recording.recording.path)
        my_recording.delete()

        # Scenario 2: User prefers own recordings, but NO recording exists for the word
        session.save()
        response_no_rec = self.client.get(reverse('learn_words'))
        self.assertEqual(response_no_rec.status_code, 200)
        word_data_no_rec = response_no_rec.context['words'][0]
        self.assertEqual(word_data_no_rec['id'], self.word.id)
        self.assertIsNone(word_data_no_rec['user_recording_url'])
        self.assertTrue(word_data_no_rec['tts_en_url'])
        self.assertTrue(word_data_no_rec['tts_ru_url'])

        # Scenario 3: User does NOT prefer own recordings
        user_settings.use_own_recordings_if_available = False
        user_settings.save()
        my_ignored_recording = WordRecording.objects.create(
            user=self.user, word=self.word, recording=SimpleUploadedFile("ignored.webm", b"ignored", "audio/webm")
        )
        session.save()
        response_pref_false = self.client.get(reverse('learn_words'))
        self.assertEqual(response_pref_false.status_code, 200)
        word_data_pref_false = response_pref_false.context['words'][0]
        self.assertEqual(word_data_pref_false['id'], self.word.id)
        self.assertIsNone(word_data_pref_false['user_recording_url'])
        self.assertTrue(word_data_pref_false['tts_en_url'])
        self.assertTrue(word_data_pref_false['tts_ru_url'])

        if hasattr(my_ignored_recording.recording, 'path'):
            # import os # Already imported
            if os.path.exists(my_ignored_recording.recording.path):
                os.remove(my_ignored_recording.recording.path)
        my_ignored_recording.delete()

    def test_save_user_settings_full_voice_preferences(self):
        # Create another user to be the 'preferred_other_user'
        other_user_for_pref = User.objects.create_user(username='otherprefrec', password='password123')
        self.client.login(username=self.user.username, password='password123')

        # Scenario 1: Preferring another user
        payload_other_user = {
            'user_settings': {
                'voicePreferenceType': 'other_user',
                'preferredOtherUserId': other_user_for_pref.id,
                'repetitions': 1, 'pauseBetween': 1000, 'delayBeforeTranslation': 500,
                'hide_translation': False, 'playbackSpeed': 1, 'lessonRepeatCount': 1
            }
        }
        response = self.client.post(reverse('save_user_settings'), json.dumps(payload_other_user), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(settings.voice_preference_type, 'other_user')
        self.assertEqual(settings.preferred_other_user, other_user_for_pref)
        self.assertFalse(settings.use_own_recordings_if_available)

        # Scenario 2: Preferring own recordings
        payload_own = {
            'user_settings': {
                'voicePreferenceType': 'own',
                'preferredOtherUserId': None,
                'repetitions': 1, 'pauseBetween': 1000, 'delayBeforeTranslation': 500,
                'hide_translation': False, 'playbackSpeed': 1, 'lessonRepeatCount': 1
            }
        }
        response_own = self.client.post(reverse('save_user_settings'), json.dumps(payload_own), content_type='application/json')
        self.assertEqual(response_own.status_code, 200)
        settings.refresh_from_db()
        self.assertEqual(settings.voice_preference_type, 'own')
        self.assertIsNone(settings.preferred_other_user)
        self.assertTrue(settings.use_own_recordings_if_available)

        # Scenario 3: Preferring TTS
        payload_tts = {
            'user_settings': {
                'voicePreferenceType': 'tts',
                'preferredOtherUserId': other_user_for_pref.id,
                'repetitions': 1, 'pauseBetween': 1000, 'delayBeforeTranslation': 500,
                'hide_translation': False, 'playbackSpeed': 1, 'lessonRepeatCount': 1
            }
        }
        response_tts = self.client.post(reverse('save_user_settings'), json.dumps(payload_tts), content_type='application/json')
        self.assertEqual(response_tts.status_code, 200)
        settings.refresh_from_db()
        self.assertEqual(settings.voice_preference_type, 'tts')
        self.assertIsNone(settings.preferred_other_user)
        self.assertFalse(settings.use_own_recordings_if_available)

        other_user_for_pref.delete()

    def test_learn_words_context_community_voice_selection(self):
        self.client.login(username=self.user.username, password='password123')

        own_rec_content = b'my voice for hello'
        own_rec_file = SimpleUploadedFile("own_hello.webm", own_rec_content, "audio/webm")
        own_recording = WordRecording.objects.create(user=self.user, word=self.word, recording=own_rec_file)

        other_rec_content_hello = b'other voice for hello'
        other_rec_file_hello = SimpleUploadedFile("other_hello.webm", other_rec_content_hello, "audio/webm")
        other_user_recording_hello = WordRecording.objects.create(user=self.other_recordist, word=self.word, recording=other_rec_file_hello)

        other_rec_content_bye = b'other voice for bye'
        other_rec_file_bye = SimpleUploadedFile("other_bye.webm", other_rec_content_bye, "audio/webm")
        other_user_recording_bye = WordRecording.objects.create(user=self.other_recordist, word=self.word2, recording=other_rec_file_bye)

        session = self.client.session
        session['selected_words'] = [self.word.id, self.word2.id]
        session['is_random'] = False
        session['selected_categories'] = {}
        session['is_random_order'] = {}
        session.save()

        # Scenario 1: Prefer 'other_user' (self.other_recordist)
        settings, _ = UserSettings.objects.update_or_create(
            user=self.user,
            defaults={
                'voice_preference_type': 'other_user',
                'preferred_other_user': self.other_recordist
            }
        )
        response = self.client.get(reverse('learn_words'))
        self.assertEqual(response.status_code, 200)

        self.assertIn('recordist_users', response.context)
        recordist_ids_in_context = [u['id'] for u in response.context['recordist_users']]
        self.assertIn(self.other_recordist.id, recordist_ids_in_context)
        self.assertNotIn(self.user.id, recordist_ids_in_context)

        words_ctx = {w['id']: w for w in response.context['words']}
        self.assertEqual(words_ctx[self.word.id]['active_recording_url'], other_user_recording_hello.recording.url)
        self.assertEqual(words_ctx[self.word2.id]['active_recording_url'], other_user_recording_bye.recording.url)

        # Scenario 2: Prefer 'own'
        settings.voice_preference_type = 'own'
        settings.preferred_other_user = None
        settings.save()
        response_own = self.client.get(reverse('learn_words'))
        words_ctx_own = {w['id']: w for w in response_own.context['words']}
        self.assertEqual(words_ctx_own[self.word.id]['active_recording_url'], own_recording.recording.url)
        self.assertIsNone(words_ctx_own[self.word2.id]['active_recording_url'])

        # Scenario 3: Prefer 'tts'
        settings.voice_preference_type = 'tts'
        settings.save()
        response_tts = self.client.get(reverse('learn_words'))
        words_ctx_tts = {w['id']: w for w in response_tts.context['words']}
        self.assertIsNone(words_ctx_tts[self.word.id]['active_recording_url'])
        self.assertIsNone(words_ctx_tts[self.word2.id]['active_recording_url'])

        # Scenario 4: Prefer 'other_user', but that user has no recording for self.word2
        # For this, delete other_user_recording_bye and re-test scenario 1 for word2
        if hasattr(other_user_recording_bye.recording, 'path') and os.path.exists(other_user_recording_bye.recording.path):
             os.remove(other_user_recording_bye.recording.path)
        other_user_recording_bye.delete()

        settings.voice_preference_type = 'other_user'
        settings.preferred_other_user = self.other_recordist # Ensure it's still set
        settings.save()
        response_other_no_rec_for_word2 = self.client.get(reverse('learn_words'))
        words_ctx_other_no_rec_for_word2 = {w['id']: w for w in response_other_no_rec_for_word2.context['words']}
        self.assertEqual(words_ctx_other_no_rec_for_word2[self.word.id]['active_recording_url'], other_user_recording_hello.recording.url)
        self.assertIsNone(words_ctx_other_no_rec_for_word2[self.word2.id]['active_recording_url'])

        if hasattr(own_recording.recording, 'path') and os.path.exists(own_recording.recording.path): os.remove(own_recording.recording.path)
        own_recording.delete()
        if hasattr(other_user_recording_hello.recording, 'path') and os.path.exists(other_user_recording_hello.recording.path): os.remove(other_user_recording_hello.recording.path)
        other_user_recording_hello.delete()
