import pygame

from .game_state import  GameState
from .game_ui import GameUI

class Game:
    def __init__(self):
        self.state = GameState()
        self.ui = GameUI(self.state)
        self.clock = pygame.time.Clock()


    def run(self):
        pygame.init()
        while self.state.get_game_is_running():
            actions = self.ui.handle_events()
            commands = self.state.update_state(actions)
            self.ui.apply_commands(commands)
            self.ui.render(self.clock)
        pygame.quit()
