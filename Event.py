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
import json

from dateutil.rrule import DAILY, WEEKLY, MONTHLY, YEARLY

from User import User


class Event:
    """
    An Event class representing an event with a title, description, participants, and occurrence type.
    """
    events_map = {}
    count = 1

    def __init__(self, title, start_time=None, end_time=None, description="", participants=None, recurrence=None,
                 organizer=None):
        self.title = title
        self._event_id = Event.count
        Event.count += 1 # создание уникального id
        self._start_time = start_time
        self._end_time = end_time
        self.description = description
        self._participants = participants or []
        self.organizer = organizer
        if isinstance(self.organizer, User):
            self._participants.insert(0, organizer)  # Insert organizer at the beginning of the participants list
        self.recurrence = recurrence
        Event.events_map[self._event_id] = self

    @property
    def start_time(self):
        return self._start_time

    @property
    def participants(self):
        return self._participants

    # def get_unique_id(self):
    #     # Ensure the start time is in ISO format for consistent unique IDs
    #     formatted_start_time = self.start_time.isoformat() if self.start_time else ''
    #     return f"{self.title}-{self.organizer}-{formatted_start_time}"

    def update_event(self, **kwargs):
        # Handle the participant updates separately to avoid issues
        participants = kwargs.pop('participants', None)

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # If participants are provided, update them
        if participants is not None:
            unique_participants = set(self.participants + participants)
            self._participants = list(unique_participants)


    @classmethod
    def create_or_get_event(cls, data, backend):
        """
        Create an Event instance from its serialized dictionary representation.
        """
        data['start_time'] = datetime.fromisoformat(data["start_time"]) if data['start_time'] else None
        data['end_time'] = datetime.fromisoformat(data["end_time"]) if data['end_time'] else None
        data['participants'] = [backend.users[username] for username in data['participants']] if data[
            'participants'] else None
        data['organizer'] = backend.users.get(data['organizer']) if data['organizer'] else None
        # event_id = f"{data['title']}-{data['organizer']}-{data.get('start_time').isoformat() if data.get('start_time') else ''}"
        event_id = data['event_id']
        data.pop('event_id')
        if event_id in Event.events_map:
            existing_event = cls.events_map[event_id]
            existing_event.update_event(**data)
            return existing_event
        else:
            return cls(**data)

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

    @staticmethod
    def formate_recurrence(recurrence):
        """Проверить, что введенная частота повторений соответствует одному из допустимых значений."""
        recurrence_dct = {i: freq for i, freq in zip(range(5), ['once', 'daily', 'weekly', 'monthly', 'yearly'])}
        return recurrence_dct[int(recurrence)]

    @staticmethod
    def formate_date(date_text, format='%d.%m.%Y %H:%M'):
        return datetime.strptime(date_text, format)

    def leave_event(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)

    def to_dict(self):
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
Начало: {self.start_time},
Конец: {self.end_time},
Организатор: {self.organizer},
Участники: {self.participants},
Периодичность: {self.recurrence}""")

    def __str__(self):
        return (f"""Cобытие: {self.title},
Начало: {self.start_time},
Конец: {self.end_time},
Организатор: {self.organizer},
Участники: {self.participants},
Периодичность: {self.recurrence}""")

    def generate_periodic_event(self, start_time, end_time):
        event_copy = Event(title=self.title, description=self.description, recurrence=self.recurrence,
                           organizer=self.organizer)
        event_copy.start_time = start_time
        event_copy.end_time = end_time
        return event_copy

    def get_timing(self):
        return self.end_time - self.start_time

    def add_participant(self, participant: User):
        if participant not in self._participants:
            self._participants.append(participant)
        else:
            raise TypeError('Участник уже был добавлен в событие')

    def remove_participant(self, user: User):
        if user in self._participants:
            self._participants.remove(user)
        # else:
        #     raise PermissionError('Добавлять участников может только организатор.')

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.title == other.title and self.start_time == other.start_time and \
                self.end_time == other.end_time and self.organizer == other.organizer
        return False



