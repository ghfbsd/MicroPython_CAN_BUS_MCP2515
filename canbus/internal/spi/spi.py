try:
    from typing import Any, Optional
except ImportError:
    pass

import sys
import time

try:
    from pyb import Pin
except ImportError:
    from machine import Pin

from . import SPI_DEFAULT_BAUDRATE, SPI_DUMMY_INT, SPI_TRANSFER_LEN, SPI_HOLD_US


class SPI:
    def __init__(self, cs: int, baudrate: int = SPI_DEFAULT_BAUDRATE) -> None:
        # Somehow the self.init() call invokes the machine.SPI .init() method?!
        self._SPICS = Pin(cs, Pin.OUT)
        self._SPI = self.init(baudrate=baudrate)  # type: Any
        self.end()

    def init(self, baudrate: int) -> Any:
        raise NotImplementedError

    def start(self) -> None:
        self._SPICS.value(0)
    ### time.sleep_us(SPI_HOLD_US)  # type: ignore # MCP2515 spec = 50 ns not us

    def end(self) -> None:
        self._SPICS.value(1)
    ### time.sleep_us(SPI_HOLD_US)  # type: ignore # MCP2515 spec = 50 ns not us

    def transfer(self,
        value: int = SPI_DUMMY_INT,
        read: bool = False,
        val: bytes = bytearray(SPI_TRANSFER_LEN),
        buf: bytes = bytearray(SPI_TRANSFER_LEN)
    ) -> Optional[int]:
        """Write int value to SPI and read SPI as int value simultaneously.
        This method supports transfer single byte only,
        and the system byte order doesn't matter because of that. The input and
        output int value are unsigned.
        val, buf used for static allocation so no changes to heap
        """
        val = value.to_bytes(SPI_TRANSFER_LEN, sys.byteorder)

        if read:
            self._SPI.write_readinto(val, buf)
            return int(buf[0])
        self._SPI.write(val)
        return None
