import unittest
import uuid
import hashlib
import re
from datetime import datetime, timedelta
from unittest.mock import patch

from Backend import Backend
from Event import Event
from Python_course_calendar.Calendar import Calendar
from Python_course_calendar.User import User


# Assuming necessary imports and exception classes are defined here
# from your_module import User, Calendar, Event, AuthenticationError

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.backend = Backend()
        self.organizer = User("johndoe", "Johndoe123")
        self.participant = User("janedoe", 'Janedoe123')
        self.title = "Meeting"
        self.description = "Weekly meeting"
        self.start_time = datetime(2023, 1, 1, 10, 0)
        self.end_time = datetime(2023, 1, 1, 11, 0)
        self.event = Event(title=self.title, start_time=self.start_time, end_time=self.end_time,
                           description=self.description, organizer=self.organizer)
    def test_singleton(self):
        """Test the Backend class is a singleton."""
        instance1 = Backend()
        instance2 = Backend()
        self.assertEqual(id(instance1), id(instance2))

    def test_create_user(self):
        """Test user creation."""
        user = self.backend.create_user("testuser", "password123")
        self.assertIn("testuser", self.backend.users)
        self.assertIsNotNone(user)

    def test_check_username_exists(self):
        """Test username checking."""
        self.backend.create_user("testuser", "password123")
        self.assertTrue(self.backend.check_username_exists("testuser"))
        self.assertFalse(self.backend.check_username_exists("nonexistentuser"))

    def test_hash_password(self):
        """Test password hashing."""
        password = "password123"
        hashed = self.backend.hash_password(password)
        self.assertNotEqual(password, hashed)

    def test_check_password(self):
        """Test password checking."""
        user = self.backend.create_user("testuser", "password123")
        self.assertTrue(self.backend.check_password(user.get_password(), "password123"))

    def test_login(self):
        """Test user login."""
        self.backend.create_user("testuser", "password123")
        self.assertIsNotNone(self.backend.login("testuser", "password123"))

    def test_validate_by_regexp(self):
        """Test password format validation"""
        self.backend.validate_by_regexp("Password123")
        with self.assertRaises(ValueError):
            self.backend.validate_by_regexp("pass123")

    def test_validate_date_format(self):
        """Test the date format validation."""
        format_example = "01.01.2020 12:00"
        self.assertIsNotNone(self.backend.validate_date_format(format_example))
        with self.assertRaises(ValueError):
            self.backend.validate_date_format("NotADate", format='%d.%m.%Y %H:%M')

    def test_compare_dates(self):
        """Test date comparison."""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=1)
        self.assertTrue(self.backend.compare_dates(start_date, end_date))
        with self.assertRaises(ValueError):
            self.backend.compare_dates(end_date, start_date)

    def test_validate_recurrence(self):
        """Test event recurrence validation."""
        self.assertEqual(self.backend.validate_recurrence('0'), Event.formate_recurrence('0'))
        with self.assertRaises(ValueError):
            self.backend.validate_recurrence('invalid_value')

    @patch('builtins.print')
    def test_invite_participants_permission_error(self, mock_print):
        # Assuming we have these setup in the test class
        backend = Backend()
        organizer = User("organizer", "password")
        non_organizer = User("non_organizer", "password")
        participant = User("participant", "password")
        event = Event("Event", datetime.now(), datetime.now(), "Description", organizer)

        with self.assertRaises(PermissionError):
            backend.invite_participants(non_organizer, event, [participant])

    def test_invite_participants_success(self):
        # Assuming we have these setup in the test class
        backend = Backend()
        organizer = User("organizer", "password")
        participant = User("participant", "password")
        event = Event("Event", datetime.now(), datetime.now(), "Description", organizer)
        # calendar = Calendar(organizer)
        # calendar.add_unprocessed_events =Calendar(organizer)

        backend.users[participant.username] = participant
        backend.calendars[participant.username] = calendar

        try:
            backend.invite_participants(organizer, event, [participant])
            calendar.add_unprocessed_events.assert_called_with(event)
        except Exception as e:
            self.fail(f"invite_participants unexpectedly raised an exception {e}")

        def test_validate_by_regexp_valid(self):
            """Тест валидного пароля"""
            self.assertEqual(Backend.validate_by_regexp('Valid123'), 'Valid123')

        def test_validate_by_regexp_short(self):
            """Тест короткого пароля"""
            with self.assertRaises(ValueError):
                Backend.validate_by_regexp('V1d')

        def test_validate_by_regexp_no_number(self):
            """Тест пароля без цифр"""
            with self.assertRaises(ValueError):
                Backend.validate_by_regexp('Invalid')

        def test_validate_by_regexp_no_uppercase(self):
            """Тест пароля без букв в верхнем регистре"""
            with self.assertRaises(ValueError):
                Backend.validate_by_regexp('invalid123')

        def test_validate_by_regexp_no_lowercase(self):
            """Тест пароля без букв в нижнем регистре"""
            with self.assertRaises(ValueError):
                Backend.validate_by_regexp('INVALID123')


if __name__ == "__main__":
    unittest.main()