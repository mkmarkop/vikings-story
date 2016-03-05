# -*- coding: utf-8 -*-

############################################################################
#                                                                          #
#   Viking's Story: an open source tower defense game                      #
#   Copyright (C) 2010  Marko Pranjic                                      #
#                                                                          #
#   This program is free software: you can redistribute it and/or modify   #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation, either version 3 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                          #
############################################################################

import pygame

from game          import *
from world         import *
from shop          import *
from player        import *
from menu          import *
from music         import *
from gui           import Cursor
from helpers       import load_image
from states        import StateManager

class Viking:

    def __init__(self):
        pygame.init()
        self.config = Config()

        if self.config["fullscreen"]==1:
            self.screen = pygame.display.set_mode((1024, 768), FULLSCREEN, 32)
        else:
            self.screen = pygame.display.set_mode((1024, 768), 0, 32)

        pygame.display.set_caption("Viking's Story")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        pointer = Sheet("./data/image/menu/cursor.png")
        self.cursor = Cursor([pointer.get_at((0, 1, 16, 16), True), \
                      pointer.get_at((16, 1, 16, 16), True), \
                      pointer.get_at((33, 0, 16, 16), True)], self.screen)
        self.player = Player("./data/profiles/default.mkm")
        self.sound_manager = SoundManager()
        self.sound_manager.change_volume("background", self.config["bsound"])
        self.sound_manager.change_volume("sound", self.config["sfx"])
        self.state_manager = StateManager(self.player, self.config, \
                                          self.screen, [1024, 768], \
                                          self.cursor, self.sound_manager)
        Game("game", self.state_manager)
        Menu("menu", self.state_manager)
        World("map", self.state_manager)
        Shop("shop", self.state_manager)
        self.state_manager.set_state("menu")
        self.version = 0.9

    def loop(self):
        font = pygame.font.Font("./data/font/viking.ttf", 24)
        paused = -1

        while True:
            for event in pygame.event.get():
                self.state_manager.event(event)
                if event.type == QUIT:
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        exit()
                    elif event.key in [K_p, K_PAUSE] and \
                         self.state_manager.current_state == "game":
                         self.player.paused *= -1

            self.screen.fill((0, 0, 0))
            self.state_manager.update()
            self.cursor.update()
            
            if self.config["fps"]==1:
                fps = "FPS: "+'%.2f' % self.clock.get_fps()
                fp = font.render(fps, True, (255, 255, 255))
                self.screen.blit(fp,(8,8))

            pygame.display.update()
            self.clock.tick(30)
