import socket as s
import time as t
from line_tracker import *
global N_ROWS
global N_COLS

def main():
    global N_COLS, N_ROWS
    current_room = 23  # É L'ALPHABOT 1
    address = ("192.168.1.138", 6969)
    client = s.socket(s.AF_INET, s.SOCK_STREAM)
    client.connect(address)
    
    N_ROWS, N_COLS = client.recv(4096).decode("utf-8").split(",")
    N_ROWS = int(N_ROWS)
    N_COLS = int(N_COLS)
    
    while True:
        # Invio la posizione attuale
        print(f"stanza corrente: {current_room}")
        client.send(f"{str(current_room)}".encode("utf-8"))
        
        # Ricevo la direzione dal server
        direction = client.recv(4096).decode("utf-8")
        print(f"direzione: {direction}, stanza: {current_room}")
        
        # Eseguo i movimenti
        handle_movements(direction=direction)
        line_tracker()
        
        current_room = calculate_room_number(direction, current_room)
        
        # IMPORTANTE: Invio conferma al server che ho completato i movimenti
        client.send("DONE".encode("utf-8"))
        

def calculate_room_number(direction, room_number):
    global N_COLS, N_ROWS
    print(f"numero colonne{N_COLS},numero righe  {N_ROWS}")
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