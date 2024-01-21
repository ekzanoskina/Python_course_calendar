"""
Позволяет зайти по логину-паролю или создать нового пользователя (а так же выйти из аккаунта)
Позволяет выбрать календарь, узнать ближайшие события, события из промежутка времени, а также
Создать событие или удалить событие
После создания события можно добавить туда пользователей
Если нас добавили в событие или удалили мы получаем уведомление

в main можно использовать ТОЛЬКО interface
"""
import locale
import re
from datetime import datetime, time
import calendar
from dateutil.rrule import rrule, DAILY

locale.setlocale(locale.LC_ALL, "")

from Backend import Backend
from Calendar import Calendar
from Event import Event
from User import User

from time import sleep, strftime, localtime
class Interface:
    calendar = None
    backend = None
    state = "start"
    logged_in_user = None
    func_request = list()

    @staticmethod
    def work():
        Interface.func_request = [Interface.start]
        while Interface.func_request:
            Interface.func_request[0]()
            del Interface.func_request[0]

        print("Работа календаря завершена.")

    @staticmethod
    def start():
        Interface.state = "start"
        print("Добро пожаловать в MyCalendar!")
        print('Использование календаря доступно только зарегистрированным пользователям.')
        Interface.backend = Backend()

        Interface.func_request.append(Interface.backend.load_user_data)
        Interface.func_request.append(Interface.backend.load_calendar_data)
        Interface.func_request.append(Interface.manage_user)


    @staticmethod
    def manage_user():
        print("Что бы вы хотели сделать?")
        user_choice = input(
"""1: Войти в систему, 
2: Создать нового пользователя,
3: Закончить работу.
Введите соответствующую цифру: """
        )
        if user_choice == '1':
            Interface.func_request.append(Interface.login)
        elif user_choice == '2':
            Interface.func_request.append(Interface.create_user)
        elif user_choice == '3':
            return
        else:
            raise Exception('Введите цифру от 1 до 3.')
        print(Interface.func_request)

    @staticmethod
    def create_user():
        while True:
            username = input("Введите имя пользователя: ")

            # Проверяем, существует ли уже пользователь
            if Interface.backend.check_username_exists(username):
                print(f"Пользователь с именем {username} уже существует. Попробуйте войти или использовать другое имя.")
                continue_login = input("Хотите войти? (да/нет): ").lower()
                if continue_login == "да":
                    Interface.func_request.append(lambda: Interface.login(username))
                    break  # Выходим из цикла, если пользователь выбрал входить
                else:
                    # Возвращаемся к началу цикла, чтобы предложить ввести новое имя пользователя
                    print('Попробуйте снова.')
                    continue
            else:
                # Пользователя нет в системе, предлагаем создать новый пароль
                def create_password():
                    while True:
                        password = input(
                        """Придумайте пароль.Пароль должен содержать восемь и более символов,\nвключая не менее одной цифры, одной буквы в верхнем регистре и одной буквы в нижнем регистре.\n""")
                        try:
                            return Interface.backend.validate_by_regexp(password)
                        except Exception as e:
                            print(str(e))
                password = create_password()
                Interface.backend.create_user(username, password)
                print("Учетная запись создана успешно.")
                Interface.backend.login(username, password)
                Interface.backend.save_user_data()
                Interface.func_request.append(Interface.main_menu)
                break

        # Interface.func_request.append(Interface.manage_user)



    @staticmethod
    def login(username=None):
        if not username:
            username = input('Введите имя пользователя: ')
        password = input('Введите пароль: ')
        try:
            Interface.backend.login(username, password)
            print(f'Добро пожаловать, {username}!')
            sleep(1)
            user = Interface.backend.users.get(username)
            Interface.logged_in_user = user
            Interface.calendar = Interface.backend.get_calendar(Interface.logged_in_user.username)
            Interface.backend.save_calendar_data()
            Interface.func_request.append(Interface.show_notifications)
            Interface.func_request.append(Interface.manage_unprocessed_evens)

        except Exception as e:
            print(f'Ошибка: {str(e)}')
            sleep(1)
            Interface.func_request.append(Interface.manage_user)

    @staticmethod
    def show_notifications():
        notifications = Interface.logged_in_user.get_notifications()
        print("Ваши уведомления:")
        for notification in notifications:
            print(notification)
    @staticmethod
    def manage_unprocessed_evens():
        unprocessed_events = Interface.calendar.get_unprocessed_events()
        if unprocessed_events:
            print('У вас есть необработанные события.\nДалее по одному будут показаны события, на которые вас пригласили.\n Введите 1: чтобы добавить событие в свой календарь,\n 2: чтобы отказаться от участия.\n 3: чтобы ответить позже.\n')
            for event in unprocessed_events:
                print(event)
                reply = input()
                if reply == '1':
                    event.add_participant(Interface.logged_in_user.username) #  добавление участника в событие, если он согласился участвовать
                    Interface.calendar.mark_event_as_processed(event)
                    Interface.calendar.add_event(event)

                    print('Событие успешно добавлено в Ваш календарь. Другие участники получат уведомление о том, что вы присоединитесь к собранию.')
                    # отправка уведомления о добавлении нового участника
                elif reply == '2':
                    Interface.calendar.mark_event_as_processed(event)
                elif reply == '3':
                    continue
                else:
                    raise ValueError
        Interface.backend.save_calendar_data()
        Interface.func_request.append(Interface.main_menu)


    @staticmethod
    def main_menu():
        menu_options = [Interface.show_calendar, Interface.get_today_events, Interface.get_coming_events, Interface.get_events_in_range, Interface.create_event, Interface.delete_event, Interface.add_paticipants, Interface.show_all_event, Interface.logout]
        Interface.state = "read"
        ans = input("""Что вы хотите сделать?
1: Посмотреть календарь на текущий месяц,
2: Посмотреть события на текущую дату,
3: Посмотреть события на ближайшую неделю, 
4: Посмотреть события из промежутка времени,
5: Создать событие,
6: Добавить участников,
7: Удалить событие,
8: Удалить участников из события,
9: Выйти из системы.
""")
        if ans.isdigit() and 0 < int(ans) <= len(menu_options):
            Interface.func_request.append(menu_options[int(ans) - 1])
        else:
            raise ValueError



    @staticmethod
    def get_today_events():
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
        today_events = Interface.calendar.get_events_in_range(start_of_day, end_of_day)
        print(f'События на сегодня:')
        for event in today_events:
            print(event)
        Interface.func_request.append(Interface.main_menu)


    @staticmethod
    def show_calendar():
        # Текущий год и месяц
        year = datetime.now().year
        month = datetime.now().month

        # Создаем текстовый календарь
        cal = calendar.TextCalendar(calendar.MONDAY)

        # Печатаем календарь на текущий месяц
        cal_str = cal.formatmonth(year, month)
        print(cal_str)
        Interface.func_request.append(Interface.main_menu)



    @staticmethod
    def create_event():
        title = input("Введите название события: ")
        def input_with_validation(prompt, validation_func):
            while True:
                user_input = input(prompt)
                try:
                    return validation_func(user_input)
                except Exception as e:
                    print(f'Ошибка: {str(e)}')


        while True:
            start_time = input_with_validation("Введите время начала события в формате dd.mm.yyyy hh:mm: ", Interface.backend.validate_date_format)
            end_time = input_with_validation("Введите время окончания события в формате dd.mm.yyyy hh:mm: ",
                                           Interface.backend.validate_date_format)
            try:
                Interface.backend.compare_dates(start_time, end_time)
                break
            except Exception as e:
                print(f'Ошибка: {str(e)}')

        recurrence = input_with_validation("Введите частоту повторений событий (0: никогда, 1: каждый день, 2: каждую неделю, 3: каждый месяц, 4: каждый год): ",
            Interface.backend.validate_recurrence)
        description = input("Введите описание события или оставьте поле пустым: ")
        organizer = Interface.logged_in_user.username
        new_event = Event(title, start_time, end_time, description, recurrence=recurrence, organizer=organizer)
        Interface.calendar.add_event(new_event)
        print('Событие успешно создано и добавлено в Ваш календарь.')
        while True:
            user_input = input_with_validation("Если хотите пригласить участников на мероприятие, введите их имена пользователей через пробел, в противном случае оставьте поле пустым",
                                           Interface.backend.validate_participants)
            if user_input is None:
                break
            try:
                Interface.backend.invite_participants(Interface.logged_in_user.username, new_event, user_input)
                break
            except Exception as e:
                print(f'Ошибка: {str(e)}')
        Interface.backend.save_calendar_data()

        sleep(1)
        Interface.func_request.append(Interface.main_menu)
    @staticmethod
    def delete_event():
        pass

    @staticmethod
    def add_paticipants():
        pass
    #     try:
    #
    #     except Exception as e:
    #         print(f'Ошибка: {str(e)}')


    @staticmethod
    def get_coming_events():
        coming_events = Interface.calendar.get_coming_events()
        if coming_events:
            print('Предстоящие события:')
            for date, events in coming_events.items():
                print()
                print(date)
                for event in sorted(events, key=lambda x: x.start_time):
                    print(f'{event.start_time.strftime("%H:%M")} - {event.end_time.strftime("%H:%M")}: {event.title}')
        else:
            print('У вас нет событий на ближайшую неделю.')

    @staticmethod
    def get_events_in_range():
        start_date = input("Введите начало интервала в формате dd.mm.yyyy hh:mm: ")
        end_date = input("Введите конец интервала в формате dd.mm.yyyy hh:mm: ")
        print(Interface.calendar.get_events_in_range(Event.formate_date(start_date), Event.formate_date(end_date)))
        Interface.func_request.append(Interface.main_menu)

    @staticmethod
    def logout():
        logout_confirmation = input('Вы действительно хотите выйти? (да/нет): ').lower()
        if logout_confirmation == 'да':
            Interface.logged_in_user = None
            Interface.func_request.append(Interface.start)
        elif logout_confirmation == 'нет':
            Interface.logged_in_user = None
            Interface.func_request.append(Interface.main_menu)
        else:
            print('Введите корректный ответ')
            Interface.func_request.append(Interface.logout)

    @staticmethod
    def show_all_event():
        all_events = Interface.backend.calendars[Interface.logged_in_user.username].events
        for i, event in enumerate(all_events, 1):
            print(i, event)
        user_input = input('Введите номер события, которые хотите изменить.')
        participants = input('Введите участников, которых хотите удалить.')
        Interface.backend.remove_participant(Interface.logged_in_user.username, all_events[int(user_input)], Interface.backend.validate_participants(participants))
        Interface.backend.save_calendar_data()
        Interface.backend.save_user_data()


Interface.work()
