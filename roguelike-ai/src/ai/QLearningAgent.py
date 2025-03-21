import numpy as np
import gymnasium as gym
from config import load_config
from src.ai.MazeEnv import MazeEnv
import os
import pickle
import time

class QLearningAgent:
    def __init__(self, env, learning_rate=0.1, discount_factor=0.99, 
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01):
        """
        Initialize Q-Learning Agent
        
        Parameters:
        - env: The environment
        - learning_rate: Rate at which the agent learns from new experiences
        - discount_factor: How much future rewards are valued
        - exploration_rate: Probability of choosing a random action
        - exploration_decay: Rate at which exploration decreases
        - min_exploration: Minimum exploration probability
        """
        self.env = env
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.min_epsilon = min_exploration
        
        # Obtain maze dimensions
        self.num_rooms = env.game.NUM_ROOMS
        
        # Define Q-table dimensions
        state_size = (self.num_rooms, self.num_rooms)
        action_size = env.action_space.n
        
        # Initialize Q-table
        self.q_table = np.zeros(state_size + (action_size,))
        
        # Training history
        self.training_history = {
            'episode_rewards': [],
            'average_rewards': []
        }

    def discretize_state(self, state):
        """
        Discretize the state ensuring it's within maze bounds
        """
        player_room = max(0, min(int(state[0]), self.num_rooms - 1))
        target_room = max(0, min(int(state[1]), self.num_rooms - 1))
        print(f"player_room = {player_room}, target_room = {target_room}")
        return (player_room, target_room)

    def train(self, num_episodes=200, max_steps_per_episode=200):
        """
        Train the Q-Learning agent
        
        Parameters:
        - num_episodes: Number of training episodes
        - max_steps_per_episode: Maximum steps in each episode
        """
        total_rewards_per_episode = []

        for episode in range(num_episodes):
            # Reset environment
            state, _ = self.env.reset()
            state = self.discretize_state(state)
            
            total_episode_reward = 0
            done = False
            
            for step in range(max_steps_per_episode):
                # Action selection (exploration vs exploitation)
                if np.random.rand() < self.epsilon:
                    action = self.env.action_space.sample()  # Exploration
                else:
                    action = np.argmax(self.q_table[state])  # Exploitation
                
                # Execute action
                next_state, reward, done, truncated, info = self.env.step(action)
                next_state = self.discretize_state(next_state)
                
                # Q-table update
                old_value = self.q_table[state + (action,)]
                next_max = np.max(self.q_table[next_state])
                
                new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
                self.q_table[state + (action,)] = new_value
                
                total_episode_reward += reward
                state = next_state
                
                if done or truncated:
                    break
            
            # Decay exploration rate
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            
            total_rewards_per_episode.append(total_episode_reward)
            
            # Record training history
            self.training_history['episode_rewards'].append(total_episode_reward)
            
            # Print progress
            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(total_rewards_per_episode[-100:])
                self.training_history['average_rewards'].append(avg_reward)
                print(f"Episode: {episode + 1}, Average Reward: {avg_reward:.2f}, Epsilon: {self.epsilon:.2f}")
        
        return self.q_table

    def test(self, num_tests=5, render=True, max_steps=2000):
        """
        Test the trained Q-Learning agent
        
        Parameters:
        - num_tests: Number of test runs
        - render: Whether to render the environment
        - max_steps: Maximum steps per test run
        
        Returns:
        - List of total rewards for each test run
        """
        test_rewards = []
        
        for test in range(num_tests):
            print(f"\nTest Run {test + 1}")
            
            # Reset environment
            state, _ = self.env.reset()
            state = self.discretize_state(state)
            
            total_reward = 0
            done = False
            steps = 0
            
            while not done and steps < max_steps:
                # Always choose the best action (no exploration)
                action = np.argmax(self.q_table[state])
                
                # Execute action
                next_state, reward, done, truncated, info = self.env.step(action)
                next_state = self.discretize_state(next_state)
                print(f"State: {state}")
                print(f"\nStep {action}")
                
                state = next_state
                total_reward += reward
                steps += 1
                time.sleep(1)
                # Render if specified
                if render:
                    self.env.render()
            
            print(f"Total Reward: {total_reward}")
            print(f"Steps Executed: {steps}")
            
            test_rewards.append(total_reward)
        
        return test_rewards

    def save_model(self, filename='q_learning_model.pkl'):
        """
        Save the trained Q-table to a file
        
        Parameters:
        - filename: Path to save the model
        """
        with open(filename, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'training_history': self.training_history
            }, f)
        print(f"Model saved to {filename}")

    def load_model(self, filename='q_learning_model.pkl'):
        """
        Load a previously saved Q-table
        
        Parameters:
        - filename: Path to load the model from
        """
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.training_history = data.get('training_history', {})
            print(f"Model loaded from {filename}")
        else:
            print(f"No model found at {filename}")