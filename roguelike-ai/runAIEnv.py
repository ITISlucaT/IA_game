from src.ai.MazeEnv import MazeEnv
from src.ai.QLearningAgent import QLearningAgent
def main():

    env = MazeEnv()
    

    agent = QLearningAgent(env)
    
    try:
        # Option 1: Train and save the model
        #agent.train(num_episodes=10000, max_steps_per_episode=2000)
        #agent.save_model('maze_q_learning_model.pkl')
        
        # Option 2: Load a pre-existing model and test
        agent.load_model('maze_q_learning_model.pkl')
        # Perform multiple test runs
        test_rewards = agent.test(num_tests=10)
        #print("\nTest Rewards:", test_rewards)
    except KeyboardInterrupt:
        print("Training interrupted. Saving model...")
        agent.save_model('maze_q_learning_model.pkl')
        print("Model saved.")
    
    # Close the environment
    env.close()

if __name__ == "__main__":
    main()