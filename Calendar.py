"""
Класс календаря - хранит события.
он умеет искать все события из промежутка (в том числе повторяющиеся)
он умеет добавлять/удалять события.
У каждого календаря ровно один пользователь.
"""

from datetime import datetime, timedelta
from dateutil.rrule import rrule, WEEKLY, DAILY, MONTHLY, YEARLY
from Event import Event
from collections import defaultdict
from Notification import Notification


class RepetitionError(Exception): # ошибка, возникающая при попытке повторного добавления участника в событие
    pass

class Calendar:
    def __init__(self, owner:str):
        self._events = []
        self._unprocessed_events = []
        self._notifications = []
        self._owner = owner

    def to_dict(self):
        """Преобразование календаря в словарь для дальнейшей записи в json файл."""
        return {
            "owner": self.owner,
            "events": [event.to_dict() for event in self.events],
            "unprocessed_events": [event.to_dict() for event in self.unprocessed_events],
            "notifications": [notification.to_dict() for notification in self.notifications]
        }

    @staticmethod
    def from_dict(data):
        """Создание календаря из словаря."""
        calendar = Calendar(data["owner"])
        calendar._events = [Event.create_or_get_event(event_data) for event_data in data["events"]]
        calendar._unprocessed_events = [Event.create_or_get_event(event_data) for event_data in data["unprocessed_events"]]
        calendar._notifications = [Notification.from_dict(notification_data) for notification_data in data["notifications"]]
        return calendar

    @property
    def events(self):
        """Список событий в календаре."""
        return self._events

    @property
    def unprocessed_events(self):
        """Список непрошедших событий в календаре."""
        return self._unprocessed_events

    @property
    def notifications(self):
        """Список уведомлений в календаре."""
        return self._notifications

    @property
    def owner(self):
        return self._owner

    def get_coming_events(self):
        """Получение предстоящих событий."""
        today = datetime.now()
        return self.get_events_in_range(today, today + timedelta(weeks=1))

    def add_event(self, new_event):
        """Добавление события в календарь"""
        if isinstance(new_event, Event):
            self._events.append(new_event)
        else:
            raise TypeError('Событие,добавляемое в календарь должно быть объектом класса Event.')


    def get_events_in_range(self, start_date, end_date):
        """Находит события, которые начинаются в указанный период времени."""
        rec_dct = {i: freq for i, freq in zip(['один раз', 'каждый день', 'каждую неделю', 'каждый месяц', 'каждый год'], [0, DAILY, WEEKLY, MONTHLY, YEARLY])}
        daily_events = defaultdict(list)
        start_date = start_date
        end_date = end_date
        for event in sorted(self.events, key=lambda x: x.start_time):
            if event.start_time > end_date:
                break
            if rec_dct[event.recurrence]:
                freq_rule = rrule(rec_dct[event.recurrence], dtstart=event.start_time)
                for dt in sorted(freq_rule.between(start_date - timedelta(seconds=1), end_date + timedelta(seconds=1))): # границы диапазона не включаются в выборку
                    daily_events[dt.strftime('%a, %d.%m.%Y')].append(event.generate_periodic_event(dt, dt + event.get_timing()))
            elif start_date <= event.start_time <= end_date:
                daily_events[event.start_time.strftime('%d.%m.%Y')].append(event)
        return daily_events

    def add_unprocessed_events(self, event):
        """Добавление необработанного события в календарь участника, после его приглашения в событие"""
        if isinstance(event, Event):
            if event not in self.unprocessed_events and event not in self.events:
                self.unprocessed_events.append(event)
            else:
                raise RepetitionError('Участник уже был приглашен на событие.')
        else:
            raise TypeError('Событие должно быть объектом класса Event')

    def get_unprocessed_events(self):
        """Получение всех необработанных событий для пользователя."""
        return self._unprocessed_events

    def mark_event_as_processed(self, event):
        """Отметить событие как обработанное для пользователя и добавить его в список events."""
        self._unprocessed_events.remove(event)
    def __repr__(self):
        return f"Calendar(User=@{self._owner})"

    def remove_event(self, event):
        """Удаление события из календаря."""
        if event in self.events:
            self.events.remove(event)

    def notify(self, n: Notification):
        """Уведомление об изменениях произошедших с событием."""
        self.notifications.append(n)

