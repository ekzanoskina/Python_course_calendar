"""
Сущность, отвечающая за хранение и предоставление данных.
Хранит логику общения с объектами.
Оно хранит пользователей, календари и события.
Хранение в том числе означает сохранение между сессиями в csv файлах
(пароли пользователей хранятся как hash)

Должен быть статическим или Синглтоном

*) Нужно хранить для каждого пользователя все события которые с ним произошли, но ещё не были обработаны.
"""
import csv
import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from typing import List

from Calendar import Calendar
from Event import Event
from User import User

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY


class AuthenticationError(Exception):
    pass


class Backend:
    __instance = None
    users = {}
    calendars = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def load_user_data(self):
        """Load data from CSV files into the class variables."""
        # Load users from the CSV file
        if os.path.exists('users.csv'):
            with open('users.csv', mode='r') as file:
                reader = csv.DictReader(file)
                self.users = {}
                for row in reader:
                    username = row['username']
                    password_hash = row['password']
                    self.users[username] = (User(username, password_hash))

    def save_user_data(self):
        """Save data to CSV files."""
        # Save users to the CSV file
        with open('users.csv', 'w', newline='') as file:
            fieldnames = ['username', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users.values():
                writer.writerow({'username': user.username, 'password': user.get_password()})

    def save_calendar_data(self):
        with open('calendars.json', 'w') as f:
            json.dump({username: calendar.to_dict() for username, calendar in self.calendars.items()}, f, indent=4)

    def load_calendar_data(self):
        if os.path.exists('calendars.json'):
            with open('calendars.json', 'r') as f:
                self.calendars = {username: Calendar.from_dict(calendar_data, self) for username, calendar_data in
                                  json.load(f).items()}


    def get_calendar(self, owner):
        if owner not in self.calendars:
            self.calendars[owner] = Calendar(owner)
        return self.calendars.get(owner)

    def create_user(self, username, password):
        user = User(username, self.hash_password(password))
        self.users[username] = user
        return user

    def check_username_exists(self, username):
        if username in self.users.keys():
            return True
        return False

    def hash_password(self, password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def check_password(self, hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

    def login(self, username, password):
        if username not in self.users or not self.check_password(self.users[username].get_password(), password):
            raise AuthenticationError('Неверное имя пользователя или пароль.')
        else:
            return self.users[username]

    def validate_by_regexp(self, password):
        """Валидация пароля по регулярному выражению."""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(pattern, password):
            raise ValueError('Неверный формат пароля.')
        else:
            return password

    @staticmethod
    def validate_date_format(date_text, format='%d.%m.%Y %H:%M'):
        """Validates that the date_text is in the specified format."""
        try:
            return datetime.strptime(date_text, format)
        except ValueError:
            raise ValueError('Неверный формат даты.')

    @staticmethod
    def compare_dates(start_datetime, end_datetime):
        """Compares two dates to check if end_time is greater than or equal to start_time."""
        if end_datetime >= start_datetime:
            return True
        else:
            raise ValueError('Время окончания события не может быть раньше времени начала.')

    @staticmethod
    def validate_recurrence(recurrence):
        """Проверить, что введенная частота повторений соответствует одному из допустимых значений."""
        if recurrence in ('0', '1', '2', '3', '4'):
            return Event.formate_recurrence(recurrence)
        else:
            raise ValueError('Некорретный ввод.')


    def invite_participants(self, user, event, participants):
        if user == event.organizer:
            for participant in participants:
                print(type(participant))
                if participant.username in self.calendars:
                    try:
                        self.calendars[participant.username].add_unprocessed_events(event)
                        participant.notify(f"Вы были приглашены на мероприятие '{event.title}'.")
                    except Exception as e:
                        print(str(e))
        else:
            raise PermissionError('У вас нет прав доступа.')

    def remove_participant(self, user, event, participants):
        if user == event.organizer:
            for participant in participants:
                if participant in event.participants:
                    try:
                        self.calendars[participant].remove_event(event)
                        event.remove_participant(participant)
                        self.users.get(participant).notify(f"Вы были удалены из мероприятия '{event.title}'.")
                    except Exception as e:
                        print(str(e))
        else:
            raise PermissionError('У вас нет прав доступа.')

    def validate_participants(self, participants):
        if participants:
            participants_list = participants.split()
            if all(self.check_username_exists(username) for username in participants_list):
                return [self.users.get(participant) for participant in participants_list]
            else:
                raise ValueError('Пользователь(-и) не найден(-ы). Попробуйте еще раз')

    def notify_participants(self):
        pass


