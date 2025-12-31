import pygame
from copy import deepcopy, copy
from .constants import (
    BOARDPOSX,
    BOARDPOSY,
    ALPHA_FLAG,
    SQUARESIZE,
    SQUARECOUNT,
    PIECE_PAWN,
    PIECE_ROOK,
    PIECE_BISHOP,
    PIECE_KNIGHT,
    PIECE_QUEEN,
)
from .piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from .team import Team


class BoardCore:
    def __init__(self, square_size: int, square_count: int):
        self.square_size = square_size
        self.square_count = square_count
        self.struct: list[list[Piece | None]] = None  # delayed setup

    def init_struct(self):
        """
        This function exists so that virtual boards don't need to populate an empty board
        and can just copy directly. Must be called by objects that require the struct attribute and
        Don't change the initialization.
        """
        self.struct = self._create_board_struct()

    def _create_board_struct(self) -> list[list[Piece | None]]:
        """
        Initializes the structure of the board as a 2D list.
        Each element of the list is either a Piece object or None which represents an empty square.

        Returns:
            list[list[Piece | None]]: a square_count x square_c(ount Grid
        """
        struct = []
        for row_index in range(self.square_count):
            row = []
            for col_index in range(self.square_count):
                row.append(None)
            struct.append(row)
        return struct

    def set_piece(self, piece: Piece):
        """
        Places piece on the board at its specified (row, col) position
        This method is used during setup of games, not for movement of pieces.


        Args:
            piece (Piece) : The piece object with its 'row' and 'col' attributes set

        Raises:
            ValueError: If the target square is already filled
            IndexError: If the specififed location is out of bounds
        """
        # ensures board is empty at location.
        row, col = piece.row, piece.col

        if not self.in_bounds(row, col):
            raise IndexError(f"Board position out of bounds: ({row}, {col})")

        if self.struct[row][col] is None:
            self.struct[row][col] = piece
        else:
            raise ValueError(f"Square is occupied at ({row}, {col})")

    def is_empty(self, row: int, col: int) -> bool:
        """
        Checks if given square is empty

        Args:
            row (int): The row of the square
            col (int): The column of the square

        Raises:
            IndexError: if the position (row, col) is not valid
        """
        if not self.in_bounds(row, col):
            raise IndexError(f"Position out of bounds: ({row}, {col})")
        return self.get_square_contents(row, col) is None

    def get_square_contents(self, row: int, col: int) -> Piece | None:
        """
        Returns the piece at the board position board(row, col), or None if the square is empty
        input :
            row (int) : 0-indexed
            col (int) : 0-indexed
        Raises :
            ValueError if row or column are out of bounds
        """
        if not (0 <= row < SQUARECOUNT and 0 <= col < SQUARECOUNT):
            raise ValueError("Invalid row or column")
        return self.struct[row][col]

    def generate_valid_moves(
        self,
        piece: Piece,
    ):
        if piece is not None:
            valid_moves = piece.generate_valid_moves(self)
            return valid_moves

    def generate_legal_moves(
        self, piece: Piece | None, team: Team, enemy: Team
    ) -> list[tuple[int, int]]:
        """
        Returns the legal moves for a given piece.
        Currently only returns valid moves as determined by the piece.
        In the future it will filter out moves that are illegal. i.e. a move that would lead to a checkmate.
 
        """
        is_king = False
        legal_moves = []
        # first generate valid moves.
        if piece.get_type() == "king":
            is_king = True
        valid_moves = piece.generate_valid_moves(self)
        # now filter for legal moves
        for move in valid_moves:
            ghost_piece = copy(piece)
            ghost_board = VirtualBoard(self)
            # apply the move
            ghost_board.move_piece(ghost_piece, *move)
            if not ghost_board.get_checking_pieces(
                team, enemy, move, is_king
            ):  # king not in check
                legal_moves.append(move)
        # This is done by simulating the move and checking if the king is in check
        return legal_moves

    def build_move_dict(
        self, team: Team, enemy: Team
    ) -> dict[Piece, list[tuple[int, int]]]:
        move_dict = {}
        for piece in team.get_active_pieces():
            move_dict[piece] = self.generate_legal_moves(piece, team, enemy)
        return move_dict

    def in_bounds(self, row: int, col: int) -> bool:
        """
        Returns if a position is contained within the board

        Args:
            row(int): The positions row
            col(int): The positions col
        """
        return (0 <= row < SQUARECOUNT) and (0 <= col < SQUARECOUNT)

    def set_pieces(self, dark_pieces: list[Piece], light_pieces: list[Piece]):
        """
        Sets the dark pieces and light pieces for the corresponding players.

        Assumes each piece has their 'row' and 'col' attributes setup

        This method is only used for setting up all pieces, not moving groups of pieces.

        Args:
            dark_pieces(list[Piece]): The pieces for the player who plays the dark pieces
            light_pieces(list[Piece]): The pieces for the player who plays the light pieces

        Raises:
            ValueError: If a piece is a placed on a square that is already occupied
        """
        for black_piece in dark_pieces:
            self.set_piece(black_piece)
        for white_piece in light_pieces:
            self.set_piece(white_piece)

    def move_piece(self, piece: Piece, dest_row: int, dest_col: int) -> Piece | None:
        """
        moves the given piece by updating both the pieces attributes and the boards structure.
        If a piece is located at the destination square, it is "captured" by removing it from the board structure
        and is returned.

        This method does not handle drawing or rendering only piece and board logic.

        Args:
            piece (Piece): The piece that is being moved
            dest_row (int): The row the piece will move to
            dest_col (int): THe col the piece will move to

        Returns:
            (Piece | None): Returns a captured piece if any, else returns None
        """
        # Move piece by updating piece parameters
        if piece.is_valid_move(dest_row, dest_col, self):
            captured_piece = self.get_square_contents(dest_row, dest_col)
            (old_row, old_col) = piece.apply_move(
                dest_row, dest_col
            )  # update piece parameters
            piece.update_after_move()
            # update board parameters
            self.struct[old_row][old_col] = None
            self.struct[dest_row][dest_col] = piece
            return captured_piece

    def upgrade_piece(self, team: Team, piece: Piece, dest_type: str) -> Piece:
        """
        Upgrades a pawn piece into a new type (rook, bishop, knight or queen).

        Args:
            team (Team): The team the pawn belongs to.
            piece (Piece): The pawn piece to be upgraded
            dest_type (str): The type the piece will be upgraded to

        Returns:
            Piece: The upgraded piece

        Raises:
            TypeError: If the piece is not a pawn, or if the piece does not belong to the given player / team
            ValueError: If the dest_type is invalid
        """
        row, col, color = piece.row, piece.col, piece.color
        upgrade_selection = {
            PIECE_ROOK: Rook,
            PIECE_BISHOP: Bishop,
            PIECE_KNIGHT: Knight,
            PIECE_QUEEN: Queen,
        }
        if piece.type != PIECE_PAWN:
            raise TypeError(f"piece : {piece.type} cannot be promoted")
        if not team.owns(piece):
            raise TypeError(f"piece : {piece.type} does not belong to team")
        if dest_type not in upgrade_selection:
            raise ValueError(f"Invalid upgrade type : {dest_type}")
        piece_class = upgrade_selection[dest_type]
        new_piece = piece_class(color, row, col, dest_type)
        self.struct[new_piece.row][new_piece.col] = new_piece
        team.active_pieces.remove(piece)
        team.active_pieces.append(new_piece)
        return new_piece

    def get_checking_pieces(self, current_player: Team, enemy_team: Team):
        checking_pieces = {}
        kings_grid_pos = current_player.king.get_grid_pos()

        for enemy_piece in enemy_team.get_active_pieces():
            enemy_pieces_moves = self.generate_valid_moves(enemy_piece)
            if kings_grid_pos in enemy_pieces_moves:
                enemy_piece_current_pos = enemy_piece.get_grid_pos()
                checking_pieces[enemy_piece] = enemy_piece_current_pos

        return checking_pieces


"""    def squares_empty_between_col(self, init_row, init_col, fin_row, fin_col):
        
        Checks that the squares between initial square and final square are
        empty, Does not include the initial and final
        
        if init_row != fin_row:
            raise ValueError("Rows must be identical to compare")

        if fin_col < init_col:
            temp = fin_col
            fin_col = init_col
            init_col = temp

        remove_edges = 1
        col_diff = fin_col - init_col - remove_edges
        for i in range(col_diff):"""



        




class GameBoard(BoardCore):
    """
    Represents a NxN checkerboard

    Args:
        square_size (int): The pixel size of each individual square
        square_count (int): The number of squares in a given row or column i.e. board is square_count x square_count
        color_dark (pygame.Color): The color of the dark squares
        color_light (pygame.Color): The color of the light squares
        window (pygame.Surface): The game window's surface

    Attributes:
        struct (list[list[Piece | None]]): 2D grid storing pieces or None
        surface (pygame.Surface): Base surface / Image of the board
        highlighted_surface (pygame.Surface): Transparent overlay surface for highlighting
        rect (pygame.Rect): Position and size of the board relative to the window
        highlighted_squares list[tuple[int, int]]: Squares which are to be highlighted stored as a list of (row,col) tuples.

    """

    def __init__(
        self,
        square_size: int,
        square_count: int,
        color_dark: pygame.Color,
        color_light: pygame.Color,
        window: pygame.Surface,
    ):
        super().__init__(square_size, square_count)
        self.init_struct()
        self.color_light: pygame.Color = color_light
        self.color_dark: pygame.Color = color_dark
        self.window: pygame.Surface = window
        self.pos_x = BOARDPOSX
        self.pos_y = BOARDPOSY
        self.surface: pygame.Surface = pygame.Surface(
            (square_count * square_size, square_count * square_size)
        )
        self.highlighted_surface: pygame.Surface = pygame.Surface(
            (square_count * square_size, square_count * square_size), flags=ALPHA_FLAG
        )
        self.rect: pygame.Rect = self.surface.get_rect(topleft=(self.pos_x, self.pos_y))
        self._draw_base_board()
        self.highlighted_squares: dict[pygame.Color, tuple[int, int]] = {}

    def _draw_base_board(self):
        """
        Colors the board with a checkerboard style, with the first (top-left) square being the self.light_color
        """
        # we go through the board and for each square, we "blit" onto the board the current square.
        for row in range(self.square_count):
            for col in range(self.square_count):
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
        square = pygame.Surface((SQUARESIZE, SQUARESIZE), flags=ALPHA_FLAG)
        square.fill((*color, alpha))
        self.highlighted_surface.blit(
            square, (col_index * SQUARESIZE, row_index * SQUARESIZE)
        )

    def draw_highlights(self, highlight_dict):
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
        self.window.blit(self.highlighted_surface, (self.pos_x, self.pos_y))

    def clear_highlights(self):
        self.highlighted_surface.fill((0, 0, 0, 0))

    def color_square(
        self,
        row_index: int,
        col_index: int,
        color: pygame.Color = None,
        highlight: bool = False,
    ):
        """
        Colors an individual square on the board.
        If no color is provided it colors based on the default checkerboard pattern and its (row, col) position
        If highlight is True, a semi-transparent version of the color is provided

        Args:
            row_index (int) : The row index of the square
            col_index (int) : the col_index of the square
            Color (pygame.Color, optional) : the color of the square, if None defaults to dark / light
            highlight (bool, optional) : Flag to check if semi-transparent highlight is used. Default is False

        """
        square = pygame.Surface((SQUARESIZE, SQUARESIZE))
        if color is None:
            color = (
                self.color_dark
                if (row_index + col_index) % 2 == 1
                else self.color_light
            )
        flags = ALPHA_FLAG if highlight else 0
        square = pygame.Surface((SQUARESIZE, SQUARESIZE), flags=flags)
        if highlight:
            square.fill(*color, 128)
        else:
            square.fill(color)
        self.surface.blit(square, (col_index * SQUARESIZE, row_index * SQUARESIZE))

    def draw_pieces(self):
        """
        Draws all pieces located on the board

        Iterates through the board, and for each square that contains a piece calls the
        'draw_piece' method to render it.

        This method assumes all surface details are correctly implemented for any given piece
        """
        for row in range(self.square_count):
            for col in range(self.square_count):
                contents = self.get_square_contents(row, col)
                if contents is not None:
                    self.draw_piece(contents, row, col)

    def get_abs_pos(self, row: int, col: int) -> tuple[int, int]:
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
        if not self.in_bounds(row, col):
            raise ValueError(f"No position corresponds to grid position ({row}, {col})")
        return (
            self.pos_x + col * self.square_size,
            self.pos_y + row * self.square_size,
        )

    def draw_piece(self, piece: Piece, row: int, col: int):
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
        pos = self.get_abs_pos(row, col)
        self.window.blit(piece.surface, pos)

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

        col = (mouse_x - self.pos_x) // SQUARESIZE
        row = (mouse_y - self.pos_y) // SQUARESIZE

        # handles the rare case that they select right most or bottom most edge,
        # leading to row or column value of 8, illegal
        if 0 <= row < 8 and 0 <= col < 8:
            return (int(row), int(col))
        else:
            return (None, None)

    def draw_board(self):
        """
        Draws the base board surface on the game window's surface, at the board position.

        Must be called before drawing highlights or pieces.

        """
        self.window.blit(self.surface, (self.pos_x, self.pos_y))

    def draw_menu(self, promo):
        """
        Draws the promotion menu, on the game window's surface,
        Must be called after background and piece surfaces are drawn
        """
        ## Perhaps move this method out of the board class and into the menu class
        self.window.blit(promo.surface, (promo.x + self.pos_x, promo.y + self.pos_y))

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


class VirtualBoard(BoardCore):
    def __init__(self, board):
        super().__init__(board.square_size, board.square_count)
        # VirtualBoard changes the initailization of the struct object so it does not make a call to
        # BoardCore.init_struct
        self.square_count = board.square_count
        self.struct = self.copy(board.struct)

    def get_checking_pieces(
        self, current_player: Team, enemy_team: Team, move=None, is_king=False
    ):
        checking_pieces = {}
        if is_king:
            kings_grid_pos = move
        else:
            kings_grid_pos = current_player.king.get_grid_pos()

        for enemy_piece in enemy_team.get_active_pieces():
            if enemy_piece.get_grid_pos() == move:
                continue
            enemy_pieces_moves = self.generate_valid_moves(enemy_piece)
            if kings_grid_pos in enemy_pieces_moves:
                enemy_piece_current_pos = enemy_piece.get_grid_pos()
                checking_pieces[enemy_piece] = enemy_piece_current_pos

        return checking_pieces

    def copy(self, lst: list[Piece]):
        grid = []
        for row in range(self.square_count):
            grid_row = []
            for col in range(self.square_count):
                grid_row.append(lst[row][col])
            grid.append(grid_row)
        return grid
