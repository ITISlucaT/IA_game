import numpy as np
import gymnasium as gym
from config import load_config
from src.ai.MazeEnv import MazeEnv
import logging

alpha = 0.1  # Tasso di apprendimento
gamma = 0.99  # Fattore di sconto
epsilon = 1.0  # Probabilità di esplorazione 
epsilon_decay = 0.995  # Decadimento di epsilon
min_epsilon = 0.01  # Valore minimo di epsilon

def softmax(x):
    """Converte i valori Q in probabilità usando softmax"""
    e_x = np.exp(x - np.max(x))  # Stabilità numerica
    return e_x / e_x.sum()

def print_state_action_probabilities(q_table):
    """
    Stampa le probabilità di azione per ogni stato
    """
    print("\n--- Probabilità di Azione per Stato ---")
    for player_room in range(q_table.shape[0]):
        for target_room in range(q_table.shape[1]):
            state_q_values = q_table[player_room, target_room]
            
            # Calcola le probabilità con softmax
            action_probs = softmax(state_q_values)
            
            print(f"\nStato (Stanza Giocatore: {player_room}, Stanza Target: {target_room}):")
            for action, prob in enumerate(action_probs):
                action_names = ["SU", "GIù", "SINISTRA", "DESTRA"]
                print(f"  {action_names[action]}: {prob*100:.2f}%")

def train_q_learning(env, num_episodes=1000, max_steps_per_episode=200):
    num_rooms = env.game.NUM_ROOMS
    state_size = (num_rooms, num_rooms)
    action_size = env.action_space.n
    
    q_table = np.zeros(state_size + (action_size,))
    
    epsilon = 1.0
    total_rewards_per_episode = []

    for episode in range(num_episodes):
        state, _ = env.reset()
        state = discretize_state(state, num_rooms)
        
        total_episode_reward = 0
        done = False
        
        for step in range(max_steps_per_episode):
            if np.random.rand() < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(q_table[state])
            
            next_state, reward, done, truncated, info = env.step(action)
            next_state = discretize_state(next_state, num_rooms)
            
            # Aggiorna Q-table
            old_value = q_table[state + (action,)]
            next_max = np.max(q_table[next_state])
            
            new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
            q_table[state + (action,)] = new_value
            
            total_episode_reward += reward
            state = next_state
            
            if done or truncated:
                break
        
        epsilon = max(min_epsilon, epsilon * epsilon_decay)
        total_rewards_per_episode.append(total_episode_reward)
        
        # Stampa progressi
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(total_rewards_per_episode[-100:])
            print(f"Episodio: {episode + 1}, Ricompensa media: {avg_reward:.2f}, Epsilon: {epsilon:.2f}")
    
    # Stampa le probabilità dopo l'addestramento
    print_state_action_probabilities(q_table)
    
    return q_table

def discretize_state(state, num_rooms):
    player_room = max(0, min(int(state[0]), num_rooms - 1))
    target_room = max(0, min(int(state[1]), num_rooms - 1))
    return (player_room, target_room)

def main():
    # Parametri del Q-Learning (come prima)
    alpha = 0.1  # Tasso di apprendimento
    gamma = 0.99  # Fattore di sconto
    epsilon = 1.0  # Probabilità di esplorazione 
    epsilon_decay = 0.995  # Decadimento di epsilon
    min_epsilon = 0.01  # Valore minimo di epsilon

    # Inizializza l'ambiente
    env = MazeEnv()
    
    # Addestra il modello Q-Learning
    q_table = train_q_learning(env)
    
    # Chiudi l'ambiente
    env.close()

if __name__ == "__main__":
    main()