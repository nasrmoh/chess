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
    def __init__(
        self,
        square_size: int,
        square_count: int,
        grid: list[list] = None,
        pieces_by_id: dict = None,
    ):
        self.square_size = square_size
        self.square_count = square_count
        self.struct: list[list[Piece | None]] = None  # delayed setup
        if pieces_by_id is not None:
            self.pieces_by_id = pieces_by_id
        else:
            self.pieces_by_id = {}
        if not grid:
            self.struct = self._create_board_struct()
        else:
            self.struct = grid

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

    def __build_pieces_by_id_dict(self) -> dict[int, Piece]:
        light_pieces = self.light_team.active_pieces
        dark_pieces = self.dark_team.active_pieces
        pieces_by_id = {}
        id_count = 0
        for piece in light_pieces:
            pieces_by_id[id_count] = piece
            id_count += 1
        for piece in dark_pieces:
            pieces_by_id[id_count] = piece
            id_count += 1
        return pieces_by_id

    def square_by_id(self, id) -> tuple[int, int]:

        for row in range(SQUARECOUNT):
            for col in range(SQUARECOUNT):
                if self.struct[row][col] == id:
                    return (row, col)
        raise IndexError('Id not found on board')

    def set_piece(self, id, row, col):
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

        if not self.in_bounds((row, col)):
            raise IndexError(f'Board position out of bounds: ({row}, {col})')

        if self.struct[row][col] is None:
            self.struct[row][col] = id
        else:
            raise ValueError(f'Square is occupied at ({row}, {col})')

    def is_empty(self, square: tuple[int, int]) -> bool:
        """
        Checks if given square is empty

        Args:
            row (int): The row of the square
            col (int): The column of the square

        Raises:
            IndexError: if the position (row, col) is not valid
        """
        row, col = square
        if not self.in_bounds((row, col)):
            raise IndexError(f'Position out of bounds: ({row}, {col})')
        return self.get_square_contents((row, col)) is None

    def get_square_contents(self, square: tuple[int, int]) -> Piece | None:
        """
        Returns the piece at the board position board(row, col), or None if the square is empty
        input :
            row (int) : 0-indexed
            col (int) : 0-indexed
        Raises :
            ValueError if row or column are out of bounds
        """
        row, col = square
        if not (0 <= row < SQUARECOUNT and 0 <= col < SQUARECOUNT):
            raise ValueError('Invalid row or column')
        return self.struct[row][col]

    def generate_valid_moves(self, id: int, from_square: tuple[int, int]):
        if id is not None:
            piece: Piece = self.pieces_by_id[id]
            valid_moves = piece.generate_valid_moves(from_square, self)
            return valid_moves

    def generate_legal_moves(
        self,
        id: int | None,
        from_square: tuple[int, int],
        team: Team,
        enemy: Team,
    ) -> list[tuple[int, int]]:
        """
        Returns the legal moves for a given piece.
        Currently only returns valid moves as determined by the piece.
        In the future it will filter out moves that are illegal. i.e. a move that would lead to a checkmate.
        """
        is_king = False
        legal_moves = []
        piece: Piece = self.pieces_by_id[id]
        # first generate valid moves.
        if piece.get_kind() == 'king':
            is_king = True
        valid_moves = piece.generate_valid_moves(from_square, self)
        # now filter for legal moves
        for move in valid_moves:
            ghost_piece = copy(piece)
            ghost_board = GameBoard(
                self.square_size,
                self.square_count,
                self.clone_grid(),
                self.pieces_by_id,
            )
            # apply the move
            ghost_board.move_piece(ghost_piece, from_square, move)
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
        found_count = 0
        ally_count = team.get_count_active()
        for row in range(SQUARECOUNT):
            for col in range(SQUARECOUNT):
                if found_count == ally_count:
                    break
                contents = self.get_square_contents((row, col))
                if (contents is not None) and (
                    self.pieces_by_id[contents].color == team.color
                ):
                    team_piece_id = contents
                    piece = self.pieces_by_id[contents]
                    found_count += 1
                    move_dict[piece] = self.generate_legal_moves(
                        team_piece_id, (row, col), team, enemy
                    )
        return move_dict

    def in_bounds(self, square: tuple[int, int]) -> bool:
        """
        Returns if a position is contained within the board

        Args:
            row(int): The positions row
            col(int): The positions col
        """
        row, col = square
        return (0 <= row < SQUARECOUNT) and (0 <= col < SQUARECOUNT)

    def setup_pieces(self, dark_team: Team, light_team: Team):

        non_pawn_pieces = []
        rook = Rook(dark_team.color, 'rook')
        knight = Knight(dark_team.color, 'knight')
        bishop = Bishop(dark_team.color, 'bishop')
        queen = Queen(dark_team.color, 'queen')
        king = King(dark_team.color, 'king')
        bishop1 = Bishop(dark_team.color, 'bishop')
        knight1 = Knight(dark_team.color, 'knight')
        rook1 = Rook(dark_team.color, 'rook')
        non_pawn_pieces += [
            rook,
            knight,
            bishop,
            queen,
            king,
            bishop1,
            knight1,
            rook1,
        ]

        # black non pawns
        black_main_rank = 0
        for i in range(SQUARECOUNT):
            if non_pawn_pieces[i].kind == 'king':
                dark_team.set_king_id(i)
            self.struct[black_main_rank][i] = i   # place reference on board
            non_pawn_pieces[i].set_id(i)   # set id
            self.pieces_by_id[i] = non_pawn_pieces[
                i
            ]   # place id -> piece on dict
            dark_team.active_pieces.append(i)

        # black pieces first
        # black pawns
        black_pawn_rank = 1
        for j in range(SQUARECOUNT, (SQUARECOUNT * 2)):
            self.struct[black_pawn_rank][j - SQUARECOUNT] = j
            pawn = Pawn(dark_team.color, 'pawn')
            pawn.set_id(j)
            self.pieces_by_id[j] = pawn
            dark_team.active_pieces.append(j)

        # white pawns
        non_pawn_pieces = []
        rook = Rook(light_team.color, 'rook')
        knight = Knight(light_team.color, 'knight')
        bishop = Bishop(light_team.color, 'bishop')
        queen = Queen(light_team.color, 'queen')
        king = King(light_team.color, 'king')
        bishop1 = Bishop(light_team.color, 'bishop')
        knight1 = Knight(light_team.color, 'knight')
        rook1 = Rook(light_team.color, 'rook')
        non_pawn_pieces += [
            rook,
            knight,
            bishop,
            queen,
            king,
            bishop1,
            knight1,
            rook1,
        ]
        # white pawns
        white_pawn_rank = 6
        for j in range(SQUARECOUNT * 2, (SQUARECOUNT * 3)):
            self.struct[white_pawn_rank][j - SQUARECOUNT * 2] = j
            pawn = Pawn(light_team.color, 'pawn')
            pawn.set_id(j)
            self.pieces_by_id[j] = pawn
            light_team.active_pieces.append(j)

        # white non pawns
        white_main_rank = 7
        for i in range(SQUARECOUNT * 3, SQUARECOUNT * 4):
            if non_pawn_pieces[i - SQUARECOUNT * 3].kind == 'king':
                light_team.set_king_id(i - SQUARECOUNT * 3)
            self.struct[white_main_rank][
                i - SQUARECOUNT * 3
            ] = i   # place reference on board
            non_pawn_pieces[i - SQUARECOUNT * 3].set_id(i)   # set id
            self.pieces_by_id[i] = non_pawn_pieces[
                i - SQUARECOUNT * 3
            ]   # place id -> piece on dict
            light_team.active_pieces.append(i)

    def move_piece(
        self,
        piece: Piece,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
    ) -> Piece | None:
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
        if piece.is_valid_move(from_square, to_square, self):
            captured_piece = self.get_square_contents(to_square)
            old_row, old_col = from_square
            dest_row, dest_col = to_square
            self.struct[old_row][old_col] = None
            self.struct[dest_row][dest_col] = piece.id
            piece.has_moved = True
            return captured_piece

    def upgrade_piece(self, team: Team, piece: Piece, dest_kind: str) -> Piece:
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
        if piece.kind != PIECE_PAWN:
            raise TypeError(f'piece : {piece.kind} cannot be promoted')
        if not team.owns(piece):
            raise TypeError(f'piece : {piece.kind} does not belong to team')
        if dest_kind not in upgrade_selection:
            raise ValueError(f'Invalid upgrade type : {dest_kind}')
        piece_class = upgrade_selection[dest_kind]
        new_piece = piece_class(color, row, col, dest_kind)
        self.struct[new_piece.row][new_piece.col] = new_piece
        team.active_pieces.remove(piece)
        team.active_pieces.append(new_piece)
        return new_piece

    def get_pieces_by_id(self, id) -> Piece:
        if not self.pieces_by_id:
            raise Exception
        return self.pieces_by_id[id]

    def get_checking_pieces(
        self, current_player: Team, enemy_team: Team, move=None, is_king=False
    ):
        checking_pieces = {}
        if is_king:
            kings_grid_pos = move
        else:
            king_id = current_player.get_king_id()
            kings_grid_pos = self.square_by_id(king_id)

        enemy_count = enemy_team.get_count_active()
        found_count = 0
        for row in range(SQUARECOUNT):
            for col in range(SQUARECOUNT):
                if found_count == enemy_count:   # found all enemies stop
                    break
                contents = self.struct[row][col]
                if (contents is not None) and (
                    self.pieces_by_id[contents].color == enemy_team.color
                ):
                    enemy_piece_id = contents
                    found_count += 1
                    if (row, col) == move:   # king captures
                        continue
                    enemy_pieces_moves = self.generate_valid_moves(
                        enemy_piece_id, (row, col)
                    )
                    if kings_grid_pos in enemy_pieces_moves:
                        checking_pieces[contents] = (row, col)

        return checking_pieces

    def clone_grid(self):
        grid = []
        for row in range(self.square_count):
            grid_row = []
            for col in range(self.square_count):
                grid_row.append(self.struct[row][col])
            grid.append(grid_row)
        return grid
