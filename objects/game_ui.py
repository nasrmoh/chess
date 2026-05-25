from .constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    GREY,
    WHITE,
    SQUARE_SIZE,
    FPS,
    ACTION_MOUSE_PRESSED,
    ACTION_QUIT,
    ACTION_SELECTED_SQUARE,
    ACTION_PROMOTION_OPTION,
    COMMAND_HIGHLIGHT_SQUARES,
    COMMAND_CLEAR_HIGHLIGHTS,
    COMMAND_BUILD_PROMO,
    COMMAND_TEARDOWN_PROMO,
    COMMAND_INITIALIZE_GAME_UI,
    COMMAND_MOVE_PIECE,
    COMMAND_PROMOTE_PAWN,
    PAYLOAD_COLOR,
    PAYLOAD_TEAM_COLOR,
    PAYLOAD_SQUARES,
    PAYLOAD_FROM_SQUARE,
    PAYLOAD_TO_SQUARE,
    PAYLOAD_UPGRADE_TYPE
)
from .promotion_menu import PromotionMenu
from .piece_view import PieceView
import pygame
from pygame.locals import *
from pygame import Surface
from .board_view import BoardView


class GameUI:
    def __init__(self, init_commands):
        # windows done
        # display done
        # view dict
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Chess')
        self.window.fill(GREY)   # ui
        init_command = init_commands[0]
        pieces_by_square = init_command[COMMAND_INITIALIZE_GAME_UI]
        self.sprite_cache = self.__build_sprite_cache(pieces_by_square)
        self.views_by_square = self.__build_views_by_square(pieces_by_square)
        self.board_view = BoardView(self.window)
        self.promotion_menu = None

    def __build_sprite_cache(
        self, pieces_by_square
    ) -> dict[tuple[str, str], Surface]:
        sprite_cache = {}
        for square in pieces_by_square:
            piece_kind, piece_color = pieces_by_square[square]
            if (piece_kind, piece_color) not in sprite_cache:
                if piece_color == WHITE:
                    surface = pygame.image.load(f'./Assets/{piece_kind}_white.png')
                else:
                    surface = pygame.image.load(f'./Assets/{piece_kind}_black.png')
                surface = pygame.transform.smoothscale(
                    surface, (SQUARE_SIZE, SQUARE_SIZE)
                )
                sprite_cache[(piece_kind, piece_color)] = surface
        return sprite_cache

    def __build_views_by_square(self, pieces_by_square):
        views_by_square = {}
        for square in pieces_by_square:
            (kind, color) = pieces_by_square[square]
            views_by_square[square] = PieceView(
                self.sprite_cache[kind, color]
            )
        return views_by_square

    def handle_events(
        self,
    ) -> dict[str, bool | tuple[int, int] | tuple[None, None]]:
        """
        Handles the pygame side of events
        """
        actions = {
            ACTION_QUIT: False,
            ACTION_MOUSE_PRESSED: False,
            ACTION_SELECTED_SQUARE: (None, None),
            ACTION_PROMOTION_OPTION: None,
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
                    actions[
                        ACTION_PROMOTION_OPTION
                    ] = self.promotion_menu.get_valid_promotion_option(
                        mouse_pos
                    )
                else:
                    actions[
                        ACTION_SELECTED_SQUARE
                    ] = self.board_view.mouse_pos_to_grid(mouse_pos)

        return actions

    def render(self, clock):
        clock.tick(FPS)
        self.board_view.draw_board()  # draw board onto the window
        self.board_view.draw_all_highlights(
            self.board_view.highlighted_squares
        )
        self.board_view.draw_all_pieces(
             self.views_by_square
        )  # draw all pieces onto the board
        if self.promotion_menu:
            self.board_view.draw_menu(self.promotion_menu)
        pygame.display.update()

    def apply_commands(self, commands: list[dict]):
        for command in commands:
            ((command_type, payload),) = command.items()
            if command_type == COMMAND_HIGHLIGHT_SQUARES:
                color = payload[PAYLOAD_COLOR]
                squares = payload[PAYLOAD_SQUARES]
                self.board_view.add_highlighted_squares(color, squares)
            elif command_type == COMMAND_CLEAR_HIGHLIGHTS:
                self.board_view.clear_highlighted_squares()
            elif command_type == COMMAND_BUILD_PROMO:
                color = payload
                self.build_promotion_menu(color)
            elif command_type == COMMAND_TEARDOWN_PROMO:
                self.teardown_promo_menu()
            elif command_type == COMMAND_MOVE_PIECE:
                for payload_entry in payload:
                    from_square = payload_entry[PAYLOAD_FROM_SQUARE]
                    to_square = payload_entry[PAYLOAD_TO_SQUARE]
                    self.update_piece_view(from_square, to_square)
            elif command_type == COMMAND_PROMOTE_PAWN:
                from_square = payload[PAYLOAD_FROM_SQUARE]
                piece_type = payload[PAYLOAD_UPGRADE_TYPE]
                piece_color = payload[PAYLOAD_TEAM_COLOR]
                self.upgrade_piece_view(from_square, piece_type, piece_color)



    def build_promotion_menu(self, color):
        self.promotion_menu = PromotionMenu(color)

    def teardown_promo_menu(self):
        self.promotion_menu = None

    def update_piece_view(self, from_square, to_square):
        piece_view = self.views_by_square[from_square]
        self.views_by_square.pop(from_square)
        self.views_by_square[to_square] = piece_view

    def upgrade_piece_view(self, from_square, kind, color):
        new_piece_view = PieceView(
                self.sprite_cache[kind, color]
        )
        self.views_by_square[from_square] = new_piece_view