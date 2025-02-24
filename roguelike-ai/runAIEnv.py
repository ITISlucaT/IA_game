from src.ai.MazeEnv import MazeEnv

env = MazeEnv()
obs, info = env.reset()
done = False

while not done:
    action = env.action_space.sample()  # Semplice politica random
    obs, reward, done, _, _ = env.step(action)
    env.render()
print("Final Score:", env.score) 
env.close()
