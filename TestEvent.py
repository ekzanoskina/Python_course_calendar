from datetime import datetime, timedelta
import unittest
from Event import Event
from Backend import Backend
from User import User


# Assuming the `User` class and `Backend` class are defined elsewhere in your code.
# from your_module import User, Backend

class TestEvent(unittest.TestCase):

    def setUp(self):
        self.username = "johndoe"
        self.password = "Johndoe123"
        self.organizer = User(self.username, self.password)
        self.participant = User("janedoe", 'Janedoe123')
        self.title = "Meeting"
        self.description = "Weekly meeting"
        self.start_time = datetime(2023, 1, 1, 10, 0)
        self.end_time = datetime(2023, 1, 1, 11, 0)
        self.event = Event(title=self.title, start_time=self.start_time, end_time=self.end_time,
                           description=self.description, organizer=self.organizer)

    def test_event_creation(self):
        self.assertEqual(self.event.title, self.title)
        self.assertEqual(self.event.description, self.description)
        self.assertEqual(self.event.start_time, self.start_time)
        self.assertEqual(self.event.end_time, self.end_time)
        self.assertEqual(self.event.organizer, self.organizer)

    def test_unique_id(self):
        unique_id = self.event.get_unique_id()
        expected_id = f"{self.title}-{self.organizer}-{self.start_time.isoformat()}"
        self.assertEqual(unique_id, expected_id)

    def test_add_participant(self):
        with self.assertRaises(TypeError):
            self.event.add_participant(self.organizer)  # Organizer should already be a participant
        initial_count = len(self.event.participants)
        self.event.add_participant(self.participant)
        self.assertEqual(len(self.event.participants), initial_count + 1)
        self.assertIn(self.participant, self.event.participants)

    def test_remove_participant(self):
        self.event.add_participant(self.participant)
        self.assertIn(self.participant, self.event.participants)
        self.event.remove_participant(self.participant)
        self.assertNotIn(self.participant, self.event.participants)

    def test_update_event(self):
        new_description = "Updated description"
        new_end_time = datetime(2023, 1, 1, 12, 0)
        self.event.update_event(description=new_description, end_time=new_end_time)
        self.assertEqual(self.event.description, new_description)
        self.assertEqual(self.event.end_time, new_end_time)

    def test_leave_event(self):
        self.event.add_participant(self.participant)
        self.assertIn(self.participant, self.event.participants)
        self.event.leave_event(self.participant)
        self.assertNotIn(self.participant, self.event.participants)

    def test_to_dict(self):
        event_dict = self.event.to_dict()
        self.assertEqual(event_dict['title'], self.title)
        self.assertEqual(event_dict['description'], self.description)
        self.assertEqual(event_dict['start_time'], self.start_time.isoformat())
        self.assertEqual(event_dict['end_time'], self.end_time.isoformat())
        self.assertEqual(event_dict['organizer'], self.username)

    def test_generate_periodic_event(self):
        new_start_time = datetime(2023, 1, 8, 10, 0)
        new_end_time = datetime(2023, 1, 8, 11, 0)
        periodic_event = self.event.generate_periodic_event(new_start_time, new_end_time)
        self.assertEqual(periodic_event.title, self.title)
        self.assertEqual(periodic_event.description, self.description)
        self.assertEqual(periodic_event.start_time, new_start_time)
        self.assertEqual(periodic_event.end_time, new_end_time)

# To run the test suite
if __name__ == '__main__':
    unittest.main()