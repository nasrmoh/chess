import pygame
from .piece import Piece
from .constants import (
    WHITE,
    SQUARE_SIZE,
    BOARDPOSX,
    BOARDPOSY,
)


class PieceView:
    def __init__(self, surface):
        self.surface = surface
