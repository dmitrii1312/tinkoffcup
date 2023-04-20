from dataclasses import dataclass
from datetime import datetime
import time
import TypeOfWork

@dataclass
class AutoWork(TypeOfWork):
    compress: int # cтепень сжатия работ

    def set_priority(self, priority):
        if priority == "critical":
            return False
        else:
            self.priority = priority
        return True

    def get_priority(self):
        return self.priority

