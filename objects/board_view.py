import pygame
from .piece_view import PieceView
from .constants import (
    BOARD_POS_X,
    BOARD_POS_Y,
    SQUARE_SIZE,
    SQUARE_COUNT,
    ALPHA_FLAG,
    DARK_COLOR,
    LIGHT_COLOR,
)


class BoardView:
    def __init__(self, window: pygame.Surface, light_color = LIGHT_COLOR, dark_color = DARK_COLOR):
        self.window = window
        self.light_color = light_color
        self.dark_color = dark_color
        self.surface: pygame.Surface = pygame.Surface(
            (SQUARE_COUNT * SQUARE_SIZE, SQUARE_COUNT * SQUARE_SIZE)
        )
        self.highlighted_surface: pygame.Surface = pygame.Surface(
            (SQUARE_COUNT * SQUARE_SIZE, SQUARE_COUNT * SQUARE_SIZE),
            flags=ALPHA_FLAG,
        )
        self.rect: pygame.Rect = self.surface.get_rect(
            topleft=(BOARD_POS_X, BOARD_POS_Y)
        )
        self.highlighted_squares: dict[pygame.Color, tuple[int, int]] = {}
        self._draw_base_board()

    def _draw_base_board(self):
        """
        Colors the board with a checkerboard style, with the first (top-left) square being a light color
        """
        # we go through the board and for each square, we "blit" onto the board the current square.
        for row in range(SQUARE_COUNT):
            for col in range(SQUARE_COUNT):
                self.color_square(row, col)

    def highlight_square(
        self, row_index: int, col_index: int, color: pygame.Color, alpha=128
    ):
        """
        Highlights an individual square by drawing over the semi-transparent highlighted surface

        Args:
            row_index (int): The row index of the square to highlight
            col_index (int): The col index of the square to highlight
            color (pygame.Color): The highlight Color
            alpha (int): Transparency level from 0-255, Optional. Defaults to 128
        """
        square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), flags=ALPHA_FLAG)
        square.fill((*color, alpha))
        self.highlighted_surface.blit(
            square, (col_index * SQUARE_SIZE, row_index * SQUARE_SIZE)
        )

    def draw_all_highlights(self, highlight_dict):
        """
        Clears highlights and redraws highlights onto the highlight surface

        Args:
            color (pygame.Color): The color used to highlight the entire surface
        """
        self.clear_highlights()
        # for color, squares in Highlights:
        for color, squares in highlight_dict.items():
            for square in squares:
                self.highlight_square(*square, color)
        self.window.blit(self.highlighted_surface, (BOARD_POS_X, BOARD_POS_Y))

    def clear_highlights(self):
        self.highlighted_surface.fill((0, 0, 0, 0))

    def color_square(
        self,
        row_index: int,
        col_index: int,
        color: pygame.Color = None,
    ):
        """
        Colors an individual square on the board.
        If no color is provided it colors based on the default checkerboard pattern and its (row, col) position
        """
        if color is None:
            color = (
                self.dark_color if (row_index + col_index) % 2 == 1 else self.light_color
            )
        square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        square.fill(color)
        self.surface.blit(
            square, (col_index * SQUARE_SIZE, row_index * SQUARE_SIZE)
        )

    def draw_all_pieces(self, grid: list[list[int | None]], views_by_piece):
        """
        Draws all pieces located on the board

        Iterates through the board, and for each square that contains a piece calls the
        'draw_piece' method to render it.

        This method assumes all surface details are correctly implemented for any given piece
        """
        for row in range(SQUARE_COUNT):
            for col in range(SQUARE_COUNT):
                contents = grid[row][col]
                if contents is not None:
                    piece_view = views_by_piece[contents]
                    self.draw_piece(piece_view, (row, col))

    def get_abs_pos(self, square: tuple[int, int]) -> tuple[int, int]:
        """
        converts a grid pos (row, col) into a absolute window screen position (x, y)

        The returned position is relative to the gane windows top-left pixel coordinate, based on the boards original position.

        Args:
            row (int): The row on the grid
            col (int): The col on the grid

        Returns:
            tuple[int, int]: The (x, y) screen position of the top-left corner of the square

        Raises:
            ValueError: If the given grid pos (row, col) is not found on the board
        """
        row, col = square
        if not self.in_bounds((row, col)):
            raise ValueError(
                f'No position corresponds to grid position ({row}, {col})'
            )
        return (
            BOARD_POS_X + col * SQUARE_SIZE,
            BOARD_POS_Y + row * SQUARE_SIZE,
        )

    def draw_piece(self, piece_view: PieceView, square: tuple[int, int]):
        """
        Draws the piece on the game window at a specific board position (row, col)

        Assumes the piece's image data has been correctly implemented

        Notes:

            This method should be called after all background and board drawing methods as pieces are drawn on the top of the
            board. Failure to do so may lead to pieces being overwritten

        Args:
            piece (Piece): The Piece to be drawn
            row (int): The row on the board
            col (int): The col on the board
        """
        pos = self.get_abs_pos(square)
        self.window.blit(piece_view.surface, pos)

    def mouse_pos_to_grid(
        self, pos: tuple[int, int]
    ) -> tuple[int, int] | tuple[None, None]:
        """
        Converts a mouse position relative to the window into a grid position relative to the board,
        If the mouse position is out of bounds returns (None, None)

        Args:

            pos (tuple[int, int]): The mouse position

        Returns:

            tuple[int, int] | tuple[None, None]: The grid position (row, col) of the board
            or (None, None) if the mouse is out of bounds
        """
        mouse_x, mouse_y = pos
        if not self.rect.collidepoint(mouse_x, mouse_y):
            return (None, None)

        col = (mouse_x - BOARD_POS_X) // SQUARE_SIZE
        row = (mouse_y - BOARD_POS_Y) // SQUARE_SIZE

        # handles the rare case that they select right most or bottom most edge,
        # leading to row or column value of 8, illegal
        if 0 <= row < 8 and 0 <= col < 8:
            return (int(row), int(col))
        else:
            return (None, None)

    def in_bounds(self, square: tuple[int, int]) -> bool:
        """
        Returns if a position is contained within the board

        Args:
            row(int): The positions row
            col(int): The positions col
        """
        row, col = square
        return (0 <= row < SQUARE_COUNT) and (0 <= col < SQUARE_COUNT)

    def draw_board(self):
        """
        Draws the base board surface on the game window's surface, at the board position.

        Must be called before drawing highlights or pieces.

        """
        self.window.blit(self.surface, (BOARD_POS_X, BOARD_POS_Y))

    def add_highlighted_squares(
        self, color: pygame.Color, squares: list[tuple[int, int]]
    ):
        """
        Sets the highlighted_squares attribute of the board.

        Args:
            squares (list[tuple[int, int]]): A list of (row, col) tuples representing board squares to be highlighted
        """
        self.highlighted_squares[color] = squares

    def clear_highlighted_squares(self):
        """
        Clears the list containing highlighted squares, has no visual component.
        """
        self.highlighted_squares = {}

    def draw_menu(self, promo):
        """
        Draws the promotion menu, on the game window's surface,
        Must be called after background and piece surfaces are drawn
        """
        ## Perhaps move this method out of the board class and into the menu class
        self.window.blit(
            promo.surface, (promo.x + BOARD_POS_X, promo.y + BOARD_POS_Y)
        )
