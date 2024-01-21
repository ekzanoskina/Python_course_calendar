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

from dateutil.rrule import rrule

from Event import Event
from collections import defaultdict


# class Calendar:
#     """
#     A Calendar class that stores events and associated operations.
#     """
#     def __init__(self, user):
#         self._user = user
#         self._events =


# def add_event(self, event):
#     self._events.append(event)
#
# def remove_event(self, event):
#     self._events.remove(event)
#
# def find_events_in_range(self, start_date, end_date):
#     results = []
#     for event in self._events:
#         if event.is_in_range(start_date, end_date):
#             results.append(event)
#     return results

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
    def from_dict(data):
        calendar = Calendar(data["owner"])
        calendar._events = [Event.create_or_get_event(event_data) for event_data in data["events"]]
        calendar._unprocessed_events = [Event.create_or_get_event(event_data) for event_data in data["unprocessed_events"]]
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

    def get_today_events(self):
        # Получение событий на сегодняшнюю дату
        today = datetime.now().date()
        return self.events.get(today, [])

    def get_coming_events(self):
        # Получение прошедших и предстоящих событий
        today = datetime.now()
        return self.get_events_in_range(today, today + timedelta(weeks=1))

    def add_event(self, new_event):
        # Добавление события в календарь
        if isinstance(new_event, Event):
            self._events.append(new_event)
        else:
            raise TypeError('Событие,добавляемое в календарь должно быть объектом класса Event.')

    # def create_event(self, title, start_time, end_time, description="", recurrence=None, organizer=''):
    #     new_event = Event(title=title, start_time=start_time, end_time=end_time, description=description,
    #                       recurrence=recurrence, organizer=organizer)
    #     return new_event

    # def get_events_in_range(self, start_date, end_date):
    #     result = []
    #     start_date = start_date
    #     end_date = end_date
    #     for event in sorted(self.events, key=lambda x: x.start_time):
    #         if event.start_time > end_date:
    #             break
    #         if event.recurrence:
    #             freq_rule = rrule(event.recurrence, dtstart=event.start_time)
    #             result.extend(event.generate_periodic_event(dt, dt + event.get_timing()) for dt in freq_rule.between(start_date, end_date))
    #         else:
    #             result.append(event)
    #     return result

    def get_events_in_range(self, start_date, end_date):
        daily_events = defaultdict(list)
        start_date = start_date
        end_date = end_date
        for event in sorted(self.events, key=lambda x: x.start_time):
            if event.start_time > end_date:
                break
            if event.recurrence:
                freq_rule = rrule(event.recurrence, dtstart=event.start_time)
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

# Использование класса Calendar
# cal = Calendar()
# cal.add_event('2023-04-15', 'Событие 1')
# cal.add_event('2023-04-16', 'Событие 2')  # Предполагаем, что сегодня 2023-04-16
# cal.add_event('2023-04-17', 'Событие 3')
#
# today_events = cal.get_todays_events()
# print("События на сегодня:", today_events)
#
# past_events, upcoming_events = cal.get_past_and_upcoming_events()
# print("Прошедшие события:", past_events)
# print("Предстоящие события:", upcoming_events)
