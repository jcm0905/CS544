from typing import Dict
from ft_quic import FTQuicConnection, QuicStreamEvent
import pdu
import asyncio
import hashlib # library used for checksum using SHA-256 hashing
import base64 # library used for encoding/decoding file chunks during transfer
from utils import calculate_checksum

# This function represents file transfer from the client side
async def ft_client_proto(scope:Dict, conn:FTQuicConnection, filename: str):
    print("[cli] Starting File Transfer...")
    new_stream_id = conn.new_stream()

    # Send the START PDU of the file message to the server
    START_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_START, filename, filename=filename)
    START_quic_stream = QuicStreamEvent(new_stream_id, START_datagram.to_framed_bytes(), False)
    await conn.send(START_quic_stream)
    print(f"[cli] Sent START of file: {filename}")

    # Begin reading the contents of the file and send file data in chunks
    try:
        sequence_number = 0
        with open(filename, "rb") as f:
            while True:
                file_chunk = f.read(4096) # Read file contents in 4KB chunks
                if not file_chunk:
                    break
                encoded_chunk_str = base64.b64encode(file_chunk).decode("ascii") # convert binary bytes to ASCII using Base64
                chunk_checksum = hashlib.sha256(file_chunk).hexdigest() # get checksum value in hexidecimal
                DATA_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_DATA, encoded_chunk_str, filename=filename, checksum=chunk_checksum, sequence=sequence_number)
                DATA_quic_stream = QuicStreamEvent(new_stream_id, DATA_datagram.to_framed_bytes(), False)
                await conn.send(DATA_quic_stream)
                print(f"[cli] Sent File Data Chunk of Size: {len(file_chunk)}, Checksum: {chunk_checksum[:8]}, Seq #: {sequence_number}")
                sequence_number += 1
                await asyncio.sleep(0.01) # delay slightly to avoid overloading
        
        # Send END PDU of the file and Calculate the Overall Checksum
        overall_checksum = await calculate_checksum(filename)
        END_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_END, "Ending File Transmission", filename=filename, checksum=overall_checksum)
        END_quic_steam = QuicStreamEvent(new_stream_id, END_datagram.to_framed_bytes(), True) # End QUIC stream
        await conn.send(END_quic_steam)
        print(f"[cli] Sent END of File With Overall Checksum: {overall_checksum[:8]}")

        # Wait for ACK from server to complete file transfer
        ACK_event: QuicStreamEvent = await asyncio.wait_for(conn.receive(), timeout=5) # Timeout after 5 seconds
        ACK_datagram = pdu.Datagram.from_bytes(ACK_event.data)
        if ACK_datagram.mtype == pdu.MSG_TYPE_FILE_ACK and ACK_datagram.msg == "File Transfer Successful (Checksum Verified)":
            print("[cli] Received File Transfer Acknowledgement: Successful Checksum Verification")
        elif ACK_datagram.mtype == pdu.MSG_TYPE_FILE_ACK and ACK_datagram.msg == "File Transfer Failed (Checksum Mismatch)":
            print("[cli] Received File Transfer Acknowledgement: Checksum Mismatch")
        elif ACK_datagram.mtype == pdu.MSG_TYPE_FILE_ACK:
            print("[cli] Received File Transfer Acknowledgement")
        else:
            print(f"[cli] Received Unexpected Message Type: {ACK_datagram.mtype}, Expected File ACK")
    # Error messages sent to server if file transfer fails
    except FileNotFoundError:
        print(f"[cli] Error: {filename} not found!")
    except:
        print("[cli] File Transfer Failed! ")
    
    print("[cli] Ending File Transfer...")
