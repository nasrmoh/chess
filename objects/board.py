from copy import deepcopy, copy
from .constants import (
    SQUARECOUNT,
    PIECE_PAWN,
    PIECE_ROOK,
    PIECE_BISHOP,
    PIECE_KNIGHT,
    PIECE_QUEEN,
)
from .piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from .team import Team


class GameBoard:
    def __init__(self, square_size: int, square_count: int):
        self.square_size = square_size
        self.square_count = square_count
        self.struct: list[list[Piece | None]] = None  # delayed setup
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



class VirtualBoard(GameBoard):
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
