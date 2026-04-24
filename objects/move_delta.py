from .constants import NORMAL, CASTLE, ENPASSANT, PROMOTION
from .piece import Piece


class CastleData:
    def __init__(
        self,
        rook_from: tuple[int, int],
        rook_to: tuple[int, int],
        rook_previous_moved: bool,
    ):
        self.rook_from = rook_from
        self.rook_to = rook_to
        self.rook_previous_moved = rook_previous_moved

    def get_rook_from(self):
        return self.rook_from

    def get_rook_to(self):
        return self.rook_to

    def get_rook_previous_moved(self):
        return self.rook_previous_moved


class EnpassantData:
    def __init__(self, captured_square: tuple[int, int]):
        self.captured_square = captured_square

    def get_captured_square(self):
        return self.captured_square


class PromotionData:
    def __init__(self, choice: str = None):
        self.choice = choice

    def get_choice(self):
        return self.choice


class MoveDelta:
    def __init__(
        self,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
        piece: Piece,
        previous_has_moved: bool,
        extra_data: None | CastleData | EnpassantData | PromotionData,
        captured_piece: None | Piece = None,
    ):
        self.from_square = from_square
        self.to_square = to_square
        self.piece = piece
        self.previous_has_moved = previous_has_moved
        self.extra_data = extra_data
        self.captured_piece = captured_piece

    def get_from_square(self):
        return self.from_square

    def get_to_square(self):
        return self.to_square

    def get_piece(self):
        return self.piece

    def get_captured_piece(self):
        return self.captured_piece

    def get_extra_data(self):
        return self.extra_data
