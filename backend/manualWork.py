from dataclasses import dataclass
from typeOfWork import typeOfWork


@dataclass
class manualWork(typeOfWork):
    compress: int  # cтепень сжатия работ

    def set_priority(self, priority):
        super().set_priority(priority)
        return True

    def get_priority(self):
        return super().get_priority()
