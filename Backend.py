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
from datetime import datetime, time
from time import sleep, strftime, localtime
from typing import List

from Calendar import Calendar
from Event import Event
from User import User

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY


class AuthenticationError(Exception):
    pass
class PermissionError(Exception):
    pass


class Backend:
    __instance = None
    users = {}
    calendars = {}
    logged_in_user = None
    current_calendar = None

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
                for row in reader:
                    username = row['username']
                    # Create a new user only if they don't already exist in the users dictionary.
                    if username not in self.users:
                        password_hash = row['password']
                        self.users[username] = User(username, password_hash)

    def save_user_data(self):
        """Save data to CSV files."""
        # Save users to the CSV file
        with open('users.csv', 'w', newline='') as file:
            fieldnames = ['user_id', 'username', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users.values():
                writer.writerow({'user_id': user.user_id, 'username': user.username, 'password': user.get_password()})

    def save_calendar_data(self):
        with open('calendars.json', 'w') as f:
            json.dump({username: calendar.to_dict() for username, calendar in self.calendars.items()}, f, indent=4)

    def load_calendar_data(self):
        if os.path.exists('calendars.json'):
            with open('calendars.json', 'r') as f:
                self.calendars = {username: Calendar.from_dict(calendar_data, self) for username, calendar_data in
                                  json.load(f).items()}


    def get_calendar(self, owner):
        if owner.username not in self.calendars:
            self.calendars[owner.username] = Calendar(owner.user_id)
        return self.calendars.get(owner.username)

    def create_user(self, username, password):
        try:
            user = User(username, self.hash_password(password))
            print("Учетная запись создана успешно.")
            self.users[username] = user
            self.login(username, password)
        except Exception as e:
            print(str(e))


    def check_username_exists(self, username):
        return username in self.users


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
            user = self.users.get(username)
            self.logged_in_user = user
            self.current_calendar = self.get_calendar(self.logged_in_user)
            print(f'Добро пожаловать, {username}!')
            return user
    def logout(self):
        self.logged_in_user = None
        self.current_calendar = None


    @staticmethod
    def validate_pass_by_regexp(password, prompt):
        """Валидация пароля по регулярному выражению."""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(pattern, password):
            raise ValueError('Неверный формат пароля.')
        else:
            return password

    @staticmethod
    def validate_date_format(date_text, prompt, format='%d.%m.%Y %H:%M'):
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
    def validate_recurrence(recurrence, prompt):
        """Проверить, что введенная частота повторений соответствует одному из допустимых значений."""
        print(recurrence, prompt, Backend.validate_number_input(recurrence, prompt))
        if Backend.validate_number_input(recurrence, prompt):

            return Event.formate_recurrence(recurrence)
        else:
            raise ValueError('Некорретный ввод.')


    def invite_participants(self, event, participants):
        if self.logged_in_user== event.organizer:
            for participant in participants:
                if participant.username in self.calendars:
                    try:
                        self.calendars[participant.username].add_unprocessed_events(event)
                        participant.notify(f"Вы были приглашены на мероприятие '{event.title}'.")
                    except Exception as e:
                        print(str(e))
        else:
            raise PermissionError('У вас нет прав доступа.')

    def remove_participants(self, event, participants):
        if self.logged_in_user == event.organizer:
            print(participants)
            for participant in participants:
                if participant in event.participants:
                    print('hi')
                    try:

                        event.remove_participant(participant)
                        self.calendars[participant.username].remove_event(event)
                        print("Пользователь удален из события.")
                        # self.users.get(participant).notify(f"Вы были удалены из мероприятия '{event.title}'.")
                    except Exception as e:
                        print(str(e))
        else:
            raise PermissionError('У вас нет прав доступа.')

    def validate_participants(self, participants, prompt):
        if participants:
            participants_list = participants.split()
            if all(self.check_username_exists(username) for username in participants_list):
                return [self.users.get(participant) for participant in participants_list]
            else:
                raise ValueError('Пользователь(-и) не найден(-ы). Попробуйте еще раз')


    def manage_unprocessed_evens(self):
        unprocessed_events = self.current_calendar.get_unprocessed_events()
        return unprocessed_events

    def accept_invitation(self, event):
        try:
            event.add_participant(self.logged_in_user)  # добавление участника в событие, если он согласился участвовать
            print(
                'Событие успешно добавлено в Ваш календарь. Другие участники получат уведомление о том, что вы присоединитесь к собранию.')
            self.current_calendar.mark_event_as_processed(event)
            self.current_calendar.add_event(event)
        except Exception as e:
            print(str(e))

                    # отправка уведомления о добавлении нового участника
    def decline_invitation(self, event):
        self.current_calendar.mark_event_as_processed(event)
        # event.owner.notify()

    @staticmethod
    def validate_number_input(user_input, prompt):
        if user_input in re.findall(r'.*?(\d):.*?', prompt):
            return user_input
        else:
            raise ValueError('Некорректный ввод.')
    @staticmethod
    def validate_str_input(user_input, prompt):
        if user_input.lower() in re.findall(r'\(([^)]+)\)', prompt)[0].split('/'):
            return user_input
        else:
            raise ValueError('Некорректный ввод.')

    @staticmethod
    def input_with_validation(prompt, validation_func):
        while True:
            user_input = input(prompt)
            try:
                return validation_func(user_input, prompt)
            except Exception as e:
                print(f'{str(e)} Попробуйте снова.')

    def create_event(self, title, start_time, end_time, description, recurrence):
        organizer = self.logged_in_user
        event = Event(title, start_time, end_time, description, recurrence=recurrence, organizer=organizer)
        if event:
            self.current_calendar.add_event(event)
        print('Событие успешно создано и добавлено в Ваш календарь.')
        return event

    def notify_participants(self):
        pass

    def get_events_in_range(self, start_date, end_date):
        return self.current_calendar.get_events_in_range(start_date, end_date)

    def get_coming_events(self):
        coming_events = self.current_calendar.get_coming_events()
        if coming_events:
            print('Предстоящие события:')
            for date, events in coming_events.items():
                print()
                print(date)
                for event in sorted(events, key=lambda x: x.start_time):
                    print(f'{event.start_time.strftime("%H:%M")} - {event.end_time.strftime("%H:%M")}: {event.title}')
        else:
            print('У вас нет событий на ближайшую неделю.')

    def get_today_events(self):
        print("Календарь запускается...")
        sleep(1)  # Пауза в 1 секунду
        # Вывод текущей даты
        print("Сегодняшняя дата: " + strftime("%A %d %b, %Y", localtime()))
        # Вывод текущего времени
        print("Текущее время: " + strftime("%H:%M", localtime()))
        sleep(1)  # Пауза в 1 секунду
        current_date = datetime.now().date()
        start_of_day = datetime.combine(current_date, time.min)
        end_of_day = datetime.combine(current_date, time(23, 59))
        today_events = self.current_calendar.get_events_in_range(start_of_day, end_of_day)
        if today_events:
            print(f'События на сегодня:')
            for event in today_events:
                print(event)
        else:
            print('На сегодня у вас ничего не запланировано.')

    def show_all_events(self):
        all_events = self.calendars[self.logged_in_user.username].events
        return all_events

    def update_event(self, event, **kwargs):
        if self.logged_in_user == event.organizer:
            return event.update_event(**kwargs)

    def leave_event(self, event):
        if self.logged_in_user in event.participants and self.logged_in_user != event.organizer:
            event.remove_participant(self.logged_in_user)
            self.current_calendar.remove_event(event)
            print('Вы успешно покинули событие.')
        else:
            raise PermissionError("Вы не можете покинуть событие, в котором Вы организатор.")

    def delete_event(self, event):
        if self.logged_in_user in event.participants and self.logged_in_user == event.organizer:
            for participant in event.participants:
                event.remove_participant(participant)
                self.calendars.get(participant.username).remove_event(event)
                Event.delete_event(event)
            print('Вы успешно удалили событие.')
        else:
            raise PermissionError('Вы не можете удалить событие, так как не являетесь организатором.')



