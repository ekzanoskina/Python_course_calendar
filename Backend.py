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
from Notification import Notification
from User import User

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
    users_storage_file = 'users.csv'
    calendars_storage_file = 'calendars.json'


    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def load_user_data(self):
        """Загружает данные из CSV-файлов в переменные класса."""
        if os.path.exists(self.users_storage_file):
            with open(self.users_storage_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']
                    # Create a new user only if they don't already exist in the users dictionary.
                    if username not in self.users:
                        password_hash = row['password']
                        self.users[username] = User(username, password_hash)

    def save_user_data(self):
        """Сохраняет данные в CSV-файлы."""
        with open(self.users_storage_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['user_id', 'username', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users.values():
                writer.writerow({'user_id': user.user_id, 'username': user.username, 'password': user.get_password()})


    def save_calendar_data(self):
        """Сохраняет данные календаря в JSON-файл."""
        with open(self.calendars_storage_file, 'w', encoding='utf-8') as f:
            json.dump({username: calendar.to_dict() for username, calendar in self.calendars.items()}, f, indent=4)

    def load_calendar_data(self):
        """Загружает данные календаря из JSON-файла."""
        if os.path.exists(self.calendars_storage_file):
            with open(self.calendars_storage_file, 'r', encoding='utf-8') as f:
                self.calendars = {username: Calendar.from_dict(calendar_data) for username, calendar_data in
                                  json.load(f).items()}


    def get_calendar(self, owner: User):
        """Возвращает календарь владельца."""
        if owner.username not in self.calendars:
            self.calendars[owner.username] = Calendar(owner.user_id)
        return self.calendars.get(owner.username)

    def create_user(self, username, password):
        """Создает нового пользователя."""
        try:
            user = User(username, self.hash_password(password))
            self.users[username] = user
            self.login(username, password)
            return user
        except Exception as e:
            print(str(e))


    def check_username_exists(self, username):
        """Проверяет, что пользователь с введенным username существует в системе."""
        return username in self.users


    def hash_password(self, password):
        """Хеширует пароль пользователя."""
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def check_password(self, hashed_password, user_password):
        """Проверяет соответствие хешированного пароля введенному паролю пользователя."""
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

    def drop_password(self, username, password):
        """Сброс пароля."""
        if self.check_username_exists(username):
            if self.validate_pass_by_regexp(password):

                user = self.users.get(username)
                user.set_password(self.hash_password(password))
            else:
                raise ValueError('Пароль долен содержать не менее 8 символов, включая цифру и строчную букву.')
        else:
            raise ValueError('Пользователь с таким именем не найден.')

    def login(self, username, password):
        """Аутентифицирует пользователя."""
        if username not in self.users or not self.check_password(self.users[username].get_password(), password):
            raise AuthenticationError('Неверное имя пользователя или пароль.')
        else:
            user = self.users.get(username)
            self.logged_in_user = user
            self.current_calendar = self.get_calendar(self.logged_in_user)
            return user
    def logout(self):
        """Выход пользователя из системы."""
        self.logged_in_user = None
        self.current_calendar = None



    @staticmethod
    def validate_pass_by_regexp(password, prompt=None):
        """Валидация пароля по регулярному выражению."""
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(pattern, password):
            raise ValueError('Неверный формат пароля.')
        else:
            return password

    @staticmethod
    def validate_date_format(date_text, prompt=None, format='%d.%m.%Y %H:%M'):
        """Валидация формата даты по определенному формату."""
        try:
            return datetime.strptime(date_text, format)
        except ValueError:
            raise ValueError('Неверный формат даты.')

    @staticmethod
    def compare_dates(start_datetime, end_datetime):
        """Сравнение двух дат для проверки, что дата конца события не раньше даты начала."""
        if end_datetime >= start_datetime:
            return True
        else:
            raise ValueError('Время окончания события не может быть раньше времени начала.')

    @staticmethod
    def validate_recurrence(recurrence, prompt=None):
        """Проверить, что введенная частота повторений соответствует одному из допустимых значений."""
        if Backend.validate_number_input(recurrence, prompt):

            return Event.formate_recurrence(recurrence)
        else:
            raise ValueError('Некорретный ввод.')


    def invite_participants(self, event, participants):
        """Приглашение участников на событие."""
        if self.logged_in_user == event.organizer:
            n = Notification(event.event_id, f"Вы были приглашены на событие '{event.title}'.")
            for participant in participants:
                if participant.username in self.calendars:
                    try:
                        participant_calendar = self.calendars[participant.username]
                        participant_calendar.add_unprocessed_events(event)
                        print(f'Участник {participant.username} успешно приглашен на событие, он может принять приглашение или отклонить его.')
                        participant_calendar.notify(n)
                    except Exception as e:
                        print(str(e))
        else:
            raise PermissionError('Вы не можете добавить участников в событие, в котором Вы не организатор.')

    def remove_participants(self, event, participants):
        """Удаление участников из события."""
        if self.logged_in_user == event.organizer: # только организатор
            for participant in participants:
                if participant in event.participants: # пользователь должен быть среди участников события
                    if participant != event.organizer: # организатор не может удалить себя из события
                        try:
                            event.remove_participant(participant)
                            participant_calendar = self.calendars[participant.username]
                            participant_calendar.remove_event(event)
                            n = Notification(event.event_id, f"Вы были удалены из мероприятия '{event.title}'.")
                            participant_calendar.notify(n)
                        except Exception as e:
                            print(str(e))
                    else:
                        raise ValueError('Вы не можете удалить себя из участников, так как Вы являетесь организатором.')
                else:
                    raise ValueError('Участник не был приглашен на событие.')
        else:
            raise PermissionError('Вы не можете удалить участников из события, в котором Вы не организатор.')

    def validate_participants(self, participants, prompt=None):
        """Проверка корректности участников и перевод из объекта str в объект list с элементами User"""
        if participants:
            participants_list = participants.split()
            if all(self.check_username_exists(username) for username in participants_list):
                return [self.users.get(participant) for participant in participants_list]
            else:
                raise ValueError('Пользователь(-и) не найден(-ы).')


    def manage_unprocessed_evens(self):
        """Получение списка необработанных событий из текущего календаря."""
        unprocessed_events = self.current_calendar.get_unprocessed_events()
        return unprocessed_events

    def accept_invitation(self, event):
        """Принятие приглашения на участие в событии.
        Осуществляется попытка добавить текущего пользователя как участника события.
    В случае успеха отправляются уведомления остальным участникам.
    При возникновении ошибки выводится информация об ошибке.
    """
        try:
            event.add_participant(self.logged_in_user)  # добавление участника в событие, если он согласился участвовать
            self.current_calendar.mark_event_as_processed(event)
            self.current_calendar.add_event(event)
            n = Notification(event.event_id, f"Участник {self.logged_in_user} присоединился к событию {event.title}.")
            for participant in event.participants:
                if participant != self.logged_in_user:
                    self.calendars.get(participant.username).notify(n)
        except Exception as e:
            print(str(e))

                    # отправка уведомления о добавлении нового участника
    def decline_invitation(self, event):
        """Отказ от участия в событии.Событие отмечается как обработанное, и отправляется уведомление организатору."""
        self.current_calendar.mark_event_as_processed(event)
        n = Notification(event.event_id, f"Участник {self.logged_in_user} отказался присоединиться к событию {event.title}.")
        self.calendars.get(event.organizer.username).notify(n)

    @staticmethod
    def validate_number_input(user_input, prompt=None):
        """Валидация ввода пользователя, когда нужно ввести цифру.
        Возвращает введённое число, если оно соответствует условиям.
    В противном случае вызывается исключение ValueError."""
        if user_input in re.findall(r'.*?(\d):.*?', prompt):
            return user_input
        else:
            raise ValueError('Некорректный ввод.')
    @staticmethod
    def validate_str_input(user_input, prompt=None):
        """Валидация строкового ввода.Возвращает введённую строку, если она соответствует условиям.
    В противном случае вызывается исключение ValueError."""
        if user_input.lower() in re.findall(r'\(([^)]+)\)', prompt)[0].split('/'):
            return user_input
        else:
            raise ValueError('Некорректный ввод.')

    @staticmethod
    def validate_not_empty(user_input, prompt=None):
        """Проверка, чо ввод не пустой."""
        if not user_input:
            raise ValueError('Некорректный ввод.')
        else:
            return user_input
    @staticmethod
    def validate_username_by_regex(username, prompt=None):
        """Валидация имени пользоцателя по регулярному выражению."""
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError('Неверный формат имени.')
        else:
            return username.lower()
    @staticmethod
    def input_with_validation(prompt, validation_func):
        """Функция для ввода данных с валидацией."""
        while True:
            user_input = input(prompt)
            try:
                return validation_func(user_input, prompt)
            except Exception as e:
                print(f'{str(e)} Попробуйте снова.')

    def create_event(self, title, start_time, end_time, description, recurrence):
        """Создание нового события в календаре."""
        organizer = self.logged_in_user
        event = Event(title, start_time, end_time, description, recurrence=recurrence, organizer=organizer)
        if event:
            self.current_calendar.add_event(event)
        return event

    def get_events_in_range(self, start_date, end_date):
        """Получение списка событий за определённый промежуток дат."""
        events_in_range = self.current_calendar.get_events_in_range(start_date, end_date)
        if events_in_range:
            print('События в данном промежутке времени:')
            for date, events in events_in_range.items():
                for event in sorted(events, key=lambda x: x.start_time):
                    yield f'{date}\n{event.start_time.strftime("%H:%M")} - {event.end_time.strftime("%H:%M")}: {event.title}'
        else:
            print('Не найдено ни одного события.')

    def get_coming_events(self):
        """Получение списка предстоящих событий, ближайшая неделя."""
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
        """Получение и вывод списка событий на текущий день."""
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
        """Возвращает список всех событий для текущего вошедшего пользователя."""
        all_events = self.calendars[self.logged_in_user.username].events
        return all_events

    def update_event(self, event, **kwargs): # **kwargs: Параметры для обновления события.
        """Обновляет событие, если текущий пользователь является его организатором."""
        if self.logged_in_user == event.organizer:
            if len(event.participants) > 1:
                n = Notification(event.event_id, f"Событие '{event.title}' было изменено организатором.")
                for participant in event.participants:
                    if participant != event.organizer:
                        self.calendars.get(participant.username).notify(n)
            return event.update_event(**kwargs)
        else:
            raise PermissionError("Вы не можете изменить событие, так как не являетесь его организатором.")


    def leave_event(self, event):
        """Покидает событие, если текущий пользователь является участником, но не организатором."""
        if self.logged_in_user in event.participants and self.logged_in_user != event.organizer:
            event.remove_participant(self.logged_in_user)
            self.current_calendar.remove_event(event)
            for participant in event.participants:
                if participant != self.logged_in_user:
                    n = Notification(event.event_id, f"Участник {self.logged_in_user} покинул событие {event.title}.")
                    self.calendars.get(participant.username).notify(n)
        else:
            raise PermissionError("Вы не можете покинуть событие, в котором Вы организатор.")

    def delete_event(self, event):
        """Удаляет событие, если текущий пользователь является организатором."""
        n = Notification(event.event_id, f"Событие '{event.title}' было удалено организатором.")
        if self.logged_in_user in event.participants and self.logged_in_user == event.organizer:
            for participant in event.participants:
                participant_calendar = self.calendars.get(participant.username)
                event.remove_participant(participant)
                if participant != event.organizer:
                    participant_calendar.notify(n)
                participant_calendar.remove_event(event)
                Event.delete_event(event)

        else:
            raise PermissionError('Вы не можете удалить событие, так как не являетесь его организатором.')

    def get_unread_notifications(self):
        """Генератор, возвращающий непрочитанные уведомления для текущего календаря пользователя.
               После вызова уведомление помечается как прочитанное."""
        unread_notifications = list(filter(lambda n:n.status == 'unread', self.current_calendar.notifications))
        if unread_notifications:
            if len(unread_notifications) > 1:
                for i, n in enumerate(unread_notifications, 1):
                    yield f'{i}. {n.message}'
                    n.status = 'read'
            else:
                yield unread_notifications[0].message
                unread_notifications[0].status = 'read'

        else:
            yield 'У вас нет непрочитанных уведомлений.'



