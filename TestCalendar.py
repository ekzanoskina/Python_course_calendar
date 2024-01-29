import unittest
from datetime import timedelta, datetime

from Calendar import RepetitionError, Calendar
from Event import Event
from User import User


class TestCalendar(unittest.TestCase):
    def setUp(self):
        self.test_user = User('test_username', "test123456789")
        self.calendar = Calendar(owner=self.test_user)
        self.start_time = datetime.now()
        self.recurrence = 'каждый день'
        self.end_time = self.start_time + timedelta(hours=2)
        self.event = Event(title="Meeting", start_time=self.start_time, end_time=self.end_time, description="Test Meeting", organizer=self.test_user, recurrence=self.recurrence)
    def tearDown(self):
        # This function will run after each test to clean up any resources used in the test
        User._usernames.clear()
        Event.events_map.clear()
        self.event.participants.clear()
        Event.count = 1

    def test_add_event(self):
        self.calendar.add_event(self.event)
        self.assertIn(self.event, self.calendar.events)

    def test_remove_event(self):
        self.calendar.add_event(self.event)
        self.calendar.remove_event(self.event)
        self.assertNotIn(self.event, self.calendar.events)

    def test_get_coming_events_contains_event(self):
        # Добавляем событие в календарь
        self.calendar.add_event(self.event)

        # Получаем список предстоящих событий
        coming_events = self.calendar.get_coming_events()

        # Проверяем, что наше событие в списке
        self.assertIn(self.event.title, [event.title for events in coming_events.values() for event in events])

    def test_get_events_in_range(self):
        self.calendar.add_event(self.event)
        events_in_range = self.calendar.get_events_in_range(self.start_time, self.start_time + timedelta(days=1))
        self.assertIn(self.event.title, [event.title for events in events_in_range.values() for event in events])

    def test_add_unprocessed_event(self):
        self.calendar.add_unprocessed_events(self.event)
        self.assertIn(self.event, self.calendar.unprocessed_events)

    def test_add_existing_unprocessed_event(self):
        self.calendar.add_unprocessed_events(self.event)
        with self.assertRaises(RepetitionError):
            self.calendar.add_unprocessed_events(self.event)

    def test_mark_event_as_processed(self):
        self.calendar.add_unprocessed_events(self.event)
        self.calendar.mark_event_as_processed(self.event)
        self.assertNotIn(self.event, self.calendar.unprocessed_events)

    def test_event_type_error(self):
        with self.assertRaises(TypeError):
            self.calendar.add_event("not_an_event")

if __name__ == '__main__':
    unittest.main()