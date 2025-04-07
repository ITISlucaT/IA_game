from src.ai.MazeEnv import MazeEnv
from src.ai.QLearningAgent import QLearningAgent
def main():

    env = MazeEnv()
    

    agent = QLearningAgent(env)
    print({k: v for k, v in env.game.graph.adjacency()})
    print()
    
    # Option 1: Train and save the model
    #agent.train(num_episodes=10000)
    #agent.save_model('maze_q_learning_model.pkl')
    
    # Option 2: Load a pre-existing model and test
    agent.load_model('maze_q_learning_model.pkl')
    # Perform multiple test runs
    test_rewards = agent.test(num_tests=5)
    print("\nTest Rewards:", test_rewards)
    
    # Close the environment
    env.close()

if __name__ == "__main__":
    main()