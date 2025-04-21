import pygame 
import pygame.font 
import random
import os
from datetime import datetime


class GameLogger:
    def __init__(self):
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.folder = os.path.join(log_dir, f"game_log_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)

        self.log_file_path = os.path.join(self.folder, "log.csv")
        self.result_file_path = os.path.join(self.folder, "result.txt")

        self.log_file = open(self.log_file_path, "w")
        self.log_file.write("x,y,vx,vy,phi,dphi,ux,uy,left_key,right_key,up_key,down_key\n")

    def log(self, text):
        self.log_file.write(text + "\n")

    def save_result(self, result_summary):
        with open(self.result_file_path, "w") as result_file:
            result_file.write(result_summary)

    def __del__(self):
        self.log_file.close()

class Game:

    def __init__(self,  initial_entities, window_dims=(640, 480), caption="Simple Game", bg_color=(255, 255, 255), time_step=60):
        self.logger = GameLogger()
        pygame.init()
        pygame.font.init()
        (width, height) = window_dims
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(bg_color)
        self.bg_color = bg_color
        self.time_step = time_step
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.ents = initial_entities
        self.running = True
        self.listeners = {}
        self.event_queue = [] 
        for e in self.ents:
            e.init(self)
        
    def add_entity(self, entity):
        self.ents.append(entity)
        entity.init(self)
        
    def add_listener(self, entity, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append((entity, callback))

    def send_event(self, event, params):
        if event in self.listeners:
            lambs = self.listeners[event]
            new_lambs = [] 
            for entity, callback in lambs:
                rval = callback(self, params)
                if rval:
                    new_lambs.append((entity, callback))
            self.listeners[event] = new_lambs

    def game_over(self, result_summary):
        self.running = False
        self.logger.save_result(result_summary)
        return False

    def run(self, keypress_events):

        # first run all the keypress events 
        while self.running:
            self.clock.tick(self.time_step)
            # process external events from the keyboard 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    for key, down_event, _ in keypress_events:
                        if event.key == key:
                            self.send_event(down_event, None)
                elif event.type == pygame.KEYUP:
                    for key, _, up_event in keypress_events:
                        if event.key == key:
                            self.send_event(up_event, None)


            # first call update on all the entities 
            new_entities = [] 
            for entity in self.ents:
                new_entities += entity.update(self)
            self.ents = new_entities
            # then draw all the entities
            self.screen.fill(self.bg_color)
            for entity in self.ents:
                entity.draw(self.screen)
            pygame.display.update()