from game_framework import Game
from quadrotor_landing_game import Quadrotor, GameParams, GameStateMonitor, ThrottleDisplay, DroneSnake
import pygame

if __name__ == "__main__":
    initial_entities = [
        Quadrotor(0, 0, 0, 0, 0, 0, 0, 0),
        GameStateMonitor(),
        ThrottleDisplay(),
        DroneSnake()
    ]
    game = Game(initial_entities, window_dims=(GameParams.width, GameParams.height), caption="Quadrotor Landing Game", bg_color=(255, 255, 255), time_step=50)
    game.run(GameParams.keypress_events)
    pygame.quit()
    print("Game Over")
