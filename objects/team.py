import pygame
from .constants import (
    SQUARECOUNT,
    WHITEPLAYER,
    PIECE_ROOK,
    PIECE_KNIGHT,
    PIECE_BISHOP,
    PIECE_QUEEN,
)
from .piece import Piece, Pawn, Rook, Bishop, Knight, King, Queen


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

    def __init__(self, team_id: int, color: pygame.Color):
        self.team_id: int = team_id
        self.color: pygame.Color = color
        self.active_pieces: list[Piece] = []
        self.captured_pieces: list[Piece] = []

    def __str__(self):
        if self.color == (0, 0, 0):
            return "Black Player"
        elif self.color == (255, 255, 255):
            return "White Player"
        else:
            raise ValueError("Invalid Color")

    

    def owns(self, piece: Piece) -> bool:
        """
        Checks that a piece belongs to a given team, Returns True if the piece has the same color as the team

        Args:
            piece (Piece): The piece that we are comparing to,

        """
        return self.color == piece.color
    
    def set_king_id(self, king_id):
        self.king_id = king_id

    def get_king_id(self):
        return self.king_Id

    def get_active_pieces(self):
        return self.active_pieces

    def get_count_active(self):
        return len(self.active_pieces)

    def get_count_captured(self):
        return len(self.captured_pieces)
