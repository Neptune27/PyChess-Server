import threading

import pygame
from pygame import SurfaceType, Surface

from client.services.base_service import BaseService
from client.services.board import Board
from client.services.setting import Setting
from client.services.stockfish_service import Stockfish


class Game(BaseService):
    screen: Surface | SurfaceType = None

    def __init__(self, setting: Setting,
                 board: Board, stockfish: Stockfish):
        BaseService.__init__(self)

        self.stockfish = stockfish
        self.setting = setting
        self.board = board
        self.run = False

        Game.screen = pygame.display.set_mode([setting.WIDTH, setting.HEIGHT])

        self.board.screen = Game.screen

        self.logger.info('Game started')

        self.clock = pygame.time.Clock()

    def start(self):
        pygame.init()
        self.run = True
        while self.run:
            self.clock.tick(self.setting.FPS)
            self.board.draw()

            # event handling
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.logger.info('Game quit')
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.logger.info(event)
                    self.board.handle_event(event)


            pygame.display.flip()
