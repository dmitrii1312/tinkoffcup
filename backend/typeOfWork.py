from dataclasses import dataclass
from datetime import datetime
import time


# тайм зоны беда, сдвиг на два часа + таймзону в конфиг
@dataclass
class TypeOfWork:
    start_dateTime: datetime  # Начало работ дата + время
    end_time: datetime  # Конец работ, только время
    priority: str  # Приоритет работ critical or normal
    inWhiteList: bool  # True - попадаем в белый список
    duration: datetime.time()  # Продолжительность работ


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


    def duration_job(self, min_time=time, max_time=time):
        if self.duration <= min_time.time():
            return False, "Duration is not compatible with minimal time"
        elif self.duration > max_time.time():
            return False, "Duration is not compatible with maximum time"
        else:
            return True, "Duration is compatible"