from .constants import BLACK, WHITE
from .piece import Piece, King


class Team:

    def __init__(self, color: str):
        self.color: str = color
        self.active_pieces: list[Piece] = []
        self.lost_pieces: list[Piece] = []
        self.king: King | None = None

    def __str__(self):
        if self.color == BLACK:
            return "Black Player"
        elif self.color == WHITE:
            return "White Player"
        else:
            raise ValueError("Invalid Color")

    def replace_piece(self, old_piece: Piece, new_piece: Piece):
        if old_piece not in self.active_pieces:
            raise ValueError(f"{old_piece.kind} not found in active pieces")
        self.active_pieces.remove(old_piece)
        self.active_pieces.append(new_piece)

    def owns(self, piece: Piece) -> bool:
        return self.color == piece.color

    def set_king_pid(self, king):
        self.king = king

    def set_king_in_check(self, cond):

        self.get_king().set_in_check(cond)

    def get_king(self):
        return self.king

    def get_count_active(self):
        return len(self.active_pieces)
