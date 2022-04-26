import time
from typing import Union
from os import PathLike
import socket
from contextlib import contextmanager



def perform_long_operation(filePath: Union[str, PathLike], duration:int = 8):
    host = 'localhost'
    port = 3520
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for sec in range(duration):
            print(sec)
            time.sleep(1)
        # the ldataong process ended, notify the listener to process next video
        s.send("TERMINATE_".encode())
    