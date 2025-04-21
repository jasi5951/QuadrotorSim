import pygame 
import pygame.font
import random 
from game_framework import Game 
import math 
import random

class GameParams:
    width = 1600
    height = 900
    keypress_events = [ (pygame.K_LEFT, 'left_keydown', 'left_keyup'), 
                       (pygame.K_RIGHT, 'right_keydown', 'right_keyup'),
                        (pygame.K_w, 'w_keydown', 'w_keyup'), 
                        (pygame.K_s, 's_keydown', 's_keyup') ]
    g = 9.81
    m = 0.25 
    dt = 0.02
    Ixx = 0.01 
    K = [-0.1, -1.0, -30.0]  # PID controller gains
    pad_width = 80 
    pad_height = 10
    pad_x = 800 - pad_width
    pad_y = 890 - pad_height*2
    ux_step=0.05
    uy_step=0.15
    min_ux = -0.5
    max_ux = 0.5
    min_uy = -5
    max_uy = 5
    quadrotor_width = 50
    quadrotor_height = 25
    very_tough = random.choice([True, False])



    
class Quadrotor: 
    def __init__(self, x, y, vx, vy, phi, dphi, ux, uy):
        self.logger = None
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.phi = phi 
        self.dphi = dphi
        self.ux = ux 
        self.uy = uy
        self.width = GameParams.quadrotor_width
        self.height = GameParams.quadrotor_height
        self.color = (0, 0, 255)  # Blue color for the quadrotor
        # load the quadrotor image file from quadrotor.png
        self.image = pygame.image.load('drone.png')
        # scale the image to the size of the quadrotor
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.left_pressed = False
        self.right_pressed = False
        self.w_pressed = False
        self.s_pressed = False
    
    def init(self, game_state):
        self.logger = game_state.logger
        self.x = random.uniform(1/5* GameParams.width, 5/6* GameParams.width)
        self.y = random.uniform(1/10* GameParams.height, 1/5* GameParams.height)
        self.vx = 0.0
        self.vy = 0.0
        self.phi = 0.0 # random.uniform(-math.pi/6, math.pi/6)
        self.dphi = 0.0 # random.uniform(-0.01, 0.01)
        self.ux = 0
        self.uy = 0
        # game_state.add_listener(self, 'left_keypress', self.on_left_keypress)
        # game_state.add_listener(self, 'right_keypress', self.on_right_keypress)
        # game_state.add_listener(self, 'w_keypress', self.on_w_keypress)
        # game_state.add_listener(self, 's_keypress', self.on_s_keypress)
        
        game_state.add_listener(self, 'left_keydown', self.on_left_keydown)
        game_state.add_listener(self, 'left_keyup', self.on_left_keyup)
        game_state.add_listener(self, 'right_keydown', self.on_right_keydown)
        game_state.add_listener(self, 'right_keyup', self.on_right_keyup)
        game_state.add_listener(self, 'w_keydown', self.on_w_keydown)
        game_state.add_listener(self, 'w_keyup', self.on_w_keyup)
        game_state.add_listener(self, 's_keydown', self.on_s_keydown)
        game_state.add_listener(self, 's_keyup', self.on_s_keyup)



    def draw(self, screen):
        # draw a line from (x,y) to (x + width * cos(phi), y + height * sin(phi))
        #delta_x = self.width * math.cos(self.phi)/2.0
        #delta_y = self.height * math.sin(self.phi)/2.0
        #pygame.draw.line(screen, self.color, (self.x-delta_x, self.y-delta_y), (self.x + delta_x, self.y + delta_y), 5)
        # draw an image of a drone rotated by phi
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.phi/5))
        image_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, image_rect.topleft)

    def update(self, game_state):
        if GameParams.very_tough:
            if self.left_pressed: #and not self.right_pressed:
                self.ux = max(self.ux - GameParams.ux_step, GameParams.min_ux)
            elif self.right_pressed: #and not self.left_pressed:
                self.ux = min(self.ux + GameParams.ux_step, GameParams.max_ux)
        else:
            if self.left_pressed and not self.right_pressed:
                self.ux = max(self.ux - GameParams.ux_step, GameParams.min_ux)
            elif self.right_pressed and not self.left_pressed:
                self.ux = min(self.ux + GameParams.ux_step, GameParams.max_ux)
            else:
                self.ux = 0

        if self.w_pressed:
            self.uy = max(self.uy - GameParams.uy_step, GameParams.min_uy)
        if self.s_pressed:
            self.uy = min(self.uy + GameParams.uy_step, GameParams.max_uy)


        # update the position of the quadrotor
        xp = self.x + self.vx * GameParams.dt
        yp = self.y + self.vy * GameParams.dt
        # update the velocity of the quadrotor
        phip = self.phi + self.dphi * GameParams.dt
        vxp = self.vx + GameParams.g * GameParams.dt * self.phi 
        vyp = self.vy  + GameParams.K[0] * GameParams.dt * self.vy + 1/GameParams.m * GameParams.dt * self.uy 
        dphip = self.dphi + GameParams.K[1] * GameParams.dt * self.phi + GameParams.K[2] * GameParams.dt * self.dphi + 1/GameParams.Ixx * GameParams.dt * self.ux
        self.x = xp
        self.y = yp
        self.vx = vxp
        self.vy = vyp
        self.phi = phip
        self.dphi = dphip
        game_state.send_event('quadrotor_position', (self.x, self.y, self.phi, self.vx, self.vy))
        game_state.send_event('quadrotor_control', (self.ux, self.uy))

        if self.logger:
            self.logger.log(
                f"{self.x:.4f},{self.y:.4f},{self.vx:.4f},{self.vy:.4f},{self.phi:.4f},{self.dphi:.4f},{self.ux:.4f},{self.uy:.4f},{int(self.left_pressed)},{int(self.right_pressed)},{int(self.w_pressed)},{int(self.s_pressed)}"
            )


        return [self]
    
    def on_left_keydown(self, gstate, p): self.left_pressed = True; return True
    def on_left_keyup(self, gstate, p): self.left_pressed = False; return True
    def on_right_keydown(self, gstate, p): self.right_pressed = True; return True
    def on_right_keyup(self, gstate, p): self.right_pressed = False; return True
    def on_w_keydown(self, gstate, p): self.w_pressed = True; return True
    def on_w_keyup(self, gstate, p): self.w_pressed = False; return True
    def on_s_keydown(self, gstate, p): self.s_pressed = True; return True
    def on_s_keyup(self, gstate, p): self.s_pressed = False; return True

    # def on_left_keypress(self, gstate,  p):
    #     # move the quadrotor to the left
    #     self.ux = self.ux - GameParams.ux_step 
    #     if self.ux <= GameParams.min_ux:
    #         self.ux = GameParams.min_ux
    #     return True 
    
    # def on_right_keypress(self, gstate, p):
    #     # move the quadrotor to the right
    #     self.ux = self.ux + GameParams.ux_step
    #     if self.ux >= GameParams.max_ux:
    #         self.ux = GameParams.max_ux
    #     return True 

    # def on_s_keypress(self, gstate, p):
    #     # move the quadrotor up
    #     self.uy = self.uy + GameParams.uy_step
    #     if self.uy >= GameParams.max_uy:
    #         self.uy = GameParams.max_uy
    #     return True 

    # def on_w_keypress(self, gstate,  p):
    #     # move the quadrotor down
    #     self.uy = self.uy - GameParams.uy_step
    #     if self.uy <= GameParams.min_uy:
    #         self.uy = GameParams.min_uy
    #     return True 

    

class ThrottleDisplay:
    def __init__(self):
        self.ux = 0
        self.uy = 0
        self.vx = 0
        self.vy = 0
        self.x = 0
        self.y = 0
        self.speed = 0
        self.tilt_angle = 0
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)  # Default font and size
        self.color = (0, 0, 0)  # Black color for the text
        self.width = 50

    def init(self, game_state):
        game_state.add_listener(self, 'quadrotor_control', self.on_quadrotor_control) 
        game_state.add_listener(self, 'quadrotor_position', self.on_quadrotor_position)

    def on_quadrotor_control(self, game_state, control):
        (ux, uy) = control
        self.ux = ux 
        self.uy = uy
        return True 
    
    def on_quadrotor_position(self, game_state, pos):
        (x, y, phi, vx, vy) = pos
        self.x = x
        self.y = y
        self.vx = vx 
        self.vy = vy
        self.speed = math.sqrt(vx**2 + vy**2)
        self.tilt_angle = math.degrees(-phi/5)
        return True


    def draw(self, screen):
        lines = [
            f"(x, y): ({self.x:.0f}, {self.y:.0f})",
            f"lateral speed: {self.vx:.1f}",
            f"vertical speed: {self.vy:.1f}",
            f"tilt angle: {self.tilt_angle:.2f}",
            f"difficulty: {'hard' if GameParams.very_tough else 'normal'}",
        ]
        text_colors = [
            self.color,
            self.color if self.speed <= 15 else (255, 0, 0),
            self.color if self.speed <= 15 else (255, 0, 0),
            self.color if abs(self.tilt_angle) <= 3 else (255, 0, 0),
            self.color,
        ]

        for i, (text, col) in enumerate(zip(lines, text_colors)):
            text_surface = self.font.render(text, True, col)
            screen.blit(text_surface, (10, 10 + i * 30))
        
        center_x = 80  
        center_y = GameParams.height - 80 

        ux_scale = 80  
        uy_scale = -10

        uy_length = self.uy * uy_scale
        ux_length = self.ux * ux_scale

        pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (center_x, center_y - uy_length), 4)

        pygame.draw.line(screen, (0, 0, 255), (center_x, center_y), (center_x + ux_length, center_y), 4)

        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 5)

    def update(self, game_state):
        return [self]


class DroneSnake:
    def __init__(self):
        self.x_positions = []
        self.y_positions = []
    
    def init(self, game_state):
        self.x_positions = []
        self.y_positions = []
        game_state.add_listener(self, 'quadrotor_position', self.on_quadrotor_position)

    def on_quadrotor_position(self, game_state, pos):
        (x, y, phi, vx, vy) = pos
        self.x_positions.append(x)
        self.y_positions.append(y)
        if len(self.x_positions) > 200:
            self.x_positions.pop(0)
            self.y_positions.pop(0)
        return True
    
    def draw(self, screen):
        for i in range(len(self.x_positions)-1):
            if i % 2 == 0:
                dx = self.x_positions[i+1] - self.x_positions[i]
                dy = self.y_positions[i+1] - self.y_positions[i]
                x = self.x_positions[i]
                y = self.y_positions[i]
                pygame.draw.line(screen, (20, 20, 100), (x, y), (x + dx, y + dy), 1)
        return True
    
    def update(self, game_state):
        return [self]
    

class GameStateMonitor:
    def __init__(self):
        self.logger = None
        self.quadrotor_positions = []
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.time = 0
        self.start_time = None

    def init(self, game_state):
        self.logger = game_state.logger
        game_state.add_listener(self, 'quadrotor_position', self.on_quadrotor_position)
    
    def on_quadrotor_position(self, game_state, pos):
        (x, y, phi, vx, vy) = pos
        if x + GameParams.quadrotor_width/2 >= GameParams.pad_x and y + GameParams.quadrotor_height/2 >= GameParams.pad_y + 5 and x - GameParams.quadrotor_width/2 <= GameParams.pad_x + 2*GameParams.pad_width:
            self.game_over = True
            result = "Game Over -- Ran into landing pad -- Crash \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif x >= GameParams.pad_x and x <= GameParams.pad_x + 2*GameParams.pad_width and y + GameParams.quadrotor_height/2 >= GameParams.pad_y and abs(phi) <= 3*math.pi/(5*180) and math.sqrt(vx**2 + vy**2) <= 15:
            self.game_won = True
            result = "Game Won -- Safe Landing \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif x >= GameParams.pad_x and x <= GameParams.pad_x + 2*GameParams.pad_width and y + GameParams.quadrotor_height/2 >= GameParams.pad_y and (phi <= -math.pi/6 or phi >= math.pi/6 or math.sqrt(vx**2 + vy**2) > 20):
            self.game_won = True
            result = "Game Over -- Unsafe Landing \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif y <= 10: 
            self.game_over = True
            result = "Game Over -- Out of bounds -- Crash \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif y >= GameParams.height - 10:
            self.game_over = True
            result = "Game Over -- Out of bounds -- Crash \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif x <= 10:
            self.game_over = True
            result = "Game Over -- Out of bounds -- Crash \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)
        elif x >= GameParams.width - 10:
            self.game_over = True
            result = "Game Over -- Out of bounds -- Crash \n"
            print(result)
            result += "ux_step: " + str(GameParams.ux_step) + "\n"
            result += "uy_step: " + str(GameParams.uy_step) + "\n"
            result += "min_ux: " + str(GameParams.min_ux) + "\n"
            result += "max_ux: " + str(GameParams.max_ux) + "\n"
            result += "min_uy: " + str(GameParams.min_uy) + "\n"
            result += "max_uy: " + str(GameParams.max_uy) + "\n"
            result += "g: " + str(GameParams.g) + "\n"
            result += "m: " + str(GameParams.m) + "\n"
            result += "Ixx: " + str(GameParams.Ixx) + "\n"
            result += "K: " + str(GameParams.K) + "\n"
            result += "dt: " + str(GameParams.dt) + "\n"
            result += "difficulty: " + ("hard" if GameParams.very_tough else "normal") + "\n"
            game_state.game_over(result)

        return True 
        
    def update(self, game_state):
        return [self]

    def draw(self, screen):
        # draw the pad 
        pygame.draw.rect(screen, (255, 0, 0), (GameParams.pad_x, GameParams.pad_y, 2*GameParams.pad_width, GameParams.pad_height*2))
