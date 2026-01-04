import pygame
import sys
from random import randint
from objects.constants import (
    WINDOWWIDTH,
    WINDOWHEIGHT,
    SQUARESIZE,
    SQUARECOUNT,
    DARKCOLOR,
    LIGHTCOLOR,
    WHITEPLAYER,
    BLACKPLAYER,
    BLACK,
    WHITE,
    GREY,
)


from objects.board import GameBoard
from objects.game_state import GameState
from objects.game_ui import GameUI
from objects.team import Team




def setup():
    game_state = GameState()
    game_ui = GameUI(game_state)
    return game_state, game_ui, pygame.time.Clock()

def main():
    # Setup and Initialization
    pygame.init()
    game_state, game_ui, clock = setup()
    actions = {}
    commands = []
    while game_state.get_game_is_running():
        actions = game_ui.handle_events()
        commands = game_state.update_state(actions)
        game_ui.apply_commands(commands)
        game_ui.render(clock)
    pygame.quit()


if __name__ == '__main__':
    main()
