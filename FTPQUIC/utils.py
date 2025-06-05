"""
This Python file houses helper functions for the client and server
"""

import hashlib
import pdu
from ft_quic import QuicStreamEvent

# This function calculates the checksum of the entire file and returns it as a hexadecimal string
async def calculate_checksum(file):
    hash = hashlib.sha256()
    # Read file chunks and hash them for the checksum
    try:
        with open(file, "rb") as f:
            while file_chunk := f.read(4096):
                hash.update(file_chunk)
        return hash.hexdigest()
    except Exception as e:
        return f"File Error: {e}"
    
# This function helps read and parse a framed datagram
async def read_framed_datagram(conn):
    buffer = b'' # empty byte string
    while True:
        event: QuicStreamEvent = await conn.receive()
        buffer += event.data
        datagram, remaining = pdu.Datagram.from_framed_bytes(buffer)
        if datagram:
            return datagram, event.stream_id
        buffer = remaining # Wait for more data
