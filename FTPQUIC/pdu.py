import json
import struct # library used for interpreting bytes as binary data

MSG_TYPE_DATA = 0x00
MSG_TYPE_ACK  = 0x01
MSG_TYPE_DATA_ACK = MSG_TYPE_DATA | MSG_TYPE_ACK

# PDU Message Types for FTP
MSG_TYPE_FILE_START = 0x02
MSG_TYPE_FILE_DATA = 0x03
MSG_TYPE_FILE_END = 0x04
MSG_TYPE_FILE_ACK = 0x05

# Constant for the length prefix for the framed message
LENGTH_PREFIX_SIZE = 4

# Updated class to include filename, checksum, and sequence number as fields
class Datagram:
    def __init__(self, mtype: int, msg: str, size:int = 0, filename: str = None, checksum: str = None, sequence: int = 0):
        self.mtype = mtype
        self.msg = msg
        self.size = len(self.msg)
        self.filename = filename
        self.checksum = checksum
        self.sequence = sequence
        
    def to_json(self):
        return json.dumps(self.__dict__)    
    
    @staticmethod
    def from_json(json_str):
        return Datagram(**json.loads(json_str))
    
    def to_bytes(self):
        return json.dumps(self.__dict__).encode('utf-8')
    
    @staticmethod
    def from_bytes(json_bytes):
        return Datagram(**json.loads(json_bytes.decode('utf-8')))
    
    """
    This function will add a 4-byte length header prefix before the message
    Format:
    [4-byte length] [message data]
    """
    def to_framed_bytes(self):
        raw = self.to_bytes()
        return struct.pack(">I", len(raw)) + raw # Prepend with 4-byte length prefix (big-endian)
    
    # This function will extract a datagram from a byte buffer with a 4-byte prefix, which stores framed datagrams
    @staticmethod
    def from_framed_bytes(buffer: bytes):
        if len(buffer) < LENGTH_PREFIX_SIZE:
            return None, buffer # Incomplete Header
        
        length = struct.unpack(">I", buffer[:LENGTH_PREFIX_SIZE])[0] # Find out how many bytes the datagram uses
        
        if len(buffer) < LENGTH_PREFIX_SIZE + length:
            return None, buffer # Incomplete Payload
        
        datagram_bytes = buffer[LENGTH_PREFIX_SIZE:LENGTH_PREFIX_SIZE + length]
        remaining = buffer[LENGTH_PREFIX_SIZE + length:]
        return Datagram.from_bytes(datagram_bytes), remaining # Deserialize datagram and return it with the remaining buffer
