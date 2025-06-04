from typing import Dict
from ft_quic import FTQuicConnection, QuicStreamEvent
import pdu
import os
import hashlib # library used for checksum using SHA-256 hashing
import base64 # library used for encoding/decoding file chunks during transfer
from utils import calculate_checksum, read_framed_datagram

# Create a dictionary to store files received from the client
received_files: Dict[str, bytearray] = {}
SERVER_FILES_DIRECTORY = "server_files" # name of the directory where the transferred files will be stored

# This function represents file transfer from the server side
async def ft_server_proto(scope:Dict, conn:FTQuicConnection):
    # Create the 'server_files' directory if it does not exist
    if not os.path.exists(SERVER_FILES_DIRECTORY):
        os.makedirs(SERVER_FILES_DIRECTORY)

    try:
        # Listen for a connection from the client
        received_datagram, stream_id = await read_framed_datagram(conn)
        # If START PDU is received, begin receiving file data from client
        if received_datagram.mtype != pdu.MSG_TYPE_FILE_START:
            print(f"[svr] Received Unexpected Message Type: {received_datagram.mtype}, Expected File START")
            return
        filename = received_datagram.filename
        print(f"[svr] Receiving File: {filename}")
        received_files[filename] = bytearray()
        last_sequence_number = -1 # begin tracking seq # of file chunks received

        # Loop to receive data until the END PDU is received
        while True:
            file_data_datagram, _ = await read_framed_datagram(conn)
            # Perform checksum for validation
            if file_data_datagram.mtype == pdu.MSG_TYPE_FILE_DATA and file_data_datagram.filename == filename:
                received_file_chunk = base64.b64decode(file_data_datagram.msg.encode("ascii")) # Convert from base64 string to original bytes
                received_checksum = file_data_datagram.checksum
                calculated_checksum = hashlib.sha256(received_file_chunk).hexdigest()
                sequence_number = file_data_datagram.sequence

                if calculated_checksum == received_checksum:
                    if sequence_number == last_sequence_number + 1:
                        received_files[filename].extend(received_file_chunk)
                        print(f"[svr] Received Data Chunk for {filename} with Valid Checksum: {calculated_checksum[:8]}, Seq #: {sequence_number}")
                        last_sequence_number = sequence_number
                    else:
                        print(f"[svr] Sequence Out of Order! Expected Seq #: {last_sequence_number + 1}")
                else:
                    print(f"[svr] Received Data Chunk for {filename} With Invalid Checksum!") 
                    print(f"[svr] Expected: {received_checksum[:8]}, Got: {calculated_checksum[:8]}")
            
            # Store the contents of the file in the established directory        
            elif file_data_datagram.mtype == pdu.MSG_TYPE_FILE_END and file_data_datagram.filename == filename:
                file_content = received_files[filename]
                split_name = os.path.splitext(filename) # split file name and extensions if presents
                modified_filename = f"{split_name[0]}_svr{split_name[1]}"
                received_filepath = os.path.join(SERVER_FILES_DIRECTORY, modified_filename)
                
                # Make sure the file is saved properly
                try:
                    with open(received_filepath, "wb") as f:
                        f.write(file_content)
                    print(f"[svr] File Received and Saved to {received_filepath}, Total Size: {len(file_content)} bytes")
                    
                    # Verify the checksum of entire file from both sides
                    client_overall_checksum = file_data_datagram.checksum
                    server_overall_checksum = await calculate_checksum(received_filepath)
                    if server_overall_checksum == client_overall_checksum:
                        print(f"[svr] Overall Checksums Match! Client: {client_overall_checksum[:8]}, Server: {server_overall_checksum[:8]}")
                        ACK_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_ACK, "File Transfer Successful (Checksum Verified)")
                    else:
                        print(f"[svr] Overall Checksums Mismatch! Client: {client_overall_checksum[:8]}, Server: {server_overall_checksum[:8]}")
                        ACK_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_ACK, "File Transfer Failed (Checksum Mismatch)")
                    ACK_event = QuicStreamEvent(stream_id, ACK_datagram.to_bytes(), False)
                    await conn.send(ACK_event)
                except:
                    print(f"[svr] Error saving file!")
                    ACK_datagram = pdu.Datagram(pdu.MSG_TYPE_FILE_ACK, f"Error saving file!")
                    ACK_event = QuicStreamEvent(stream_id, ACK_datagram.to_bytes, False)
                    await conn.send(ACK_event)
                break
            else:
                print(f"[svr] Unexpected PDU Type: {file_data_datagram.mtype}")
                break
    except:
        print("[svr] File Transfer Failed!")

    print("[svr] Ending File Transfer...")
