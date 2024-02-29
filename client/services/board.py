import math
from typing import List, Tuple

import numpy as np
import pygame
from pygame import SurfaceType, Surface

from client.components.piece import Piece, Rook, Pawn, Knight, King, Bishop, Queen
from client.services.base_service import BaseService
from client.services.setting import Setting


class Board(BaseService):
    def __init__(self, setting: Setting):
        BaseService.__init__(self)
        self.setting = setting
        self._screen: Surface | SurfaceType
        self._board: Surface | SurfaceType

        self.drawingPos = (100, 0)

        self.minDimension: int = 0
        self.rectDimension = 0

        self.coordinate = np.full((8, 8), None, dtype=Piece)

        pygame.font.init()
        self.font = pygame.font.Font('./assets/fonts/Roboto-Regular.ttf', 15)
        self.selectedPiece: Piece = None

        self._is_white_turn = False

        # self.p = Pawn(False, 0, 0)
        # self.p2 = Pawn(False, 5, 2)
        # self.p1 = Pawn(True, 1, 1)
        # self.r = Rook(True, 2, 2)
        # self.n = Knight(True, 5, 5)
        # self.k = King(False, 7, 2)
        # self.coordinate[0, 0] = self.p
        # self.coordinate[1, 1] = self.p1
        # self.coordinate[5, 2] = self.p2
        # self.coordinate[2, 2] = self.r
        # self.coordinate[5, 5] = self.n
        # self.coordinate[7, 2] = self.k
        #
        self.pieces = pygame.sprite.Group()
        # self.pieces.add(self.p)
        # self.pieces.add(self.p1)
        # self.pieces.add(self.p2)
        # self.pieces.add(self.r)
        # self.pieces.add(self.n)
        # self.pieces.add(self.k)

        self.setDefaultBoard()
        # self.setBoardByFEN("8/R5pk/8/8/8/8/8/K7 w KQkq - 0 1")
        self.compute_legal_move()

    def empty_board(self):
        self.coordinate = np.full((8, 8), None, dtype=Piece)
        self.pieces.empty()

    def _compute_all_moves(self):
        for piece in self.pieces:
            if not isinstance(piece, Piece):
                pass

            piece.compute_possible_moves(self.coordinate)

    @property
    def screen(self) -> Surface | SurfaceType:
        return self._screen

    @screen.setter
    def screen(self, screen: Surface | SurfaceType):
        self._screen = screen
        self.minDimension = min(self.screen.get_width(), self.screen.get_height())
        self.rectDimension = math.floor(self.minDimension / 8)
        self.board = pygame.Surface((self.minDimension, self.minDimension))

    @property
    def board(self) -> Surface | SurfaceType:
        return self._board

    @board.setter
    def board(self, board: Surface | SurfaceType):
        self._board = board
        self.minDimension = min(self._board.get_width(), self._board.get_height())
        self.rectDimension = math.floor(self.minDimension / 8)

    @property
    def is_white_turn(self) -> bool:
        return self._is_white_turn

    @is_white_turn.setter
    def is_white_turn(self, turn: bool) -> None:
        self._is_white_turn = turn

    def setDrawingPos(self, startPos: tuple[0, 0]) -> None:
        pass

    def set_piece(self, piece: Piece) -> None:
        x, y = piece.x, piece.y
        self.coordinate[x][y] = piece
        self.pieces.add(piece)

    def setBoardByFEN(self, fen: str):
        self.empty_board()
        self.logger.info(f"Loading FEN Board: {fen}")
        items = fen.split(" ")
        fenBoard = items[0].split("/")
        for y, item in enumerate(fenBoard):
            offset = 0
            for char in item:
                if offset > 7:
                    break

                p = char
                match p:
                    case "r":
                        self.set_piece(Rook(False, offset, y))
                    case "R":
                        self.set_piece(Rook(True, offset, y))
                    case "n":
                        self.set_piece(Knight(False, offset, y))
                    case "N":
                        self.set_piece(Knight(True, offset, y))
                    case "b":
                        self.set_piece(Bishop(False, offset, y))
                    case "B":
                        self.set_piece(Bishop(True, offset, y))
                    case "q":
                        self.set_piece(Queen(False, offset, y))
                    case "Q":
                        self.set_piece(Queen(True, offset, y))
                    case "k":
                        self.set_piece(King(False, offset, y))
                    case "K":
                        self.set_piece(King(True, offset, y))
                    case "p":
                        self.set_piece(Pawn(False, offset, y))
                    case "P":
                        self.set_piece(Pawn(True, offset, y))
                    case _:
                        if p.isnumeric():
                            offset += int(p) - 1
                        else:
                            raise ValueError(f"p is not a number: {p}")
                offset += 1

        pass

    def setBoardByNotations(self, notations: list[str]) -> None:
        self.logger.log(f"Loading Notations Board: {notations}")
        pass

    def setDefaultBoard(self):
        self.logger.info("Loading default board...")
        self.setBoardByFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def drawBoard(self, rectDimension: int):
        for i in range(64):
            column = i % 8
            row = i // 8
            # self.logger.info(f"Column: {column}, Row: {row}")
            if (column + row) % 2 == 0:
                # pygame.draw.rect(self.screen, '#b58863', [relativeDimension[0] + (column * rectDimension),
                #                                           row * rectDimension, rectDimension, rectDimension])
                pygame.draw.rect(self.board, self.setting.color1, [(column * rectDimension),
                                                                   (row * rectDimension),
                                                                   rectDimension, rectDimension])
            else:
                pygame.draw.rect(self.board, self.setting.color2, [(column * rectDimension),
                                                                   (row * rectDimension),
                                                                   rectDimension, rectDimension])

    def drawNotations(self):
        for i in range(8):
            numberImg = None
            alphabetImg = None
            if i % 2 == 0:
                numberImg = self.font.render(str(8 - i), True, self.setting.color1)
                alphabetImg = self.font.render(chr(i + 97), True, self.setting.color1)

            else:
                numberImg = self.font.render(str(8 - i), True, self.setting.color2)
                alphabetImg = self.font.render(chr(i + 97), True, self.setting.color2)

            # Setup draw position at the end of the column
            numberRect = numberImg.get_rect()
            numberRect.x = self.minDimension - 15
            numberRect.y = self.rectDimension * i + 10
            self.board.blit(numberImg, numberRect)

            # Setup draw position at the bottom
            alphabetRect = numberImg.get_rect()
            alphabetRect.x = 10 + self.rectDimension * i
            alphabetRect.y = self.minDimension - 20
            self.board.blit(alphabetImg, alphabetRect)

    def draw(self):

        if self.screen is None:
            self.logger.error(f"Screen is not defined")
            raise Exception("Screen is not defined")
        self.drawBoard(self.rectDimension)
        self.pieces.draw(self.board)
        self.pieces.update(screen=self.board)
        self.drawNotations()

        self.screen.blit(self.board, self.drawingPos)

        # get all events
        ev = pygame.event.get()

        # proceed events
        for event in ev:

            # handle MOUSEBUTTONUP
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                rel_x, rel_y = pos[0] - self.drawingPos[0], pos[1] - self.drawingPos[1]
                self.handle_moving((rel_x, rel_y))
                #
                # do something with the clicked sprites...

        # pygame.draw.rect(self.screen, 'light gray', [x, y, height, width])

        # pygame.draw.rect(self.screen, 'gray', [0, 800, self.setting.WIDTH, 100])
        # pygame.draw.rect(self.screen, 'gold', [0, 800, self.setting.WIDTH, 100], 5)
        # pygame.draw.rect(self.screen, 'gold', [800, 0, 200, self.setting.HEIGHT], 5)
        # status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
        #                'Black: Select a Piece to Move!', 'Black: Select a Destination!']
        # self.screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
        # for i in range(9):
        #     pygame.draw.line(self.screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        #     pygame.draw.line(self.screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        # self.screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))

    def handle_moving(self, pos: tuple[int, int]):
        clicked_sprites = [s for s in self.pieces if s.rect.collidepoint(pos)]
        if len(clicked_sprites) > 0:
            if clicked_sprites[0].is_white != self.is_white_turn and self.selectedPiece is None:
                return
            self._handle_piece_selection(clicked_sprites[0], pos)
        else:
            self._handle_click_empty(pos)

    def _handle_piece_selection(self, piece: Piece, pos):

        if self.selectedPiece is not None:
            self._handle_click_empty(pos)
            return

        self.selectedPiece = piece
        self.logger.info(f"Selected Piece: {piece} at {piece.x} and {piece.y}")
        self.selectedPiece.is_selected = True

        # if self.is_white_turn != piece.is_white:
        #     self.make_turn((piece.x, piece.y))
        #     return

    def compute_legal_move(self):
        self._compute_all_moves()
        self.filter_invalid_moves()

    def _handle_click_empty(self, pos: tuple[int, int]):
        if self.selectedPiece is None:
            return

        clicked_sprites = [s for s in self.selectedPiece.possibleMoves if s.hidden_rect.collidepoint(pos)]
        if len(clicked_sprites) > 0:
            self.logger.info(f"Move to pos: {clicked_sprites[0].x}, {clicked_sprites[0].y}")
            self.make_turn((clicked_sprites[0].x, clicked_sprites[0].y))

            self.is_white_turn = not self.is_white_turn
            self.compute_legal_move()


        else:
            self.selectedPiece.is_selected = False
            self.selectedPiece = None
            self.logger.info(f"Click none")

    def make_turn(self, dest: tuple[int, int]) -> None | Piece:
        x, y = dest[0], dest[1]

        from_piece = self.selectedPiece
        dest_item = self.coordinate[x, y]

        from_piece.is_selected = False
        self.selectedPiece = None

        (from_x, from_y) = from_piece.x, from_piece.y
        if (from_x, from_y) == (x, y):
            return None

        self.coordinate[from_x, from_y] = None

        from_piece.move(x, y)

        self.coordinate[x, y] = from_piece

        if isinstance(from_piece, Pawn):
            from_piece.isFirstMove = False

            if from_piece.is_white and dest[1] == 6:
                from_piece.isFirstMove = True
            if not from_piece.is_white and dest[1] == 1:
                from_piece.isFirstMove = True
        if dest_item is not None:
            self.pieces.remove(dest_item)

        return dest_item

    #         Play capture sound

    #    Play move sound

    def filter_invalid_moves(self) -> None:
        black_king, white_king = self.get_black_and_white_king()
        team_king = white_king if self.is_white_turn else black_king
        temp_selected_piece = self.selectedPiece
        opponents = [p for p in self.pieces if p.is_white != self.is_white_turn]
        teams = [p for p in self.pieces if p.is_white == self.is_white_turn]

        illegal_move_dict = {}

        for piece in teams:
            if not isinstance(piece, Piece):
                self.logger.info(f"Invalid piece type: {piece}")
                raise ValueError(f"Invalid piece type: {piece}")

            x, y = piece.x, piece.y

            for move in piece.possibleMoves:

                self.selectedPiece = piece
                remove_piece = self.make_turn((move.x, move.y))

                if remove_piece is not None:
                    remove_piece.possibleMoves.empty()

                self._compute_all_moves()
                illegal_moves = []
                for opponent_piece in opponents:
                    inner_illegal_moves = [move for move in opponent_piece.possibleMoves if move.x == team_king.x
                                           and move.y == team_king.y]
                    if len(inner_illegal_moves) > 0:
                        illegal_moves.append(move)
                        break

                # Undo
                self.selectedPiece = piece
                self.make_turn((x, y))

                if remove_piece is not None:
                    self.set_piece(remove_piece)
                self._compute_all_moves()

                # Add to remove list
                if illegal_move_dict.get((x, y)) is None:
                    illegal_move_dict[(x, y)] = []

                illegal_move_dict[(x, y)] += illegal_moves

        for piece in teams:
            x, y = piece.x, piece.y
            possible = filter(lambda possible_move: self._compare(possible_move, illegal_move_dict[(x, y)]),
                              piece.possibleMoves)
            # [move for move in piece.possibleMoves if move not in illegal_move_dict[piece]]
            piece.possibleMoves.empty()
            [piece.possibleMoves.add(move) for move in possible]


    def _compare(self, move, illegal_moves):
        for illegal_move in illegal_moves:
            if move.x != illegal_move.x or move.y != illegal_move.y:
                continue
            return False
        return True

    def get_black_and_white_king(self):
        white_king: King
        black_king: King
        for piece in self.pieces:
            if not isinstance(piece, King):
                continue

            if piece.is_white:
                white_king = piece
            else:
                black_king = piece

        return black_king, white_king

    def drawPieces(self):
        pass

    def getCurrentFEN(self) -> str:
        pass

    def getCurrentNotations(self) -> List[str]:
        pass
