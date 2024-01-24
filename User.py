"""
Пользователь - имеет логин и пароль, а так же календарь.
у пользователя есть итендифекатор начинающийся с @
"""
import hashlib

import uuid

class User:
    _usernames = set()  # множество на уровне класса для контроля уникальности username

    def __init__(self, username, password):
        if username in User._usernames:
            raise ValueError(f"Username {username} is already taken.")
        self._username = username
        self._password = password
        self._user_id = str(uuid.uuid4())  # генерирует уникальное id
        User._usernames.add(username)
        self._notifications = []

    def __repr__(self):
        return self.username

    def __str__(self):
        return self.username

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user_id == other.user_id
        return False

    def __hash__(self):
        return hash(self.user_id)

    @property
    def username(self):
        return self._username

    @classmethod
    def is_username_taken(cls, username):
        return username in cls._usernames

    @property
    def user_id(self):
        return self._user_id

    @property
    def notifications(self):
        return self._notifications


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

    def to_json(self):
        pass


