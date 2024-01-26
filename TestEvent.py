import unittest
from datetime import datetime
from Event import Event
from Python_course_calendar.Backend import Backend
from User import User# Replace with actual import paths
from copy import deepcopy

class TestEvent(unittest.TestCase):
    def setUp(self):
        self.username = "john"
        self.password = "John12345"
        self.organizer = User(self.username, self.password)
        self.participant = User("janedoe", 'Janedoe123')
        self.title = "Meeting"
        self.description = "Weekly meeting"
        self.start_time = datetime(2023, 1, 1, 10, 0)
        self.end_time = datetime(2023, 1, 1, 11, 0)
        self.event = Event(title=self.title, start_time=self.start_time, end_time=self.end_time,
                               description=self.description, organizer=self.organizer)


    def tearDown(self):
        # This function will run after each test to clean up any resources used in the test
        User._usernames.clear()
        Event.events_map.clear()
        self.event.participants.clear()
        Event.count = 1
        User._users_by_username.clear()

    def test_event_creation(self):
        self.assertEqual(self.event.title, self.title)
        self.assertEqual(self.event.description, self.description)
        self.assertEqual(self.event.start_time, self.start_time)
        self.assertEqual(self.event.end_time, self.end_time)
        self.assertEqual(self.event.organizer, self.organizer)


    def test_add_participant(self):
        with self.assertRaises(TypeError):
            self.event.add_participant(self.organizer)  # организатор сразу должен быть участником
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



    def test_init_creates_unique_id(self):
        # Test __init__ creates unique event IDs
        first_event = Event("First Event")
        second_event = Event("Second Event")
        self.assertNotEqual(first_event._event_id, second_event._event_id)


    def test_formate_date(self):
        # Test the static method formate_date of the Event class

        date_text = "01.01.2023 14:00"
        formatted_date = Event.formate_date(date_text)
        self.assertEqual(formatted_date, datetime(2023, 1, 1, 14, 0))


    def test_create_or_get_event_classmethod(self):
        # Test the create_or_get_event class method

        # Mock data and backend for testing
        mock_data = {
                "event_id": "1",
                "title": "breakfast",
                "start_time": "1997-12-12T12:20:00",
                "end_time": "1997-12-12T12:20:00",
                "description": "discussion",
                "recurrence": "once",
                "participants": [
                    "john", "janedoe"
                ],
                "organizer": "john"
            }
        mock_data1 = deepcopy(mock_data)
        event1 = Event.create_or_get_event(mock_data)
        event2 = Event.create_or_get_event(mock_data1)


        # Assert that both calls return the same event
        self.assertEqual(event1, event2)
        self.assertTrue(isinstance(event1.organizer, User))
        self.assertTrue(all(isinstance(participant, User) for participant in event1.participants))

    def test_get_timing(self):
        # Test the get_timing method
        timing = self.event.get_timing()
        expected_timing = self.event.end_time - self.event.start_time
        self.assertEqual(timing, expected_timing)

    def test_delete_event(self):
        # Test the delete_event method
        Event.delete_event(self.event)
        self.assertNotIn(self.event.event_id, Event.events_map)  # Event should be deleted from events_map

if __name__ == '__main__':
    unittest.main()