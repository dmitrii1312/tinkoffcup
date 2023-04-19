from dataclasses import dataclass
from datetime import datetime


# тайм зоны беда, сдвиг на два часа + таймзону в конфиг
@dataclass
class typeOfWork:
    start_dateTime: datetime  # Начало работ дата + время
    end_time: datetime  # Конец работ, только время
    priority: str  # Приоритет работ critical or normal
    inWhiteList: bool # True - попадаем в белый список
    duration: datetime # Продолжительность работ

