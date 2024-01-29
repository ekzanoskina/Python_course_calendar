"""
Пользователь - имеет логин и пароль, а так же календарь.
у пользователя есть итендифекатор начинающийся с @
"""
import uuid


class User:
    _users_by_username = {}  # словарь для хранения пользователей по username
    _usernames = set()  # множество на уровне класса для контроля уникальности username
    def __init__(self, username, password):
        if username in User._usernames:
            raise ValueError(f"Username {username} is already taken.")
        self._username = username
        self._password = password
        self._user_id = str(uuid.uuid4())  # генерирует уникальное id
        User._usernames.add(username)
        User._users_by_username[username] = self


    def __repr__(self):
        return self.username

    def __str__(self):
        return self.username
    @classmethod
    def get_user_by_username(cls, username):
        """Получить пользователя по имени пользователя из словаря _users_by_username."""
        return cls._users_by_username.get(username)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user_id == other.user_id
        return False

    def __hash__(self):
        """Хэширует идентификатор пользователя."""
        return hash(self.user_id)

    @property
    def username(self):
        return self._username

    @classmethod
    def is_username_taken(cls, username):
        """Проверяет, занято ли указанное имя пользователя."""
        return username in cls._usernames

    @property
    def user_id(self):
        return self._user_id

    def get_password(self):
        """Получить пароль пользователя."""
        return self._password



