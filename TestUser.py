import unittest
import uuid  # Make sure to import this as it's used in your class
from User import User  # Update this to the path where your User class is defined


class TestUser(unittest.TestCase):

    def setUp(self):
        # This will be called before every test function
        User._usernames.clear()

    def test_init(self):
        username = "user1"
        password = "password123"
        user = User(username, password)
        self.assertEqual(user.username, username)
        self.assertEqual(user.get_password(), password)
        self.assertIsInstance(user.user_id, str)
        self.assertRegex(user.user_id, r"^[0-9a-f-]+$")  # Check if it looks like a valid UUID
        self.assertIn(username, User._usernames)

    def test_username_uniqueness(self):
        username = "user2"
        User(username, "password123")
        with self.assertRaises(ValueError):
            User(username, "another_password")

    def test_eq(self):
        user1 = User("user3", "password123")
        user2 = User("user4", "password321")
        self.assertNotEqual(user1, user2)


    def test_hash(self):
        user = User("user5", "password123")
        self.assertEqual(hash(user), hash(user.user_id))


    def test_class_method_is_username_taken(self):
        username = "user7"
        self.assertFalse(User.is_username_taken(username))
        User(username, "password123")
        self.assertTrue(User.is_username_taken(username))

    def test_json(self):
        # This test is not implemented as the method `to_json` is not defined
        # You would put here the test for the to_json method
        pass


if __name__ == '__main__':
    unittest.main()