from datetime import datetime, timedelta
import unittest
from Event import Event
from Backend import Backend
from User import User


# Assuming the `User` class and `Backend` class are defined elsewhere in your code.
# from your_module import User, Backend

# class TestEvent(unittest.TestCase):
#
#     def setUp(self):
#         self.username = "john"
#         self.password = "John12345"
#         self.organizer = User(self.username, self.password)
#         self.participant = User("janedoe", 'Janedoe123')
#         self.title = "Meeting"
#         self.description = "Weekly meeting"
#         self.start_time = datetime(2023, 1, 1, 10, 0)
#         self.end_time = datetime(2023, 1, 1, 11, 0)
#         self.event = Event(title=self.title, start_time=self.start_time, end_time=self.end_time,
#                            description=self.description, organizer=self.organizer)
#
#     def test_event_creation(self):
#         self.assertEqual(self.event.title, self.title)
#         self.assertEqual(self.event.description, self.description)
#         self.assertEqual(self.event.start_time, self.start_time)
#         self.assertEqual(self.event.end_time, self.end_time)
#         self.assertEqual(self.event.organizer, self.organizer)
#
#     # def test_unique_id(self):
#     #     unique_id = self.event.get_unique_id()
#     #     expected_id = f"{self.title}-{self.organizer}-{self.start_time.isoformat()}"
#     #     self.assertEqual(unique_id, expected_id)
#
#
#     def test_add_participant(self):
#         with self.assertRaises(TypeError):
#             self.event.add_participant(self.organizer)  # организатор сразу должен быть участником
#         initial_count = len(self.event.participants)
#         self.event.add_participant(self.participant)
#         self.assertEqual(len(self.event.participants), initial_count + 1)
#         self.assertIn(self.participant, self.event.participants)
#
#     def test_remove_participant(self):
#         self.event.add_participant(self.participant)
#         self.assertIn(self.participant, self.event.participants)
#         self.event.remove_participant(self.participant)
#         self.assertNotIn(self.participant, self.event.participants)
#
#     def test_update_event(self):
#         new_description = "Updated description"
#         new_end_time = datetime(2023, 1, 1, 12, 0)
#         self.event.update_event(description=new_description, end_time=new_end_time)
#         self.assertEqual(self.event.description, new_description)
#         self.assertEqual(self.event.end_time, new_end_time)
#
#     def test_leave_event(self):
#         self.event.add_participant(self.participant)
#         self.assertIn(self.participant, self.event.participants)
#         self.event.leave_event(self.participant)
#         self.assertNotIn(self.participant, self.event.participants)
#
#     def test_to_dict(self):
#         event_dict = self.event.to_dict()
#         self.assertEqual(event_dict['title'], self.title)
#         self.assertEqual(event_dict['description'], self.description)
#         self.assertEqual(event_dict['start_time'], self.start_time.isoformat())
#         self.assertEqual(event_dict['end_time'], self.end_time.isoformat())
#         self.assertEqual(event_dict['organizer'], self.username)
#
#     def test_generate_periodic_event(self):
#         new_start_time = datetime(2023, 1, 8, 10, 0)
#         new_end_time = datetime(2023, 1, 8, 11, 0)
#         periodic_event = self.event.generate_periodic_event(new_start_time, new_end_time)
#         self.assertEqual(periodic_event.title, self.title)
#         self.assertEqual(periodic_event.description, self.description)
#         self.assertEqual(periodic_event.start_time, new_start_time)
#         self.assertEqual(periodic_event.end_time, new_end_time)
#
# # To run the test suite
# if __name__ == '__main__':
#     unittest.main()

import unittest
from datetime import datetime
from Event import Event
from User import User# Replace with actual import paths

class TestEvent(unittest.TestCase):

    def setUp(self):
        # Setup test data/conditions
        self.test_user = User(username='test_user', password='Testpassword123')
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=2)
        self.test_event = Event(
            title="Test Event",
            start_time=self.start_time,
            end_time=self.end_time,
            description="Test Description",
            participants=[self.test_user],
            organizer=self.test_user
        )
    def tearDown(self):
        # This function will run after each test to clean up any resources used in the test
        User._usernames.clear()
        Event.events_map.clear()
        self.test_event.participants.clear()
        Event.count = 1
    def test_init_creates_unique_id(self):
        # Test __init__ creates unique event IDs
        first_event = Event("First Event")
        second_event = Event("Second Event")
        self.assertNotEqual(first_event._event_id, second_event._event_id)

    def test_add_participant(self):
        # Test add_participant method
        new_participant = User(username='new_user', password='Newuser123')
        self.test_event.add_participant(new_participant)
        self.assertIn(new_participant, self.test_event.participants)

    def test_add_existing_participant_raises_error(self):
        # Test add_participant raises error if participant already exists
        with self.assertRaises(TypeError):
            self.test_event.add_participant(self.test_user)

    def test_remove_participant(self):
        # Test remove_participant method
        self.test_event.remove_participant(self.test_user)
        self.assertNotIn(self.test_user, self.test_event.participants)

    def test_update_event(self):
        # Test the update_event method of the Event class
        # Assume User is a properly defined class with necessary attributes
        additional_participant = User(username='test_user', password='Testuser123')
        self.event.update_event(title="Updated Title", participants=[additional_participant])
        self.assertEqual(self.event.title, "Updated Title")
        self.assertIn(additional_participant, self.event.participants)

    def test_create_or_get_event(self):
        # Test the create_or_get_event classmethod of the Event class

        backend_stub = type('BackendStub', (object,), {"users": {"new_user": self.test_user}})
        data = {
            'event_id': 1,
            'title': 'Get Event Test',
            'start_time': '2023-01-01 14:00',
            'end_time': '2023-01-01 15:00',
            'participants': ['new_user'],
            'organizer': 'new_user'
        }
        event = Event.create_or_get_event(data, backend_stub())
        self.assertIsInstance(event, Event)
        self.assertEqual(event.start_time, datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M'))

    def test_formate_date(self):
        # Test the static method formate_date of the Event class

        date_text = "01.01.2023 14:00"
        formatted_date = Event.formate_date(date_text)
        self.assertEqual(formatted_date, datetime(2023, 1, 1, 14, 0))

    def test_leave_event(self):
        # Test the leave_event method of the Event class

        self.test_event.add_participant(self.test_user)
        self.assertIn(self.test_user, self.test_event.participants)
        self.test_event.leave_event(self.test_user)
        self.assertNotIn(self.test_user, self.test_event.participants)


    # Additional tests should be written for other methods, such as:
    # - test_update_event for validating the update_event method
    # - test_create_or_get_event for validating the classmethod create_or_get_event
    # - test_formate_date for checking static date formatting method
    # - test_leave_event
    # - test_to_dict to validate the dictionary representation of the Event
    # - test_generate_periodic_event to validate event periodic generation
    # - test_get_timing
    # - test_delete_event
    # ...and any other methods

if __name__ == '__main__':
    unittest.main()