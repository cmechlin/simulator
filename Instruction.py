from abc import ABC, abstractmethod, abstractproperty


class Instruction(ABC):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.name}: {hex(self.id_bytes)}"

    @abstractproperty
    def id_bytes(self) -> int:
        return None

    @abstractproperty
    def name(self) -> str:
        return "Undefined"

    @abstractproperty
    def length(self) -> int:
        return 2

    @abstractmethod
    def execute(self) -> None:
        print(self.__str__())


class JIT_Instruction(Instruction):
    name = "JIT"
    id_bytes = 0xF000
    length = 4

    def execute(self):
        super().execute()


class JIF_Instruction(Instruction):
    name = "JIF"
    id_bytes = 0x6000
    length = 4

    def execute(self):
        super().execute()


class WRT_Instruction(Instruction):
    name = "WRT"
    id_bytes = 0x3000
    length = 3

    def execute(self):
        super().execute()


class WRF_Instruction(Instruction):
    name = "WRF"
    id_bytes = 0xA000
    length = 3

    def execute(self):
        super().execute()


class JMP_Instruction(Instruction):
    name = "JMP"
    id_bytes = 0x5000
    length = 3

    def execute(self):
        super().execute()


class TMR_Instruction(Instruction):
    name = "TMR"
    id_bytes = 0x9000
    length = 4

    def execute(self):
        super().execute()


class SLB_Instruction(Instruction):
    name = "SLB"
    id_bytes = 0xC000
    length = 2

    def execute(self):
        super().execute()
