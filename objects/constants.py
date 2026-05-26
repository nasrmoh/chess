import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_TO_BOARD_RATIO = 1
SQUARE_COUNT = 8
ALPHA_FLAG = pygame.SRCALPHA
BOARD_SIDE_LENGTH = WINDOW_WIDTH * WINDOW_TO_BOARD_RATIO
SQUARE_SIZE = int(BOARD_SIDE_LENGTH / SQUARE_COUNT)
BOARD_POS_X = (WINDOW_WIDTH - BOARD_SIDE_LENGTH) / 2
BOARD_POS_Y = (WINDOW_HEIGHT - BOARD_SIDE_LENGTH) / 2
FPS = 60
EMPTY = None
DIAGONALS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
CARDINALS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
KNIGHT_OFFSET = [
    (-2, 1),
    (-2, -1),
    (2, 1),
    (2, -1),
    (1, 2),
    (-1, 2),
    (1, -2),
    (-1, -2),
]

ROOK = "rook"
BISHOP = "bishop"
KNIGHT = "knight"
QUEEN = "queen"
PAWN = "pawn"
KING = "king"


DARK_COLOR = (102, 0, 0)
LIGHT_COLOR = (185, 122, 87)
WHITE = "white"
BLACK = "black"
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
GREY = (119, 136, 153)
BLUE = (0, 0, 255)
INITIAL_POSITION = {
    WHITE: {
        ROOK: [(7, 0), (7, 7)],
        KNIGHT: [(7, 1), (7, 6)],
        BISHOP: [(7, 2), (7, 5)],
        QUEEN: [(7, 3)],
        KING: [(7, 4)],
        PAWN: [(6, i) for i in range(8)],
    },
    BLACK: {
        ROOK: [(0, 0), (0, 7)],
        KNIGHT: [(0, 1), (0, 6)],
        BISHOP: [(0, 2), (0, 5)],
        QUEEN: [(0, 3)],
        KING: [(0, 4)],
        PAWN: [(1, i) for i in range(8)],
    },
}

KING_SIDE = "king_side"
QUEEN_SIDE = "queen_side"

CASTLE_POSITION = {
    WHITE : {
        KING_SIDE : {
            KING : (7, 6),
            ROOK : (7, 5)
        },
        QUEEN_SIDE : {
            KING : (7, 2),
            ROOK : (7, 3)
        }
    },
    BLACK : {
        KING_SIDE : {
            KING : (0, 6),
            ROOK : (0, 5)
        },
        QUEEN_SIDE : {
            KING : (0, 2),
            ROOK : (0, 3)
        }
    }
}

KSK_COL = 6
KSR_COL = 5
QSK_COL = 2
QSR_COL = 3


PROMOTION_SELECTOR = {
    0 : ROOK,
    1 : BISHOP,
    2 : KNIGHT,
    3 : QUEEN
}
GAME_START = "game_start"
START_TURN = "start_turn"
SELECT_PIECE = "select_piece"
SELECT_MOVE = "select_move"
SELECT_PROMOTION = "select_promotion"
END_TURN = "end_turn"
GAME_END = "game_end"
BLACK_PLAYER = "player_one"
WHITE_PLAYER = "player_two"
ACTION_QUIT = "quit"
ACTION_MOUSE_PRESSED = "mouse_pressed"
ACTION_SELECTED_SQUARE = "selected_square"
ACTION_PROMOTION_OPTION = "promotion_option"
COMMAND_HIGHLIGHT_SQUARES = "highlight_squares"
COMMAND_CLEAR_HIGHLIGHTS = "clear_highlights"
COMMAND_BUILD_PROMO = "build_promotion_menu"
COMMAND_TEARDOWN_PROMO = "teardown_promo"
COMMAND_INITIALIZE_GAME_UI = "initialize_game_ui"
COMMAND_APPLY_MOVE = "apply_move"
COMMAND_CAPTURE_PIECE = "capture_piece"
COMMAND_PROMOTE_PAWN = "promote_pawn"
COMMAND_DELETE_ENPASSANTED_PIECE = "delete_enpassanted_piece"
PAYLOAD_COLOR = "payload_color"
PAYLOAD_TEAM_COLOR = "payload_TEAM_color"
PAYLOAD_SQUARES = "payload_squares"
PAYLOAD_FROM_SQUARE = "payload_from_square"
PAYLOAD_TO_SQUARE = "payload_to_square"
PAYLOAD_CAPTURED_PIECE = "payload_captured_piece"
PAYLOAD_UPGRADE_TYPE = "payload_upgrade_type"
MOVE_NORMAL = "move_normal"
MOVE_CAPTURE = "move_capture"
MOVE_ENPASSANT = "move_enpassant"
MOVE_CASTLE = "move_castle"

