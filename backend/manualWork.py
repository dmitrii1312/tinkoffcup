from dataclasses import dataclass
from datetime import datetime
import time
import TypeOfWork

@dataclass
class manualWork(TypeOfWork):
    compress: int # cтепень сжатия работ

    def set_priority(self, priority):
        super().set_priority(priority)
        return True

    def get_priority(self):
        return super().get_priority()

