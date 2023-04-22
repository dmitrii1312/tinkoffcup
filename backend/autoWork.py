from dataclasses import dataclass
from typeOfWork import typeOfWork


@dataclass
class autoWork(typeOfWork):
    compress: int  # cтепень сжатия работ

    def set_priority(self, priority):
        if priority == "critical":
            return False, "Can't set this priority to the task of this type"
        else:
            self.priority = priority
        return True
