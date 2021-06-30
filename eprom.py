from struct import *

offset = 0
size = 0


class Eprom:
    def __init__(self, eprom_bytes) -> None:
        self.data_bytes = eprom_bytes  # [offset:] #size]

    def get_byte(self, offset: int) -> int:
        """
        gets byte at given offset
        """
        self.data_bytes.seek(offset)
        return unpack(">B", self.data_bytes.read(1))[0]

    def get_word(self, offset: int) -> int:
        """
        gets word at given offset
        """
        self.data_bytes.seek(offset)
        return unpack(">H", self.data_bytes.read(2))[0]

    def get_quad(self, offset: int) -> int:
        """
        gets quad at given offset
        """
        self.data_bytes.seek(offset)
        return unpack(">I", self.data_bytes.read(4))[0]
