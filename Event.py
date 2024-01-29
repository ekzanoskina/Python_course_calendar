"""
Описывает некоторые "событие" - промежуток времени с присвоенными характеристиками
У события должно быть описание, название и список участников
Событие может быть единожды созданым
Или периодическим (каждый день/месяц/год/неделю)

Каждый пользователь ивента имеет свою "роль"
организатор умеет изменять названия, список участников, описание, а так же может удалить событие
участник может покинуть событие

запрос на хранение в json
Уметь создавать из json и записывать в него

Иметь покрытие тестами
Комментарии на нетривиальных методах и в целом документация
"""
from datetime import datetime, timedelta
from User import User


class Event:
    """
    An Event class representing an event with a title, description, participants, and occurrence type.
    """
    events_map = {} #  Словарь, содержащий все созданные события с ключами - идентификаторами событий.
    count = 1 # Счетчик объектов класса, используется для присвоения уникального идентификатора каждому событию.

    def __init__(self, title, start_time=None, end_time=None, description="", participants=None, recurrence=None,
                 organizer:User=None):
        self._title = title
        self._event_id = Event.count
        Event.count += 1 # создание уникального id
        self._start_time = start_time
        self._end_time = end_time
        self._description = description
        self._participants = participants or []
        self._organizer = organizer
        if isinstance(self._organizer, User) and self._organizer not in self._participants:
            self._participants.insert(0, self._organizer)  # Insert organizer at the beginning of the participants list
        self._recurrence = recurrence
        Event.events_map[self._event_id] = self


    @property
    def event_id(self):
        return self._event_id
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if isinstance(title, str):
            self._title = title

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str):
            self._description = description

    @property
    def organizer(self):
        return self._organizer

    @property
    def recurrence(self):
        return self._recurrence

    @recurrence.setter
    def recurrence(self, recurrence):
        self.recurrence = recurrence
    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        if isinstance(start_time, str):
            self._start_time = self.formate_date(start_time)
        else:
            self._start_time = start_time

    @property
    def participants(self):
        return self._participants

    @participants.setter
    def participants(self, participants):
        if isinstance(participants, list):
            self._participants.extend(participants)

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        if isinstance(end_time, str):
            self._end_time = self.formate_date(end_time)
        else:
            self._end_time = end_time

    def update_event(self, **kwargs):
        """Обновляет атрибуты события с использованием предоставленных именованных аргументов, участники обрабатываются отдельно"""
        participants = kwargs.pop('participants', None)

        for key, value in kwargs.items():
            # Assuming the attribute names begin with underscore and match the keys directly
            if hasattr(self, f'_{key}'):
                setattr(self, f'_{key}', value)

        if participants is not None:
            unique_participants = set(self.participants + participants)
            self._participants = list(unique_participants)

    @classmethod
    def create_or_get_event(cls, data):
        """
        Создает новый экземпляр Event или получает уже существующий из `events_map`, используя предоставленный словарь данных.
        """
        data['start_time'] = datetime.fromisoformat(data["start_time"]) if data['start_time'] else None
        data['end_time'] = datetime.fromisoformat(data["end_time"]) if data['end_time'] else None
        data['participants'] = [User.get_user_by_username(username) for username in data['participants']] if data[
            'participants'] else None
        data['organizer'] = User.get_user_by_username(data['organizer']) if data['organizer'] else None
        try:
            event_id = int(data.pop('event_id'))
            if event_id in cls.events_map:  # Check if the event_id exists in the events_map of the class
                existing_event = cls.events_map[event_id]
                existing_event.update_event(**data)
                return existing_event
            else:
                return cls(**data)
        except Exception as e:
            print(str(e))



    @staticmethod
    def formate_recurrence(recurrence):
        """Проверяет валидность и возвращает удобочитаемое описание частоты повторения события."""
        recurrence_dct = {i: freq for i, freq in zip(range(5), ['один раз', 'каждый день', 'каждую неделю', 'каждый месяц', 'каждый год'])}
        return recurrence_dct[int(recurrence)]

    @staticmethod
    def formate_date(date_text, format='%d.%m.%Y %H:%M'):
        """Преобразует строку с датой в объект datetime согласно предоставленному формату."""
        return datetime.strptime(date_text, format)

    def leave_event(self, participant):
        """Удаляет участника из списка участников события."""
        if participant in self.participants:
            self.participants.remove(participant)

    def to_dict(self):
        """Подготавливает данные из Event для записи в json."""
        return {
            "event_id": self._event_id,
            "title": self.title,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "description": self.description,
            "recurrence": self.recurrence,
            "participants": [participant.username for participant in self._participants],
            "organizer": self.organizer.username if self.organizer else None
        }

    def __repr__(self):
        return (f"""Cобытие: {self.title},
Начало: {self.start_time.strftime('%d.%m.%Y %H:%M')},
Конец: {self.end_time.strftime('%d.%m.%Y %H:%M')},
Организатор: {self.organizer},
Участники: {', '.join([participant.username for participant in self.participants])},
Периодичность: {self.recurrence}""")

    def __str__(self):
        return (f"""
Cобытие: {self.title},
Начало: {self.start_time.strftime('%d.%m.%Y %H:%M')},
Конец: {self.end_time.strftime('%d.%m.%Y %H:%M')},
Организатор: {self.organizer},
Участники: {', '.join([participant.username for participant in self.participants])},
Периодичность: {self.recurrence}""")

    def generate_periodic_event(self, start_time, end_time):
        """Генерирует периодическое событие на основе текущего, внося изменения во времена начала и окончания."""
        event_copy = Event(title=self.title, description=self.description, recurrence=self.recurrence,
                           organizer=self.organizer)
        event_copy.start_time = start_time
        event_copy.end_time = end_time
        return event_copy

    def get_timing(self):
        """Возвращает продолжительность события как разность между временем окончания и временем начала."""
        return self.end_time - self.start_time

    def add_participant(self, participant: User):
        """Добавляет пользователя в список участников события, если он еще не добавлен."""
        if participant not in self._participants:
            self._participants.append(participant)
        else:
            raise TypeError('Участник уже был добавлен в событие')

    def remove_participant(self, user: User):
        """Удаляет пользователя из списка участников события, если он там присутствует."""
        if user in self._participants:
            self._participants.remove(user)
        else:
            raise ValueError

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.event_id == other.event_id
        return False

    @classmethod
    def delete_event(cls, event):
        """Удаляет событие из словаря events_map."""
        if event.event_id in cls.events_map:
            del cls.events_map[event.event_id]
        else:
            raise ValueError(f"No event found with event_id {event.event_id}")


