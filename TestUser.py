import unittest

from Python_course_calendar.User import User


class TestUser(unittest.TestCase):
    def setUp(self):
        self.username = "john_doe"
        self.password = "Johndoe12345"
        self.user = User(self.username, self.password)

    def test_init(self):
        self.assertEqual(self.user.username, self.username)
        self.assertEqual(self.user.get_password(), self.password)
        self.assertEqual(self.user.id, f"@{self.username}")

    def test_repr(self):
        self.assertEqual(repr(self.user), self.username)

    def test_str(self):
        self.assertEqual(str(self.user), self.username)

    def test_notify(self):
        message = "You have a new notification!"
        self.user.notify(message)
        self.assertIn(message, self.user.notifications)

    def test_get_notifications(self):
        message = "You have a new notification!"
        self.user.notify(message)
        notifications = self.user.get_notifications()
        self.assertIn(message, notifications)
        self.assertListEqual(self.user.notifications, [])

    def test_eq(self):
        another_user = User(self.username, "another_secret")
        different_user = User("jane_doe", "diff_secret")
        self.assertEqual(self.user, another_user)
        self.assertNotEqual(self.user, different_user)

    def test_hash(self):
        user_set = {self.user}
        another_user = User(self.username, "another_secret")
        different_user = User("jane_doe", "diff_secret")
        user_set.add(another_user)  # This should not add a new element as it is considered equal to self.user
        user_set.add(different_user)
        self.assertEqual(len(user_set), 2)

if __name__ == '__main__':
    unittest.main()