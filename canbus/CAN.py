from .internal import (
    CAN,
    CAN_CLOCK,
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
    CAN_SPEED,
    ERROR,
)

from .internal import SPIPICO as SPI
from .internal import CANFrame

class CanError:
    ERROR_OK = ERROR.ERROR_OK
    ERROR_FAIL = ERROR.ERROR_FAIL

    # Decodes contents of various MCP2015 status registers
    # Returns blank-delimited string, one for each keyword-value,
    #    e.g. for 3 keywords:
    #       {status_reg_flags} {interrupt_reg_flags} {error_reg_flags}
    #    e.g. for 2 keywords (status= and error=):
    #       {status_reg_flags} {error_reg_flags}
    #    e.g. for 1 keyword (interrupt=):
    #       {interrupt_reg_flags}
    # txctl: TXBnCTRL

    @classmethod
    def decode(cls,status=None,interrupt=None,error=None,txctl=None):

       def cat(txt):
          nonlocal pfx
          res, pfx = pfx + txt, ','
          return res

       res, nxt, pfx = '', '', ''
       if status is not None:
          res += '{'
          bits = status & 0xe0
          if bits == 0x00: res += cat('Normal-mode')
          if bits == 0x20: res += cat('Sleep-mode')
          if bits == 0x40: res += cat('Loopback-mode')
          if bits == 0x60: res += cat('Listen-only-mode')
          if bits == 0x80: res += cat('Config-mode')
          bits = status & 0x0e
          if bits == 0x00: res += cat('No-interrupt')
          if bits == 0x02: res += cat('Error-interrupt')
          if bits == 0x04: res += cat('Wake-up-interrupt')
          if bits == 0x06: res += cat('TXB0-interrupt')
          if bits == 0x08: res += cat('TXB1-interrupt')
          if bits == 0x0a: res += cat('TXB2-interrupt')
          if bits == 0x0c: res += cat('RXB0-interrupt')
          if bits == 0x0e: res += cat('RXB1-interrupt')
          res += '}'
          nxt = ' '

       if txctl is not None:
          res += nxt + '{'
          pfx = ''
          if txctl & 0x80: res += cat('<unknown>')
          if txctl & 0x40: res += cat('Msg-abort')
          if txctl & 0x20: res += cat('Msg-lostarb')
          if txctl & 0x10: res += cat('Msg-xmt-error')
          if txctl & 0x08: res += cat('Msg-xmt-req')
          if txctl & 0x04: res += cat('<unknown>')
          if txctl & 0x02: res += cat('Msg-prio1')
          if txctl & 0x01: res += cat('Msg-prio0')
          res += '}'

       if interrupt is not None:
          res += nxt + '{'
          pfx = ''
          if interrupt & 0x80: res += cat('Message-error')
          if interrupt & 0x40: res += cat('Wake-up')
          if interrupt & 0x20: res += cat('Error')
          if interrupt & 0x10: res += cat('Xmtbuf2-empty')
          if interrupt & 0x08: res += cat('Xmtbuf1-empty')
          if interrupt & 0x04: res += cat('Xmtbuf0-empty')
          if interrupt & 0x02: res += cat('Rcvbuf1-full')
          if interrupt & 0x02: res += cat('Rcvbuf0-full')
          res += '}'
          nxt = ' '

       if error is not None:
          res += nxt + '{'
          pfx = ''
          if error & 0x80: res += cat('Rcvbuf1-overflow')
          if error & 0x40: res += cat('Rcvbuf0-overflow')
          if error & 0x20: res += cat('Bus-off')
          if error & 0x10: res += cat('Xmterror-pasv')
          if error & 0x08: res += cat('Rcverror-pasv')
          if error & 0x04: res += cat('Xmterror-warn')
          if error & 0x02: res += cat('Rcverror-warn')
          if error & 0x01: res += cat('Error-warn')
          res += '}'

       return res
          

class CanMsgFlag:
    RTR = CAN_ERR_FLAG
    EFF = CAN_EFF_FLAG

class CanMsg:
    def __init__(self, can_id = 0, data = None, flags = None):
        if flags:
            self.frame = CANFrame(can_id | flags, data)
        else:
            self.frame = CANFrame(can_id, data)
        self.is_remote_frame = self.frame.is_remote_frame
        self.is_extended_id = self.frame.is_extended_id
        self.can_id = self.frame.arbitration_id
        self.data = self.frame.data
        self.dlc = self.frame.dlc
    def _set_frame(self, frame):
        self.frame = frame
        self.is_remote_frame = self.frame.is_remote_frame
        self.is_extended_id = self.frame.is_extended_id
        self.can_id = self.frame.arbitration_id
        self.data = self.frame.data
        self.dlc = self.frame.dlc
    def _get_frame(self):
        return self.frame

class CAN_1:
    ERROR = ERROR
    def __init__(self, board: str = "CANBed_RP2040", spi: int = 0, spics: int = 9):
        self.can = CAN(SPI(cs=spics))
    def begin(self, bitrate: int = CAN_SPEED.CAN_500KBPS, canclock: int = CAN_CLOCK.MCP_16MHZ, mode: str = 'normal'):
        ret = self.can.reset()
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.can.setBitrate(bitrate, canclock)
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.can.setNormalMode()
        return ret
    def setLoopback(self):
        return self.can.setLoopbackMode()
    def clearInterrupts(self):
        self.can.clearInterrupts()
    def getInterrupts(self):
        return self.can.getInterrupts()
    def getInterruptMask(self):
        return self.can.getInterruptMask()
    def getErrorFlags(self):
        return self.can.getErrorFlags()
    def clearErrorFlags(self, RXERR=False, MERR=False):
        # Keyword args for clearing more conditions in future if required, e.g.
        # TXBO, passive errors, warnings
        if RXERR: self.can.clearRXnOVRFlags()
        if MERR: self.can.clearMERR()
    def getStatus(self):
        return self.can.getStatus()
    def init_mask(self, mask, is_ext_id, mask_id):
        ret = self.can.setFilterMask(mask + 1, is_ext_id, mask_id)
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.can.setNormalMode()
        return ret
    def init_filter(self, ft, is_ext_id, filter_id):
        ret = self.can.setFilter(ft, is_ext_id, filter_id)
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.can.setNormalMode()
        return ret
    def checkReceive(self):
        return self.can.checkReceive()
    def recv(self):
        error, frame = self.can.readMessage()
        msg = CanMsg()
        if frame is not None: msg._set_frame(frame)
        return error, msg
    def recvinto(self,msg):
        frame = msg._get_frame()
        error = self.can.readMessageInto(frame)
        msg._set_frame(frame)
        return error
    def send(self, msg):
        frame = msg._get_frame()
        error = self.can.sendMessage(frame)
        return error
