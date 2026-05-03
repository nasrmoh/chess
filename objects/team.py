from .constants import BLACK, WHITE
from .piece import Piece, King
class Team:
    """
    Represents a "team" of pieces.

    Args:
        team_id (int): The team ID, 0 represents dark pieces and 1 represents light pieces.
        color (pygame.Color): The color of the associated pieces.

    Attributes:
        team_id (int): The team ID, 0 represents dark pieces and 1 represents light pieces.
        color (pygame.Color): The color of the associated pieces.
        active_pieces (list[Piece]): A list of pieces that are currently in play
        captured_pieces (list[Piece]): A list of pieces that belong to the player and have been captured.
    """

    def __init__(self, team_id: int, color: str):
        self.team_id: int = team_id
        self.color: str = color
        self.active_pieces: list[Piece] = []
        self.captured_pieces: list[Piece] = []

    def __str__(self):
        if self.color == BLACK:
            return 'Black Player'
        elif self.color == WHITE:
            return 'White Player'
        else:
            raise ValueError('Invalid Color')

    def owns(self, piece: Piece) -> bool:
        """
        Checks that a piece belongs to a given team, Returns True if the piece has the same color as the team

        Args:
            piece (Piece): The piece that we are comparing to,

        """
        return self.color == piece.color

    def set_king_pid(self, king):
        self.king = king

    def set_king_in_check(self, cond):
        self.get_king().set_in_check(cond)

    def get_king(self):
        return self.king

    def get_active_pieces(self):
        return self.active_pieces

    def get_count_active(self):
        return len(self.active_pieces)

    def get_count_captured(self):
        return len(self.captured_pieces)
