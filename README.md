# CS 544 Course Project - File Transfer Protocol Over QUIC

This project runs a simple file transfer application using the QUIC protocol in Python with the 'aioquic' library.

## Software Requirements

- Python 3.10 or higher

## Setup
1. Clone the repository:
```sh
git clone https://github.com/jcm0905/CS544.git
```
Navigate to the `FTPQUIC` folder:
```sh
cd CS544/FTPQUIC
```

2. Generate the necessary authentication certificates

Navigate to the `certs` folder and run the following command:
```sh
bash gencert.sh
```
3. In the `FTPQUIC` folder, create a Python Virtual Environment
```sh
python3 -m venv venv
```

5. Activate the Python Virtual Environment
```sh
source venv/bin/activate
```

6. Install the libraries needed to run the program
```sh
pip install -r requirements.txt
```

7. Confirm installation of the libraries
```sh
pip list
```

8. Exit the Python Virtual Environment
```sh
deactivate
```

9. Create a file to transfer
```sh
echo "Created a file for testing this program..." > test_file
```

## Running the Project

1. Open 2 terminals: one for the client and one for the server

2. Navigate to the `FTPQUIC` folder in both terminals

4. Activate the Python Virtual Environment in both terminals
```sh
source venv/bin/activate
```

3. Start the server in one terminal
```sh
python3 file_transfer.py server
```

4. Run the client in the other terminal
```sh
python3 file_transfer.py client -f test_file
```

The server will continue to run, and you can keep running the client by executing the same command in (4) to continue transferring different files to the server.

5. When finished, exit the Python Virtual Environment in both terminals
```sh
deactivate
```

## Verify File Transfer

After running the program:
- Navigate to the `server_files` directory to see if the file is present there
- The transferred file will have a `_svr` in its name to indicate a successful file transfer
- In a free terminal, run this command to perform a comparison between both files:
```sh
diff <filename> server_files/<filename>
```

If there is no output, it means that there is no difference between the two files (i.e., the file transferred successfully)

## Deleting the Python Virtual Environment

If you would like to delete the virtual environment in the project directory, run this command:
```sh
rm -rf venv
```


## Deleting server_files/ directory

If you would like to remove the server_files/ directory to start from scratch, run this command:
```sh
rm -rf server_files/
```

## Configuration

The client and server can be configured using command-line arguments.

### Client Arguments

- `-s`, `--server`: Server address (e.g., localhost (default), `127.0.0.1`, etc.)
- `-p`, `--port`: Server port number (e.g., 4433 (default), 5000, etc.)
- `-c`, `--cert-file`: Path to the QUIC certificate (.pem file)
- `-f`, `--filename`: Path to the file to be sent to the server

### Server Arguments

- `-c`, `--cert-file`: Path to the QUIC certificate (.pem file)
- `-k`, `--key-file`: Path to the QUIC private key (.pem file)
- `l`, `--listen`: Address for server to listen on
- `p`, `--port`: Port number for server to listen on

Run these commands for client and server for more information about these command line arguments:

Client:
```sh
python3 file_transfer.py client -h
```

Server:
```sh
python3 file_transfer.py server -h
```
