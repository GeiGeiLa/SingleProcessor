"""A daemon server listening video process requests.

Listens to socket messages passed from the upload nodejs server.

"""




from filelock import FileLock
from datetime import datetime
from pathlib import Path
from typing import Union
import socket
import queue

import long_process


host = 'localhost'
port = 3520
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


dirname = Path(__file__).parent

video_to_process = queue.Queue()

# Python Queue does not know the exact length of queue.
# Must maintain the size with a variable. 
qSize = 0

VIDEO_HEADER = ("VIDEO_")
TERMINATE_HEADER = ("TERMINATE_")


def call_detector(file_name):
    long_process.perform_long_operation(file_name)
    print("Completed")

if __name__ == "__main__":

    s.bind((host, port))
    s.listen(10)
    print(f"Listening on port {port}")

    try:
        while True:

            conn, addr = s.accept()
            request_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            print(f"New request received at {request_time}")

            # Rejects non-localhost requests for protection.
            if '127.0.0.1' not in str(addr):
                conn.send(str(f"Rejected connection: {str(addr)}").encode())
                conn.close()
                continue

            indata = conn.recv(1024)
            if not indata:
                continue
            indata = indata.decode()

            # Only accepts messages starting with "VIDEO_".
            if indata.startswith(VIDEO_HEADER):
                indata = indata[len(VIDEO_HEADER):]
                print("Added video to queue")
                video_to_process.put(indata)
                qSize += 1
                conn.close()
                print(video_to_process)
                outdata = f'queuing {indata}'
                # this is the only video to process
                if qSize == 1:
                    call_detector(video_to_process.get())
                    qSize -= 1
                
            # Notifies that a video process is completed.
            elif indata.startswith(TERMINATE_HEADER):
                outdata = "Understood"
                conn.send(outdata.encode())
                conn.close()
                if not video_to_process.empty():
                    call_detector(video_to_process.get())
                    qSize -= 1
            else:
                outdata = f"Rejected connection due to invalid message: {indata}"
                conn.send(outdata.encode())
                conn.close()
    finally:
        s.close()

        # with FileLock(dirname / "lockfile") as lock:
        #     # This part of code is guarenteed to be run by only a single thread
        #     now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        #     print(f"Starting request at {now}")
        #     long_process.perform_long_operation()



