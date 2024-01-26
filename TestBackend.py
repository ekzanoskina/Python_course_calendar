import os
import unittest
import uuid
import hashlib
import re
from datetime import datetime, timedelta
from unittest.mock import patch

from Backend import Backend, PermissionError, AuthenticationError
from Event import Event
from Calendar import Calendar
from User import User


# Assuming necessary imports and exception classes are defined here
# from your_module import User, Calendar, Event, AuthenticationError

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.backend = Backend()
        self.organizer = User("johndoe", "Johndoe123")
        self.backend.logged_in_user = self.organizer
        self.backend.current_calendar = self.backend.get_calendar(self.organizer)
        self.participant = User("janedoe", 'Janedoe123')
        self.title = "Meeting"
        self.description = "Weekly meeting"
        self.recurrence = 'weekly'
        self.start_time = datetime(2023, 1, 1, 10, 0)
        self.end_time = datetime(2023, 1, 1, 11, 0)
        self.event = Event(title=self.title, start_time=self.start_time, end_time=self.end_time,
                           description=self.description, recurrence=self.recurrence, organizer=self.organizer)

    def tearDown(self):
        # This function will run after each test to clean up any resources used in the test
        User._usernames.clear()
        User._users_by_username.clear()
        Event.events_map.clear()
        Event.count = 1
        # self.event.participants.clear()
        self.backend = None

    def test_singleton(self):
        """Test the Backend class is a singleton."""
        instance1 = Backend()
        instance2 = Backend()
        self.assertEqual(id(instance1), id(instance2))

    def test_create_user(self):
        """Test user creation."""
        user = self.backend.create_user("test_user", "Password123")
        self.assertIn("test_user", self.backend.users)
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
        user = self.backend.create_user("test_user1", "Password123")
        self.assertTrue(self.backend.check_password(user.get_password(), "Password123"))

    def test_login(self):
        """Test user login."""
        self.backend.create_user("test_user2", "Password123")
        self.assertIsNotNone(self.backend.login("test_user2", "Password123"))

    def test_validate_pass_by_regexp(self):
        """Test password format validation"""
        self.backend.validate_pass_by_regexp("Password123")
        with self.assertRaises(ValueError):
            self.backend.validate_pass_by_regexp("pass123")

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
        self.assertEqual(self.backend.validate_recurrence('0', '0:'), Event.formate_recurrence('0'))
        with self.assertRaises(ValueError):
            self.backend.validate_recurrence('invalid_value', '0:')

    def test_invite_participants_permission_error(self):
        # Assuming we have these setup in the test class
        organizer = User("organizer", "Password123")
        non_organizer = User("non_organizer", "Password123")
        participant = User("participant", "Password123")
        event = Event("Event", datetime.now(), datetime.now(), "Description", organizer)
        self.backend.logged_in_user = non_organizer
        with self.assertRaises(PermissionError):
            self.backend.invite_participants(event, [participant])

    def test_validate_by_regexp_valid(self):
        """Тест валидного пароля"""
        self.assertEqual(Backend.validate_pass_by_regexp('Valid123'), 'Valid123')

    def test_validate_by_regexp_short(self):
        """Тест короткого пароля"""
        with self.assertRaises(ValueError):
            Backend.validate_pass_by_regexp('V1d')

    def test_validate_by_regexp_no_number(self):
        """Тест пароля без цифр"""
        with self.assertRaises(ValueError):
            Backend.validate_pass_by_regexp('Invalid')

    def test_validate_by_regexp_no_uppercase(self):
        """Тест пароля без букв в верхнем регистре"""
        with self.assertRaises(ValueError):
            Backend.validate_pass_by_regexp('invalid123')

    def test_validate_by_regexp_no_lowercase(self):
        """Тест пароля без букв в нижнем регистре"""
        with self.assertRaises(ValueError):
            Backend.validate_pass_by_regexp('INVALID123')

    # def test_load_user_data(self):
    #     self.backend.load_user_data()
    #     self.assertIn(self.organizer.username, self.backend.users)
    #
    # def test_save_user_data(self):
    #     self.backend.save_user_data()
    #     self.assertTrue(os.path.exists('users.csv'))
    #
    # def test_load_calendar_data(self):
    #     self.backend.load_calendar_data()
    #     self.assertTrue(self.backend.calendars)
    #
    # def test_save_calendar_data(self):
    #     self.backend.save_calendar_data()
    #     self.assertTrue(os.path.exists('calendars.json'))

    def test_manage_unprocessed_evens(self):
        self.backend.logged_in_user = self.participant
        self.backend.current_calendar = self.backend.get_calendar(self.participant)
        self.backend.current_calendar.add_unprocessed_events(self.event)
        self.assertTrue(self.backend.manage_unprocessed_evens())

    def test_accept_invitation(self):
        self.backend.logged_in_user = self.participant
        self.backend.current_calendar = self.backend.get_calendar(self.participant)
        self.backend.current_calendar.add_unprocessed_events(self.event)
        self.backend.accept_invitation(self.event)
        self.assertIn(self.event, self.backend.current_calendar.events)
        self.backend.current_calendar.remove_event(self.event)

    def test_decline_invitation(self):
        self.backend.logged_in_user = self.participant
        self.backend.current_calendar = self.backend.get_calendar(self.participant)
        self.backend.current_calendar.add_unprocessed_events(self.event)
        self.backend.decline_invitation(self.event)
        self.assertNotIn(self.event, self.backend.current_calendar.get_unprocessed_events())

    def test_validate_number_input(self):
        self.assertEqual(self.backend.validate_number_input('1', '1: Enter number'), '1')

    def test_validate_str_input(self):
        self.assertEqual(self.backend.validate_str_input('option1', 'Choose (option1/option2)'), 'option1')

    def test_create_event(self):
        title = 'Test Event'
        start_time = datetime(2022, 1, 1, 12, 0)
        end_time = datetime(2022, 1, 1, 13, 0)
        description = 'Test description'
        recurrence = 'daily'
        self.backend.logged_in_user = self.organizer
        self.backend.current_calendar = self.backend.get_calendar(self.organizer)
        event = self.backend.create_event(title, start_time, end_time, description, recurrence)
        self.assertIn(event, self.backend.current_calendar.events)

    def test_get_events_in_range(self):
        self.backend.current_calendar.add_event(self.event)
        start_date = datetime(2023, 1, 1, 10, 0)
        end_date = datetime(2023, 1, 1, 11, 0)
        events = self.backend.get_events_in_range(start_date, end_date)
        self.assertTrue(events)

    def test_leave_event(self):
        self.event.add_participant(self.participant)
        self.backend.logged_in_user = self.participant
        self.backend.current_calendar = self.backend.get_calendar(self.participant)
        self.backend.leave_event(self.event)
        self.assertNotIn(self.event, self.backend.current_calendar.events)

    #
    def test_delete_event(self):
        self.backend.delete_event(self.event)
        self.assertNotIn(self.event, self.backend.current_calendar.events)


if __name__ == "__main__":
    unittest.main()
