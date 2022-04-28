"""A daemon server listening video process requests.

Listens to socket messages passed from the upload nodejs server.
"""

from datetime import datetime
from pathlib import Path
from typing import Union
import socket
import queue
import threading
import time
import shutil
import os

host = 'localhost'
port = 3520
max_queue_length = 20

dirname = Path(__file__).parent


# Python Queue does not know the exact length of queue.
# Must maintain the size with a variable. 
qSize = 0

VIDEO_HEADER = ("VIDEO_")
TERMINATE_HEADER = ("TERMINATE_")

exitFlag = False
video_to_process = queue.Queue(max_queue_length)

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = video_to_process
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        print("Start listening to node messages")
        self.socket.bind((host, port))
        self.socket.listen(max_queue_length)
        while not exitFlag:
            conn, addr = self.socket.accept()

            request_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            print(f"New request received at {request_time}")

            # Rejects non-localhost requests for protection.
            if '127.0.0.1' not in str(addr):
                reject_message = f"Rejected connection: {str(addr)}"
                print(reject_message)
                conn.send(reject_message.encode())
                conn.close()
                continue

            indata = conn.recv(1024)
            if not indata:
                print("indata is empty, skippped.")
                continue

            indata = indata.decode()

            # Only accepts messages starting with "VIDEO_".
            if indata.startswith(VIDEO_HEADER):
                # Get the video name
                indata = indata[len(VIDEO_HEADER):]
                print(f"Added video {indata} to queue")
                self.queue.put(indata)
                conn.close()

            else:
                outdata = f"Rejected connection due to invalid message: {indata}"
                print(outdata)
                conn.close()


class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = video_to_process

    def make_bones(self, video_path: os.PathLike[str]):
        new_folder = dirname / "processed_video_storage"
        video_name = os.path.basename(video_path)
        print(f"NEW VID {video_name}")
        shutil.copyfile(video_path, new_folder / video_name)

    def run(self):
        print("Start consuming the video queue...")
        while not exitFlag:
            video_path = self.queue.get()
            # print(f"Processing {video_path}")
            self.make_bones(video_path)
            print(f"Completed bone for: {video_path}")




if __name__ == "__main__":
    producer = Producer()          # create producer object with priority 6
    consumer = Consumer()          # create consumer object with priority 2

    # start producer and consumer threads
    producer.start()
    consumer.start()
    pass