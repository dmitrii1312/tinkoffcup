from dataclasses import dataclass
from datetime import datetime
import time


# тайм зоны беда, сдвиг на два часа + таймзону в конфиг
@dataclass
class TypeOfWork:
    start_time: datetime  # Начало работ дата + время
    end_time: datetime  # Конец работ, только время
    duration_time: datetime.time()  # Продолжительность работ
    deadline_time: datetime # крайний срок для работ
    priority: str  # Приоритет работ critical or normal
    zone_name: str # название зоны
    work_type: str # тип работ


"""
Methods:
1) Работы попадают в окно из белого списка?
Написать проверку попадания в окно

2) Длительность работ
Метод проверки длительности работ
должен проверить:
duration >= minimal_time
duration < maximal_time

3) Метод проверки передаваемого времени со всеми запланированными работами, т.е
start_dateTime + end_time = delta
Метод проверяет delta - true или false
+ 
вопрос: У нас  минимальное время и максимальное это константы?
"""
    def __init__(self, work_type):
        self.work_type = work_type
        self.duration = -1;

    def check_duration_job(self, min_time=time, max_time=time):
        if self.duration <= min_time.time():
            return False, "Duration is not compatible with minimal time"
        elif self.duration > max_time.time() and max_time.time() != 0:
            return False, "Duration is not compatible with maximum time"
        else:
            return True, "Duration is compatible"

    def set_start_time(self, starttime:datetime):
        now = datetime(now)
        if starttime < now:
            return False, "Can't plan task in the past"
        else:
            self.start_time=starttime
        return True, "OK"

# TODO: Нужно проверить, что максимальное время не равно 0, так же нужно придумать значение, которое будет считаться некорректным(устанавливаться в случае некорректного значения длительности)
    def set_duration(self, duration:datetime, min_time: time, max_time: time):
        self.duration_time = duration
        res, text = check_duration_job(self, min_time, max_time)
        if res:
            return True, text
        else:
            self.duration_time = -1;
            return False, text


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

    def set_priority(self, priority: str):
        self.priority = priority
        return True, "OK"

