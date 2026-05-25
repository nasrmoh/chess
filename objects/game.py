import pygame

from .game_state import  GameState
from .game_ui import GameUI

# =============================================================================
# TODO: Move System Refactor
# =============================================================================
#
# MOVE CLASS (lean, used during move generation and execution)
# -------------------------------------------------------
# - from_square       tuple[int, int]
# - to_square         tuple[int, int]
# - kind              NORMAL | CAPTURE | EN_PASSANT | CASTLE
# - payload           optional, shape depends on kind:
#       CAPTURE       -> captured piece's current square
#       EN_PASSANT    -> pawn to capture's current square
#       CASTLE        -> rook's from and to squares
#
# board.move_piece switches on move.kind to handle extra work
#   - CASTLE:     also moves the rook
#   - EN_PASSANT: removes the captured pawn from its actual square
#   - CAPTURE:    standard capture handling
#
# NOTE: UI integration — board.move_piece will need to communicate
#       extra changes (rook movement, en passant removal) back via
#       commands. Consider how COMMAND_MOVE_PIECE handles multi-piece moves.
#       Probably can just change COMMAND_MOVE_PIECE -> COMMAND_MOVE_PIECES or.
#       COMMAND_EXECUTE_MOVE ????
#
# MOVE HISTORY
# -------------------------------------------------------
# - MoveHistory     container, wraps list of HistoryEntry objects
# - HistoryEntry    element, wraps a Move with extra data needed
#                   for reversal (e.g. promotion reversal kind)
#
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
