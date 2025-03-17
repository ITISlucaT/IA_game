import socket as s
import time as t
from line_tracker import *

global N_ROWS
global N_COLS

def main():
    global N_COLS, N_ROWS
    current_room = 0 ################## É L'ALPHABOT 1
    address = ("192.168.1.138", 6969)

    client = s.socket(s.AF_INET, s.SOCK_STREAM)
    client.connect(address)
    N_ROWS, N_COLS = client.recv(4096).decode("utf-8").split(",")


    while True:
        # se sono sull'incrocio mando la mia posizione (N° stanza)
        print(current_room)
        client.send(f"{current_room}".encode("utf-8"))
        direction = client.recv(4096).decode("utf-8")
        print(direction, current_room)
        line_tracker()
        handle_movements(direction=direction)
        current_room = calculate_room_number(direction, current_room)
        t.sleep(1)


def calculate_room_number(direction, room_number):
    if direction == "UP":
        room_number -= N_COLS
    elif direction == "DOWN":
        room_number += N_COLS
    elif direction == "RIGHT":
        room_number += 1
    else:
        room_number -= 1
    return room_number


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass