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

    # print(agent.q_table[0, 23])
    
    #get_direction(agent=agent)
    host='0.0.0.0'
    port=6969
    server_address = (host, port)
    BUFFER_SIZE = 4096
    while True:
        robot_current_room = int(input("Inserisci stanza robot "))
        direction = get_direction(agent=agent, state=(robot_current_room, 23))
        print(f"direction: {direction}")
   
    
    try:
        while True:
            # Ricevo la stanza corrente dal client
            print(f"Robot current room: {robot_current_room}")
            
            if not robot_current_room:
                break
                
                robot_current_room = int(robot_current_room)
                direction = get_direction(agent=agent, state=(23, robot_current_room))
                print(f"direction: {direction}")
                    
    except KeyboardInterrupt:
        print("Chiusura server")


def get_direction(agent, state = (0, 23)):
    
    # lo state è la tupla del player e del target
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

if __name__ == "__main__":
    main()