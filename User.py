"""
Пользователь - имеет логин и пароль, а так же календарь.
у пользователя есть итендифекатор начинающийся с @
"""
import hashlib

class User:
    """
    A User class representing a user with a unique identifier, login, and password.
    """
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._id = f"@{username}"
        self._notifications = []

    def __repr__(self):
        return self.username

    def __str__(self):
        return self.username

    def get_password(self):
        return self._password

    def notify(self, message):
        """Добавить новое уведомление для пользователя."""
        self.notifications.append(message)

    def get_notifications(self):
        """Получить уведомления пользователя, очистив очередь уведомлений."""
        notifications = self.notifications.copy()
        self.notifications.clear()
        return notifications
    @property
    def username(self):
        return self._username

    @property
    def id(self):
        return self._id

    @property
    def notifications(self):
        return self._notifications

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id
        return False
    def __hash__(self):
        return hash(self.id)