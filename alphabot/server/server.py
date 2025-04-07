from src.ai.MazeEnv import MazeEnv
from src.ai.QLearningAgent import QLearningAgent
import time
import threading
import socket

# Variabili globali per le posizioni dei giocatori
PLAYER1_CURRENT_ROOM = None
PLAYER2_CURRENT_ROOM = None

# Barrier per sincronizzare i client
client_barrier = threading.Barrier(2)
client_data_lock = threading.Lock()
client_ready = [False, False]
client_connections = [None, None]

def handle_client(conn, client_address, env, agent, player_id):
    global PLAYER1_CURRENT_ROOM, PLAYER2_CURRENT_ROOM, client_ready, client_connections
    
    print(f"Connesso al client {client_address} come Player {player_id}")
    BUFFER_SIZE = 4096
    
    # Salva la connessione per invio futuro
    client_connections[player_id] = conn
    
    # Invia le dimensioni del labirinto al client
    conn.send(f"{env.game.NUM_ROWS},{env.game.NUM_COLS}".encode("utf-8"))
    
    try:
        while True:
            # Ricevi la stanza corrente dal client
            robot_current_room = conn.recv(BUFFER_SIZE).decode("utf-8")
            print(f"Client {player_id} - Robot current room: {robot_current_room}")
            
            if not robot_current_room:
                break
                
            try:
                # Aggiorna la posizione corrente del giocatore
                robot_current_room = int(robot_current_room)
                with client_data_lock:
                    if player_id == 0:
                        PLAYER1_CURRENT_ROOM = robot_current_room
                    else:
                        PLAYER2_CURRENT_ROOM = robot_current_room
                    client_ready[player_id] = True
                    print(f"PLAYER1_CURRENT_ROOM: {PLAYER1_CURRENT_ROOM}, PLAYER2_CURRENT_ROOM: {PLAYER2_CURRENT_ROOM}")
                
                # Attendi che entrambi i client abbiano inviato le loro posizioni
                print(f"Player {player_id} in attesa dell'altro giocatore...")
                
                # Usando barrier per sincronizzare i due thread
                client_barrier.wait()
                
                # Resetta il barrier se necessario (nel thread 0)
                if player_id == 0:
                    with client_data_lock:
                        # Verifica che entrambi i client siano pronti
                        if all(client_ready):
                            # Calcola le direzioni per entrambi i client
                            direction1 = get_direction(agent=agent, state=(PLAYER1_CURRENT_ROOM, PLAYER2_CURRENT_ROOM))
                            direction2 = get_direction(agent=agent, state=(PLAYER2_CURRENT_ROOM, PLAYER1_CURRENT_ROOM))
                            
                            # Invia le direzioni a entrambi i client
                            client_connections[0].send(direction1.encode("utf-8"))
                            client_connections[1].send(direction2.encode("utf-8"))
                            
                            print(f"Inviate direzioni: Player 0 -> {direction1}, Player 1 -> {direction2}")
                            
                            # Resetta i flag di prontezza
                            client_ready = [False, False]
                
                # Attendi conferma che il client ha completato i movimenti
                completion_status = conn.recv(BUFFER_SIZE).decode("utf-8")
                if completion_status == "DONE":
                    print(f"Client {player_id} ha completato i movimenti")
                else:
                    print(f"Messaggio inatteso dal client {player_id}: {completion_status}")
                    
            except ValueError:
                print(f"Errore nel formato della stanza ricevuta da client {player_id}: {robot_current_room}")
    except Exception as e:
        print(f"Errore con client {player_id}: {e}")
    finally:
        conn.close()
        print(f"Connessione con client {player_id} chiusa")
        # Segna che questo client non è più disponibile
        with client_data_lock:
            client_connections[player_id] = None
            client_ready[player_id] = False

def get_direction(agent, state = (0, 23)):
    # Lo state è la tupla del player e del target
    action = agent.get_action(state=state)
    print(f"action: {action}")
    action_map = {
        0: "UP",
        1: "DOWN",
        2: "LEFT",
        3: "RIGHT",
        4: "STOP"
    }
    direction = action_map[action]
    return direction

def main():
    env = MazeEnv()
    agent = QLearningAgent(env)
    # Carica il modello addestrato
    agent.load_model('maze_q_learning_model.pkl')
    print(agent.q_table[0, 23])
    
    host = '0.0.0.0'
    port = 6969
    server_address = (host, port)
    
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(server_address)
    tcp_server_socket.listen(5)  # Aumenta il backlog per gestire più client
    print(f"Server in ascolto su {server_address}")
    
    player_count = 0
    client_threads = []
    
    try:
        while player_count < 2:  # Accetta esattamente 2 client
            # Accetta connessione dal client
            conn, client_address = tcp_server_socket.accept()
            
            # Crea un nuovo thread per gestire il client
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, client_address, env, agent, player_count)
            )
            client_thread.daemon = True
            client_thread.start()
            
            client_threads.append(client_thread)
            player_count += 1
            print(f"Connesso client {player_count}/2")
        
        print("Entrambi i client connessi. Il gioco può iniziare.")
        
        # Mantieni il server in esecuzione
        while any(thread.is_alive() for thread in client_threads):
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Chiusura server")
    finally:
        # Chiudi il socket del server
        tcp_server_socket.close()
        
        # Attendi il completamento di tutti i thread client
        for thread in client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

if __name__ == "__main__":
    main()