import math
from abc import abstractmethod
from typing import Any, Callable, Tuple

import pygame
from numpy import ndarray, dtype
from pygame.sprite import Sprite

from client.services.base_service import BaseService


class Piece(BaseService, Sprite):
    move_dict = {
        "P": {"movements": (1, -1), "continuous": False},
        "R": {"movements": [(1, 0), (0, 1), (-1, 0), (0, -1)], "continuous": True},
        "N": {"movements": [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2), ],
              "continuous": False},
        "B": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1)], "continuous": True},
        "Q": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1), ],
              "continuous": True},
        "K": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1), ],
              "continuous": False},
    }

    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__()
        Sprite.__init__(self)
        self.is_selected = is_selected
        self._x = x
        self._y = y
        self.is_white = is_white
        self.name = "Piece"
        self.shortName = "P"

        self.possibleMoves = pygame.sprite.Group()

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def move(self, x, y):
        self._x = x
        self._y = y
        self._recompute()

    def get_FEN_name(self):
        return self.shortName if self.is_white \
            else self.shortName.lower()

    def _compute_center(self):
        value = 100
        pos_x = self.x * value + math.floor(value / 2)
        pos_y = self.y * value + math.floor(value / 2)

        return pos_x, pos_y

    def _recompute(self):
        self.rect.center = self._compute_center()

    @staticmethod
    def get_piece_moves_dict(piece_type: str) -> tuple[list[tuple[int, int]], bool]:
        """Return info: (dict) on ghow a particular piece moves"""
        piece_move_info: dict = Piece.move_dict[piece_type]
        movements: list[tuple[int, int]] = piece_move_info["movements"]
        continuous: bool = piece_move_info["continuous"]
        return movements, continuous

    def clone(self):
        return Piece(self.is_white, self.x, self.y)

    # def _is_cover_king(self, board: ndarray):
    #     movements, is_continuous = self.get_piece_moves_dict("Q")
    #     for add_x, add_y in movements:  # Loop through piece movements list
    #         new_x, new_y = self.x + add_x, self.y + add_y  # Get new starting pos
    #         while not _is_out_of_bounds(new_x, new_y):
    #
    #             item = board[new_x][new_y]
    #
    #             # Check if the square is empty
    #             if item is None:
    #                 new_x += add_x
    #                 new_y += add_y
    #                 continue
    #
    #             if not isinstance(item, Piece):
    #                 self.logger.error("Item is not a Piece, what?")
    #                 raise ValueError("WTF")
    #
    #             if isinstance(item, King) and self.is_white == item.is_white:
    #                 return True
    #
    #             # Collides with team piece
    #             new_x += add_x
    #             new_y += add_y
    #
    #     return False
    #
    # def is_pin(self, board: ndarray):
    #     """Check whether a piece is pinned or not"""
    #     if not self._is_cover_king(board):
    #         return []
    #
    #     piece = Queen(self.is_white, self.x, self.y)
    #     piece._generate_non_pawn_move(board)
    #     pinned = []
    #     for move in piece.possibleMoves:
    #         if not isinstance(move, GreenDot):
    #             raise ValueError("Item is not a GreenDot, what?")
    #
    #         item = board[move.x][move.y]
    #
    #         if not isinstance(item, Piece):
    #             continue
    #
    #         if isinstance(item, Queen) or isinstance(item, Rook) or isinstance(item, Bishop):
    #             pinned.append(item)
    #
    #     return pinned

    def _generate_non_pawn_move(self, board: ndarray) -> None:
        piece_type = self.shortName
        movements, is_continuous = self.get_piece_moves_dict(piece_type)

        for add_x, add_y in movements:  # Loop through piece movements list
            new_x, new_y = self.x + add_x, self.y + add_y  # Get new starting pos
            while not _is_out_of_bounds(new_x, new_y):

                item = board[new_x][new_y]

                # Check if the square is empty
                if item is None:
                    self.possibleMoves.add(GreenDot(new_x, new_y))

                    if not is_continuous:  # If piece type doesn't continuously move e.g Knight, Pawn, King etc..
                        break
                    new_x += add_x
                    new_y += add_y
                else:
                    if not isinstance(item, Piece):
                        self.logger.error("Item is not a Piece, what?")
                        raise ValueError("WTF")

                    # Collides with team piece
                    if item.is_white == self.is_white:
                        break
                    # Collides with enemy piece
                    self.possibleMoves.add(GreenDot(new_x, new_y))
                    break

    def compute_possible_moves(self, board: ndarray):
        self.possibleMoves.empty()
        self._generate_non_pawn_move(board)

        # pin_items = self.is_pin(board)

        # if len(pin_items) > 1:
        #     return

        # if len(pin_items) == 1:
        #     pinned_item = pin_items[0]
        #     can_remove = [p for p in self.possibleMoves if p.x == pinned_item.x and p.y == pinned_item.y]
        #     self.possibleMoves.empty()
        #
        #     if len(can_remove):
        #         self.possibleMoves.add(GreenDot(pinned_item.x, pinned_item.y))

    def update(self, *args, **kwargs):
        if self.is_selected:
            self.possibleMoves.draw(kwargs['screen'])


class GreenDot(Piece, Sprite):
    def __init__(self, x: int, y: int, is_selected=False) -> None:
        Piece.__init__(self, False, x, y, is_selected)
        Sprite.__init__(self)

        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 125, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()
        self.hidden_rect = self.rect.inflate(90, 90)


def _is_out_of_bounds(x, y):
    if x < 0 or y < 0 or x > 7 or y > 7:
        return True
    else:
        return False


class Pawn(Piece):
    def __init__(self, is_white: bool, x: int, y: int, isFirstMove=True, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.isFirstMove = isFirstMove
        self.name = "Pawn"
        self.shortName = ""
        if self.is_white:
            self.image = pygame.image.load("assets/img/white_pawn.png", )
        else:
            self.image = pygame.image.load("assets/img/black_pawn.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()

    def _compute(self, board: ndarray[Any, dtype]):
        """Generate pawn moves"""
        # -------------------------------------
        x, y = self.x, self.y
        # piece_color, piece_type = chess_square  # type: ignore
        direction = -1 if self.is_white else 1
        # -------------------------------------
        movements, _ = self.get_piece_moves_dict("P")

        # Check if its inbounds
        if _is_out_of_bounds(x, y + direction):
            return

        # One square move
        cas = board[x][y + direction]
        if board[x][y + direction] is None:  # If empty
            self.possibleMoves.add(GreenDot(x, y + direction))
            # Two square move
            if self.isFirstMove and board[x][y + (direction * 2)] is None:
                # If its empty and pawn hasn't moved
                # f"{col}{row}:{col}{row + (direction * 2)}:N")
                self.possibleMoves.add(GreenDot(x, y + (direction * 2)))

        # Captures
        for add_x in movements:
            new_x = x + add_x  # type: ignore
            new_y = y + direction  # type: ignore

            if _is_out_of_bounds(new_x, y + direction):
                continue

            item = board[new_x][new_y]
            if item is None:  # Not empty square
                continue

            if not isinstance(item, Piece):
                raise ValueError("item is not a Piece")

            if item.is_white != self.is_white:  # Collides with enemy
                self.possibleMoves.add(GreenDot(new_x, new_y))

    def compute_possible_moves(self, board: ndarray[Any, dtype]):
        self.possibleMoves.empty()

        self._compute(board)


class Rook(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Rook"
        self.shortName = "R"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_rook.png", )
        else:
            self.image = pygame.image.load("assets/img/black_rook.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class Knight(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Knight"
        self.shortName = "N"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_knight.png", )
        else:
            self.image = pygame.image.load("assets/img/black_knight.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class Bishop(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Bishop"
        self.shortName = "B"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_bishop.png", )
        else:
            self.image = pygame.image.load("assets/img/black_bishop.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class King(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "King"
        self.shortName = "K"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_king.png", )
        else:
            self.image = pygame.image.load("assets/img/black_king.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class Queen(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Queen"
        self.shortName = "Q"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_queen.png", )
        else:
            self.image = pygame.image.load("assets/img/black_queen.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()
