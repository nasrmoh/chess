from .constants import (
    WINDOWWIDTH,
    WINDOWHEIGHT,
    GREY,
    WHITE, 
    SQUARESIZE, 
    FPS, 
    ACTION_MOUSE_PRESSED, 
    ACTION_QUIT, 
    ACTION_SELECTED_SQUARE,
    ACTION_PROMOTION_OPTION,
    COMMAND_HIGHLIGHT_SQUARES,
    COMMAND_CLEAR_HIGHLIGHTS,
    COMMAND_BUILD_PROMO,
    COMMAND_TEARDOWN_PROMO,
    PAYLOAD_COLOR,
    PAYLOAD_SQUARES
    )
from .game_state import GameState
from .promotion_menu import PromotionMenu
from .piece_view import PieceView
import pygame
import sys
from pygame.locals import *
from pygame import Surface
from .board_view import BoardView


        
class GameUI:
    def __init__(self, game_state : GameState):
        # windows done
        # display done
        # view dict 
        self.game_state = game_state
        self.window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) 
        pygame.display.set_caption('Chess')
        self.window.fill(GREY) #ui
        self.sprite_cache = self.__build_sprite_cache(game_state)
        self.views_by_id = self.__build_views_by_id()
        self.board_view = BoardView(self.window)
        self.promotion_menu = None

    def __build_sprite_cache(self, game_state : GameState) -> dict[tuple[str, str], Surface]:
        sprite_cache = {}
        pieces_by_id = game_state.board.pieces_by_id
        for piece in set(pieces_by_id.values()): # may cause problems
            piece_kind = piece.kind
            piece_color = piece.color
            if  piece_color == WHITE:
                surface = pygame.image.load(f"./Assets/{piece_kind}_white.png")
            else:
                surface = pygame.image.load(f"./Assets/{piece_kind}_black.png")
            surface = pygame.transform.smoothscale(surface, (SQUARESIZE, SQUARESIZE))
            sprite_cache[(piece_kind, piece_color)] = surface
        return sprite_cache

    def __build_views_by_id(self):
        pieces_by_id = self.game_state.board.pieces_by_id
        views_by_id = {}
        for id, piece in pieces_by_id.items():
            views_by_id[id] = PieceView(self.sprite_cache[piece.kind, piece.color])
        return views_by_id

    def handle_events(self) -> dict[str, bool | tuple[int, int] | tuple[None, None]]:
        """
        Handles the pygame side of events
        """
        actions = {
            ACTION_QUIT : False,
            ACTION_MOUSE_PRESSED : False, 
            ACTION_SELECTED_SQUARE : (None, None),
            ACTION_PROMOTION_OPTION : (None)
        }
        for event in pygame.event.get():
            if event.type == QUIT:
                actions[ACTION_QUIT] = True 
                # pygame.quit()
                # sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                actions[ACTION_MOUSE_PRESSED] = True
                mouse_pos = event.pos
                if self.promotion_menu:
                    actions[ACTION_PROMOTION_OPTION] = self.promotion_menu.get_valid_promotion_option(mouse_pos)
                else:
                    actions[ACTION_SELECTED_SQUARE] = self.board_view.mouse_pos_to_grid(mouse_pos)

        return actions

    def render(self, clock):
        clock.tick(FPS)
        self.board_view.draw_board()  # draw board onto the window
        self.board_view.draw_all_highlights(self.board_view.highlighted_squares)
        self.board_view.draw_all_pieces(self.game_state.board.struct, self.views_by_id)  # draw all pieces onto the board
        if self.promotion_menu:
            self.board.draw_menu(self.promotion_menu)
        pygame.display.update()

    def apply_commands(self, commands : list[dict]):
        for command in commands:
            (command_type, payload), = command.items()
            if command_type == COMMAND_HIGHLIGHT_SQUARES:
                color = payload[PAYLOAD_COLOR]
                squares = payload[PAYLOAD_SQUARES]
                self.board_view.add_highlighted_squares(color, squares)
            elif command_type == COMMAND_CLEAR_HIGHLIGHTS:
                self.board_view.clear_highlighted_squares()
            elif command_type == COMMAND_BUILD_PROMO:
                color = payload[PAYLOAD_COLOR]
                self.build_promotion_menu(color)
            elif command_type == COMMAND_TEARDOWN_PROMO:
                self.teardown_promo_menu()
        
    def build_promotion_menu(self, color):
        self.promotion_menu = PromotionMenu(color)

    def teardown_promo_menu(self):
        self.promotion_menu = None 