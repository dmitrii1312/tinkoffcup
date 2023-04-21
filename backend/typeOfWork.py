from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
import time

"""
    Methods:
    1) Работы попадают в окно из белого списка?
    Написать проверку попадания в окно

    2) Длительность работ
    Метод проверки длительности работ
    должен проверить:
    duration >= minimal_time
    duration < maximal_time

    3) Метод проверки передаваемого времени со всеми запланированными работами
    т.е
    start_dateTime + end_time = delta
    Метод проверяет delta - true или false
    вопрос: У нас  минимальное время и максимальное это константы?
"""


# тайм зоны беда, сдвиг на два часа + таймзону в конфиг
@dataclass
class typeOfWork:
    start_time: datetime  # Начало работ дата + время
    end_time: datetime  # Конец работ, только время
    duration_time: timedelta  # Продолжительность работ
    deadline_time: datetime  # крайний срок для работ
    priority: str  # Приоритет работ critical or normal
    zone_name: str  # название зоны
    work_type: str  # тип работ
    work_id: str # id работ

    def __init__(self, work_type: str, work_id: str):
        self.work_type = work_type
        self.work_id = work_id
        self.duration = -1

# set methods
    def check_duration_job(self, min_time: timedelta, max_time: timedelta):
        if self.duration_time <= min_time:
            return False, "Duration is not compatible with minimal time"
        elif self.duration_time > max_time and max_time != 0:
            return False, "Duration is not compatible with maximum time"
        else:
            return True, "Duration is compatible"

    def set_start_time(self, starttime: datetime):
        now = datetime.now()
        if starttime < now:
            return False, "Can't plan task in the past"
        else:
            self.start_time = starttime
        return True, "OK"

# TODO: Нужно проверить, что максимальное время не равно 0, так же нужно придумать значение, которое будет считаться некорректным(устанавливаться в случае некорректного значения длительности)
    def set_duration(self, duration: timedelta, min_time: timedelta, max_time: timedelta):
        self.duration_time = duration
        res, text = self.check_duration_job(min_time, max_time)
        if res:
            return True, text
        else:
            self.duration_time = -1
            return False, text

    def set_end_time(self, end_time: datetime):
        self.end_time = end_time
        return True, "OK"

    def calculate_end_time(self):
        end_time = self.start_time + self.duration_time
        return end_time

    def calculate_duration(self):
        duration = self.end_time - self.start_time
        return duration

    def set_deadline(self, deadline: datetime):
        if self.end_time > deadline:
            return False, "Deadline is too early"
        else:
            self.deadline_time = deadline
            return True, "OK"


    def set_summary(self, summary: str):
        self.summary = summary
        return True, "OK"

    def set_priority(self, priority: str):
        self.priority = priority
        return True, "OK"

    def set_zone_name(self, name: str):
        self.zone_name = name
        return True, "OK"

    # Get methods
    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_duration_time(self):
        return self.duration_time

    def get_deadline_time(self):
        return self.deadline_time

    def get_summary(self):
        return self.summary

    def get_priority(self):
        return self.priority

    def get_zone_name(self):
        return self.zone_name

    def get_work_type(self):
        return self.work_type

    def get_work_id(self):
        return self.work_id
