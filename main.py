import pygame
import sys
from random import randint
from objects.constants import (
    WINDOWWIDTH,
    WINDOWHEIGHT,
    SQUARESIZE,
    SQUARECOUNT,
    DARKCOLOR,
    LIGHTCOLOR,
    WHITEPLAYER,
    BLACKPLAYER,
    BLACK,
    WHITE,
    GREY,
)


from objects.board import GameBoard
from objects.game_state import GameState
from objects.team import Team


FPS = 60   # frames per second


def setup():
    pygame.init()
    window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Chess')  # window title
    window.fill(GREY)
    chessboard = GameBoard(
        SQUARESIZE, SQUARECOUNT, DARKCOLOR, LIGHTCOLOR, window
    )  # create a board
    chessboard.draw_board()
    pygame.display.update()
    black_player = Team(BLACKPLAYER, BLACK)
    white_player = Team(WHITEPLAYER, WHITE)
    chessboard.set_pieces(
        black_player.active_pieces, white_player.active_pieces
    )
    return (pygame.time.Clock(), chessboard, black_player, white_player)


def main():
    # Setup and Initialization
    clock, chessboard, black_player, white_player = setup()
    game_state = GameState(chessboard, black_player, white_player)
    while game_state.get_game_is_running():
        game_state.handle_events()
        game_state.update_state()
        game_state.render()
        clock.tick(FPS)
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
