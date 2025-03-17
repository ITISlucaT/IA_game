from src.ai.MazeEnv import MazeEnv
from src.ai.QLearningAgent import QLearningAgent
import time
import threading
import socket
def main():
    env = MazeEnv()
    agent = QLearningAgent(env)
    
    # Load trained model
    agent.load_model('maze_q_learning_model.pkl')

    host='0.0.0.0'
    port=6969

    
    
    server_address = (host, port)
    BUFFER_SIZE = 4096 

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_server_socket.bind(server_address)

    tcp_server_socket.listen(1)
    print(f"Server in ascolto su {server_address}")

    conn, client_address = tcp_server_socket.accept()
    print(f"Connesso al client {client_address}")

    conn.send(f"{env.game.NUM_ROWS},{env.game.NUM_COLS}".encode("utf-8"))

    try:
        while True:
        
            robot_current_room = conn.recv(BUFFER_SIZE).decode("utf-8")
            print(f"Robot current room: {robot_current_room}")
            robot_current_room = int(robot_current_room)
            conn.send(get_direction(agent=agent, state=(robot_current_room, 23)).encode("utf-8"))
            
            if not robot_current_room:
                break  

            print(f"Ricevuto dal client: {robot_current_room}")
            
    except KeyboardInterrupt:
        print("Chiusura server")
    finally:
        tcp_server_socket.close()

def get_direction(agent, state = (0, 23)):
    
    # lo state è la tupla del player e del target

    action = agent.get_action(state=state)
    print(f"action: {action}")
    action_map = {
            0: "UP",
            1: "DOWN", 
            2: "LEFT", 
            3: "RIGHT"
        }
    direction = action_map[action]
    print(f"direction: {direction}")

    return direction


if __name__ == "__main__":
    main()