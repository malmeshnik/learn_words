import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import Section, Chapter, Room, Word, UserSelection, UserSettings

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
