"""
    C. Mechling
"""
import os
# import BinaryReader
from struct import *
from pathlib import Path
from enum import Enum
import mmap


class HeaderTypes(Enum):
    END = 0x0000
    VPM2_APP = 0x0001
    EQUATIONS_CFG = 0x0002
    RECORD_TABLE_CFG = 0x0004
    TIMER_CFG = 0x0008
    VITAL_CONFIG_SETTINGS_CFG = 0x0010
    CHASSIS_CFG = 0x0020
    TWO_WIRE_INPUT_CFG = 0x0040
    TWO_WIRE_OUTPUT_CFG = 0x0080
    LAMP_VLDC6S_CFG = 0x0100
    NVIO_CFG = 0x0200
    NSM_CFG = 0x0350
    TRACK_CODE_SELECT_INPUT_CFG = 0x0400
    ISLAND_CFG = 0x0700
    TRACK_CODE_SELECT_OUTPUT_CFG = 0x0800
    APPROACH_CFG = 0x0900
    CAB_OUTPUT_CFG = 0x1000
    GFD_CFG = 0x1818
    TRACK_INPUT_CFG = 0x2000
    TRACK_OUTPUT_CFG = 0x4000
    IXC_CFG = 0x5000
    CHASSIS_SSR_CFG = 0x7000
    OFFICE_PORT_PRIMARY_CFG = 0x8000
    OFFICE_PORT_DUAL_CFG = 0x8003
    BATTERY_CFG = 0x8005
    TEMP_CFG = 0x8006
    LAMP_VLDR16S_CFG = 0xA000
    WCM_APP_CFG = 0xA001
    WCM_NONVITAL_APP_CFG = 0xA002
    GPS_APP_CFG = 0xA004
    GPS_NONVITAL_APP_CFG = 0xA008
    VSSR_CFG = 0xA100
    LAMP_VLDR8AC_CFG = 0xB000
    VSSR_VLDR8AC_CFG = 0xB100
    IXS_VPM3_VITAL_APP = 0xFF01
    IXS_VPM3_NON_VITAL_APP = 0xFF02
    APPLICATION_ID_INPUTS_CFG = 0xFF13
    ETHERNET_SETTING_CFG = 0xFF14
    TELNET_SETTING_CFG = 0xFF17
    HAWK_CFG = 0xFF1F
    LCP_CFG = 0xFF2F
    PMD4_VPM3_VITAL_APP = 0xFF31
    PMD4_VPM3_NONVITAL_APP = 0xFF32
    MULTI_APP = 0xFFF1
    CHASSIS_ID_INPUTS_CFG = 0xFFFD
    VCOM_CFG = 0xFFFE


class InstructionTypes(Enum):
    JIT = 1
    JIF = 2
    TMR = 3
    JMP = 4
    WRT = 5
    WRF = 6
    SLB = 7
    END = 0
    UNKNOWN = 99


class VitalInstructionSignatures(Enum):
    JIT = 0x22483011
    JIF = 0x2448
    TMR = 0x22482448
    JMP = 0x6000
    WRT = 0x2848
    WRF = 0x2A48
    SLB = 0x5282
    END = 0x0000


class StatusTypes(Enum):
    INPUT = 0x0
    OUTPUT = 0x1
    INTERNAL = 0x2
    NOT_USED = 0x3


class BinaryReader:
    def __init__(self, filepath=None, bigEndian=False, signed=False):
        self.posMark = 0
        # is LE little-endian, BE big-endian
        self.endianess = "<" if bigEndian else ">"
        self.signed = signed
        if filepath:
            with open(filepath, "rb") as f:
                self.mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
                self.marker = 0

    def close(self):
        self.mm.close()

    def read(self, pattern="", raw=False):
        if len(pattern) == 0:
            return
        pattern = self._decode_pattern(pattern)
        size = self._get_size(pattern)
        self.start = self.mm.tell()
        self.end = self.mm.tell() + size
        if raw:
            pat = ">"
            sz = int(size / 2)
            pat = pat + "H" * sz
            print(f"Raw {list(map(hex,unpack(pat, (self.mm.read(size)))))}")
            self.jump(-size)
        struct = Struct(self.endianess + pattern)
        if len(pattern.replace("x", "")) == 1:
            return struct.unpack(self.mm.read(size))[0]
        else:
            return struct.unpack(self.mm.read(size))

    def read_multi(self, fields, totalsize):
        result = []
        self.start = self.mm.tell()
        self.end = self.mm.tell() + totalsize
        for offset, size in fields:
            if size == 1:
                pattern = "b"
            elif size == 2:
                pattern = "h"
            elif size == 4:
                pattern = "i"
            elif size == 8:
                pattern = "q"
            else:
                return None
            pattern = self._decode_pattern(pattern)
            self.jump(offset)
            result.append(unpack(pattern, self.mm.read(size))[0])
        self.jump(self.end, False)
        return result

    def peek(self, pattern="", offset=0, relative=True):
        if len(pattern) != 1:
            return
        size = self._get_size(pattern)
        pattern = self._decode_pattern(pattern)
        if offset > 0:
            self.jump(offset, relative)
        result = unpack(self.endianess + pattern, self.mm.read(size))[0]
        self.jump(-size - offset)
        return result

    def read_string(self, size):
        if size < 1:
            return
        self.start = self.mm.tell()
        self.end = self.mm.tell() + size
        str = self.mm.read(size).decode("utf-8")
        return str[: str.find("\x00")]

    def jump(self, offset, relative=True):
        if relative:
            self.mm.seek(offset, os.SEEK_CUR)
        else:
            self.mm.seek(offset, os.SEEK_SET)

    def _decode_pattern(self, str):
        result = ""
        count = ""
        for c in str.lower():
            if c.isnumeric():
                count = count + c
            else:
                if len(count) == 0:
                    count = 1
                else:
                    count = int(count)

                if c == "b" or c == "h" or c == "i" or c == "q":
                    if not self.signed:
                        c = c.upper()
                    result = result + c * count
                elif c == "x":
                    result = result + c * count
                else:
                    print(f"Unrecognized character {c} in pattern")
                count = ""
        return result

    def _get_size(self, str):
        size = 0
        for c in str.lower():
            if c == "b" or c == "x":
                size = size + 1
            elif c == "h":
                size = size + 2
            elif c == "i" or c == "l":
                size = size + 4
            elif c == "q":
                size = size + 8
        return size

    def mark(self):
        self.start = self.mm.tell()

    def position(self, relative=False):
        if relative:
            return self.mm.tell() - self.start
        else:
            return self.mm.tell()

    def size(self):
        return self.mm.size()


class EpromReader:
    def __init__(self, filepath=None):
        if not Path(filepath).exists():
            print(f"Path {filepath} does not exist")
            return
        self.equations = []
        self.statuses = []
        self.instructions = []
        br = BinaryReader(filepath)
        self.ParseFile(br)
        br.close()
        pass

    def ParseFile(self, br):
        self.ApplicationHeader = App_Structure(br)
        while br.position() < br.size():
            header = self.getHeader(br)
            if header.name == "END":
                break
            self.getBody(br, header)

    def getHeader(self, br):
        return Header(br)

    def getBody(self, br, header):
        if header.name == "EQUATIONS_CFG" and header.length == 0:
            body = globals()[header.name](br, self.statuses)
            self.instructions = body.instructions
            self.equations = body.equations
            br.jump(br.end, False)
        elif header.name == "RECORD_TABLE_CFG":
            body = globals()[header.name](br)
            self.statuses = body.statuses
            # print(self.statuses[35].name)
        else:
            br.jump(header.length)


class Header:
    def __init__(self, br):
        self.crc, lsb_length, self.type, self.rev, msb_length = br.read("ihhbb")
        self.length = (msb_length << 16) + lsb_length
        try:
            self.name = HeaderTypes(self.type).name
        except:
            self.name = "Unknown"


class App_Structure:
    def __init__(self, br):
        self.revtext = br.read_string(1024)
        self.header = Header(br)
        self.appSize = self.header.length
        self.crc, self.length, self.chassisid = br.read("iibx")


class Generic_Structure:
    def __init__(self, data, root):
        self.data = data

    def read(self, root):
        self.header = Header(self.data)
        # print(f"Type: {self.header.name} [{self.header.type}] Rev: {self.header.rev}")
        # TODO: fix this. this is when it reaches the equations
        s_size = self.header.length
        if self.header.name == "RECORD_TABLE_CFG":
            self.payload = globals()[self.header.name](self.data, root)  # RECORD_TABLE_CFG(data, root)
        elif self.header.name == "EQUATIONS_CFG":
            self.payload = globals()[self.header.name](self.data, root)
        #  self.payload
        else:
            self.payload = self.data.read(s_size)
            return None
        self.totalsize = self.data.tell()


# Record Table Structure 0x0004 Rev 1
class RECORD_TABLE_CFG:
    def __init__(self, br):
        number_rows, self.number_statuses = br.read("hh")
        self.statuses = []
        for row in range(number_rows):
            RecordTable_RowInfo_Structure(br, self.statuses)


# Record Table - Row Info Structure Rev 1
class RecordTable_RowInfo_Structure:
    def __init__(self, br, statuses):
        offset, number_cols = br.read("hh")
        for col in range(number_cols):
            index = int(offset / 2 + col)
            RecordTable_ColInfo_Structure(br, index, statuses)


# Record Table - Column Info Structure Rev 1
class RecordTable_ColInfo_Structure:
    def __init__(self, br, index, statuses):
        name = br.read_string(12)
        flags, type = br.read("bb")
        shared = bool(flags & 0x1)
        recorded = bool(flags & 0x2)
        type = type
        if type != 0x3:
            statuses.append(Status(index, name, type, shared, recorded))
        else:
            statuses.append(None)


class Status:
    def __init__(self, index, name, type, shared, recorded):
        self.index = index
        self.name = name
        self.typecode = type
        self.type = StatusTypes(type).name
        self.shared = shared
        self.recorded = recorded
        self.state = False
        # print(f"Name: {self.name} Type: {self.type} Index: {self.index}")

    def __change_state__(self, state):
        if self.state != state:
            self.state = state
            print(f"Status {self.name} state changed to {self.state}")
        else:
            print(f"Status {self.name} state already {state}")

    def getState(self):
        # print(f"{self.type}: Status {self.name} state is {self.state}")
        return self.state

    def setState(self, state):
        if self.type != "INPUT":
            raise Exception(f"You are trying to set the state on status {self.name}, which is not an input!")
        self.state = state
        print(f"Status {self.name} state changed to {self.state}")


# Equations Structure 0x0002 Rev 2
# IXS VPM-3 Vital and Non Vital Applications, Coldfire Op Codes
class EQUATIONS_CFG:
    def __init__(self, br, statuses):
        max_stability, equation_type, number_equations, length = br.read("bbhi")
        self.max_stability = max_stability
        self.equation_type = equation_type
        self.number_equations = number_equations
        # self.start = data.tell()
        # self.end = data.tell() + self.length
        self.instructions = []
        self.equations = []
        br.mark()
        equation = Equation()
        WRTFound = False
        WRFFound = False
        SLBFound = False

        for instruction in InstructionIterator(br, length, statuses):
            equation.add(instruction)
            self.instructions.append(instruction)
            WRTFound |= instruction.type == InstructionTypes.WRT
            WRFFound |= instruction.type == InstructionTypes.WRF
            SLBFound |= instruction.type == InstructionTypes.SLB
            if WRTFound and WRFFound:
                equation.setLast()
                self.equations.append(equation)
                equation = Equation()
                WRTFound = False
                WRFFound = False
            

    def readInstruction(self, br):
        magic = br.peek("h")
        if magic == 0x2248:
            move = br.peek("h", 8)
            if move == 0x3011:
                # JIT
                return VitalJIT(br)
            elif move == 0x2448:
                # Timer
                return VitalTMR(br)
        elif magic == 0x2448:
            # JIF
            return VitalJIF(br)
        elif magic == 0x2A48:
            # WRF
            self.WRFFound = True
            return VitalWRF(br)
        elif magic == 0x2848:
            # WRT
            self.WRTFound = True
            return VitalWRT(br)
        elif magic == 0x5282:
            # SLB
            return VitalSLB(br)
        elif magic == 0x6000:
            # JMP
            return VitalJMP(br)
        elif magic == 0x0000:
            return "END"
        else:
            print("unknown instruction")
            return None

    def getData(self):
        pass


class InstructionIterator:
    def __init__(self, br, length, statuses):
        self.br = br
        self.length = length
        self.statuses = statuses

    def __iter__(self):
        return self

    def __next__(self):
        type = self.getType()

        if type == InstructionTypes.END or self.br.position(True) >= self.length:
            raise StopIteration

        data = self.getData(type)
        instruction = Instruction(type, data, self.statuses)
        return instruction

    def getType(self):
        magic = self.br.peek("h")
        if magic == 0x2248:
            move = self.br.peek("h", 8)
            if move == 0x3011:  # JIT
                return InstructionTypes.JIT
            elif move == 0x2448:  # TMR
                return InstructionTypes.TMR
        elif magic == 0x2448:  # JIF
            return InstructionTypes.JIF
        elif magic == 0x2A48:  # WRF
            return InstructionTypes.WRF
        elif magic == 0x2848:  # WRT
            return InstructionTypes.WRT
        elif magic == 0x5282:  # SLB
            return InstructionTypes.SLB
        elif magic == 0x6000:  # JMP
            return InstructionTypes.JMP
        elif magic == 0x0000:  # End of Data
            return InstructionTypes.END
        else:
            return InstructionTypes.UNKNOWN

    def getData(self, type):
        if type == InstructionTypes.JIT:
            return VitalJIT(self.br)
        elif type == InstructionTypes.TMR:
            return VitalTMR(self.br)
        elif type == InstructionTypes.JIF:
            return VitalJIF(self.br)
        elif type == InstructionTypes.WRF:
            return VitalWRF(self.br)
        elif type == InstructionTypes.WRT:
            return VitalWRT(self.br)
        elif type == InstructionTypes.SLB:
            return VitalSLB(self.br)
        elif type == InstructionTypes.JMP:
            return VitalJMP(self.br)


class Equation:
    def __init__(self):
        self.instructions = []
        self.IP = 0
        self.size = 0

    def add(self, instruction):
        if instruction.type == InstructionTypes.WRF:
            self.name = instruction.status.name
        l = len(self.instructions)
        if l > 0:
            prev = self.instructions[l-1]
            instruction.offset = prev.offset + prev.size
            instruction.previous = prev
            prev.next = instruction
        elif l == 0:
            self.first = instruction
        self.instructions.append(instruction)

    def setLast(self):
        self.last = self.instructions[len(self.instructions)-1]
        self.size = self.last.offset

    def eval(self):
        for instruction in self.instructions:
            if self.IP != instruction.offset:
                print(f"{self.name}: Instruction {instruction.type} skipped")
                continue
            result = instruction.eval()
            self.IP = self.IP + result
            if result == 999 or self.IP >= self.size:
                self.IP = 0
                print(f"{self.name}: Equation complete")
                break


class Instruction:
    def __init__(self, type, data, statuses):
        self.type = type
        self.next = None
        self.previous = None
        self.size = data.size
        self.offset = 0
        if hasattr(data, "statusIdx"):
            # self.statusIndex = data.statusIdx
            self.status = statuses[data.statusIdx]
        if hasattr(data, "jmpOffset"):
            self.jumpOffset = data.jmpOffset
        if hasattr(data, "enableIdx"):
            # self.enableIndex = data.enableIdx
            self.enableStatus = statuses[data.enableIdx]
        if hasattr(data, "completeIdx"):
            # self.completeIndex = data.completeIdx
            self.completeStatus = statuses[data.completeIdx]

    def eval(self):
        if self.type == InstructionTypes.JIT:
            print(f"JIT: {self.status.name} - {self.status.state}")
            if not self.status.getState():
                return self.offset + self.size
            else:
                return self.offset + self.size + self.jumpOffset
        elif self.type == InstructionTypes.TMR:
            return VitalTMR(self.br)
        elif self.type == InstructionTypes.JIF:
            print(f"JIF: {self.status.name} - {self.status.state}")
            if self.status.getState():
                return self.offset + self.size
            else:
                return self.offset + self.size + self.jumpOffset
        elif self.type == InstructionTypes.WRF:
            self.status.__change_state__(False)
            return self.offset + self.size
        elif self.type == InstructionTypes.WRT:
            self.status.__change_state__(True)
            return self.offset + self.size
        elif self.type == InstructionTypes.SLB:
            return 999
        elif self.type == InstructionTypes.JMP:
            print(f"JMP: {self.jumpOffset}")
            return self.offset + self.size + self.jumpOffset


class VitalJIT:
    def __init__(self, br):
        self.size = 24
        self.type = "JIT"
        statusIdx, jmpOffset = br.read("4xi14xh")
        self.statusIdx = int(statusIdx / 2)
        self.jmpOffset = int(jmpOffset - 2)
        # print(f"JIT: Status {self.statusIdx} Jump {self.jmpOffset}")


class VitalJIF:
    def __init__(self, br):
        self.size = 26
        statusIdx, jmpOffset = br.read("4xi16xh")
        self.statusIdx = int(statusIdx / 2)
        self.jmpOffset = int(jmpOffset - 2)
        # print(f"JIF: Status {self.statusIdx} Jump {self.jmpOffset}")


class VitalTMR:
    def __init__(self, br):
        self.size = 42
        enableIdx, completeIdx = br.read("4xi4xi26x")
        self.enableIdx = int(enableIdx / 2)
        self.completeIdx = int(completeIdx / 2)
        # print(f"TMR: Enable {self.enableIdx} Complete {self.completeIdx}")


class VitalJMP:
    def __init__(self, br):
        self.size = 4
        jmpOffset = br.read("2xh")
        self.jmpOffset = int(jmpOffset - 2)
        # print(f"JMP: Jump {self.jmpOffset}")


class VitalSLB:
    def __init__(self, br):
        self.size = 42
        self.stabilityCount, self.codeLength = br.read("12xh8xi16x")
        # print(f"SLB: Stability Count {self.stabilityCount} Code Length {self.codeLength}")


class VitalWRT:
    def __init__(self, br):
        self.size = 34
        statusIdx = br.read("6xi24x")
        self.statusIdx = int(statusIdx / 2)
        # print(f"WRT: Status {self.statusIdx}")


class VitalWRF:
    def __init__(self, br):
        self.size = 40
        statusIdx = br.read("6xi30x")
        self.statusIdx = int(statusIdx / 2)
        # print(f"WRF: Status {self.statusIdx}")


def main():
    binary = EPROM(".\\simpleappv.b1")

    print(binary.statuses[37].getState())
    binary.statuses[37].setState(True)
    print(binary.statuses[37].getState())

    print(binary.statuses[44].getState())
    # binary.statuses[44].setState(True)
    print(binary.statuses[44].getState())

    print("end")


if __name__ == "__main__":
    main()
