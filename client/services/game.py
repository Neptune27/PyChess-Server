import threading

import pygame
from pygame import SurfaceType, Surface

from client.services.base_service import BaseService
from client.services.board import Board
from client.services.setting import Setting
from client.services.socket_service import SocketService
from client.services.stockfish_service import Stockfish


class Game(BaseService):
    screen: Surface | SurfaceType = None

    def __init__(self, setting: Setting,
                 board: Board, stockfish: Stockfish, socket_service: SocketService):
        BaseService.__init__(self)

        self.socket_service = socket_service
        self.stockfish = stockfish
        self.setting = setting
        self.board = board
        self.run = False

        Game.screen = pygame.display.set_mode([setting.WIDTH, setting.HEIGHT])

        self.board.screen = Game.screen

        self.logger.info('Game started')

        self.clock = pygame.time.Clock()

        self.game_scenes = []

        self.play_online = False
        self.board.play_online = self.play_online
        if self.play_online:
            self.socket_service.ready_msg = "join|1"
            self.socket_service.on_receive(self.board.handle_socket_message)
            self.board.start_online_game()

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
                    self.kill_socket()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # self.logger.info(event)
                    self.board.handle_event(event)

            pygame.display.flip()

    def kill_socket(self):
        self.socket_service.running = False
