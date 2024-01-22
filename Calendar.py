"""
Класс календаря - хранит события.
он умеет искать все события из промежутка (в том числе повторяющиеся)
он умеет добавлять/удалять события.
У каждого календаря ровно один пользователь.
"""
import unittest
from datetime import datetime, timedelta
import json
from typing import List

from dateutil.rrule import rrule, WEEKLY, DAILY, MONTHLY, YEARLY
from Event import Event
from collections import defaultdict

class RepetitionError(Exception):
    pass

class Calendar:
    def __init__(self, owner=None):
        self._events = []
        self._unprocessed_events = []
        self._owner = owner

    def to_dict(self):
        return {
            "owner": self.owner,
            "events": [event.to_dict() for event in self.events],
            "unprocessed_events": [event.to_dict() for event in self.unprocessed_events]
        }

    @staticmethod
    def from_dict(data, backend):
        calendar = Calendar(data["owner"])
        calendar._events = [Event.create_or_get_event(event_data, backend) for event_data in data["events"]]
        calendar._unprocessed_events = [Event.create_or_get_event(event_data, backend) for event_data in data["unprocessed_events"]]
        return calendar

    @property
    def events(self):
        return self._events

    @property
    def unprocessed_events(self):
        return self._unprocessed_events

    @property
    def owner(self):
        return self._owner

    def get_coming_events(self):
        # Получение прошедших и предстоящих событий
        today = datetime.now()
        return self.get_events_in_range(today, today + timedelta(weeks=1))

    def add_event(self, new_event):
        """Добавление события в календарь"""
        if isinstance(new_event, Event):
            self._events.append(new_event)
        else:
            raise TypeError('Событие,добавляемое в календарь должно быть объектом класса Event.')


    def get_events_in_range(self, start_date, end_date):
        rec_dct = {i: freq for i, freq in zip(['once', 'daily', 'weekly', 'monthly', 'yearly'], [0, DAILY, WEEKLY, MONTHLY, YEARLY])}
        daily_events = defaultdict(list)
        start_date = start_date
        end_date = end_date
        for event in sorted(self.events, key=lambda x: x.start_time):
            if event.start_time > end_date:
                break
            if rec_dct[event.recurrence]:
                freq_rule = rrule(rec_dct[event.recurrence], dtstart=event.start_time)
                for dt in sorted(freq_rule.between(start_date, end_date)):
                    daily_events[dt.strftime('%a, %d.%m.%Y')].append(event.generate_periodic_event(dt, dt + event.get_timing()))
                # result.extend(event.generate_periodic_event(dt, dt + event.get_timing()) for dt in freq_rule.between(start_date, end_date))
            else:
                daily_events[event.start_time.dt.strftime('%d.%m.%Y')].append(event)
        return daily_events

    def add_unprocessed_events(self, event):
        if isinstance(event, Event):
            if event not in self.unprocessed_events and event not in self.events:
                self.unprocessed_events.append(event)
            else:
                raise RepetitionError('Участник уже был приглашен на событие.')
        else:
            raise TypeError('Событие должно быть объектом класса Event')

    def get_unprocessed_events(self):
        """Get all unprocessed events for a user."""
        return self._unprocessed_events

    def mark_event_as_processed(self, event):
        """Mark the given events as processed for a user."""
        self._unprocessed_events.remove(event)
    def __repr__(self):
        return f"Calendar(User=@{self._owner})"

    def remove_event(self, event):
        if event in self.events:
            self.events.remove(event)


