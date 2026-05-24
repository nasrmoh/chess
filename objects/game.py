import pygame

from .game_state import  GameState
from .game_ui import GameUI
from .constants import ACTION_QUIT

# =============================================================================
# TODO: Actions & Commands
# =============================================================================
#
# ACTIONS (GameUI -> GameState)
# -------------------------------------------------------
# - SELECT_SQUARE       payload: square
# - MOVE_PIECE          payload: from_square, to_square
#
# COMMANDS (GameState -> GameUI)
# -------------------------------------------------------
# - COMMAND_INITIALIZE_GAME_UI      payload: {square: (kind, color)} - completed
# - COMMAND_MOVE_PIECE              payload: from_square, to_square - completed
# - COMMAND_CAPTURE_PIECE           payload: square - Wasn't needed
# - COMMAND_PROMOTE_PAWN            payload: square, kind, color, - completed
#
# NOTE: Handlers for COMMAND_MOVE_PIECE, COMMAND_CAPTURE_PIECE,
#       and COMMAND_PROMOTE_PAWN not yet implemented in GameUI.
#       views_by_square must be updated accordingly in each handler.
# =============================================================================


class Game:
    def __init__(self):
        self.state = GameState()
        init_commands = self.state.get_init_commands()
        self.ui = GameUI(init_commands)
        self.clock = pygame.time.Clock()


    def run(self):
        pygame.init()
        while self.state.get_game_is_running():
            actions = self.ui.handle_events()
            commands = self.state.update_state(actions)
            self.ui.apply_commands(commands)
            self.ui.render(self.clock)
        pygame.quit()
