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

import pygame, particles
import random

from helpers import *

M = Sheet("./data/image/objects/minis.png")
WPS = [[M.get_at((6,220,12,26),True), M.get_at((33,220,12,26),True), \
        M.get_at((60,220,12,26),True), M.get_at((87,220,12,26),True)], \
       [M.get_at((0,147,26,30),True), M.get_at((27,147,26,30),True), \
        M.get_at((54,147,26,30),True), M.get_at((81,147,26,30),True)], \
       [M.get_at((6,247,12,26),True), M.get_at((33,247,12,26),True), \
        M.get_at((60,247,12,26),True), M.get_at((87,247,12,26),True)], \
       [M.get_at((0,178,26,30),True), M.get_at((27,178,26,30),True), \
        M.get_at((54,178,26,30),True), M.get_at((81,178,26,30),True)]]


class Floater(pygame.sprite.Sprite):

    def __init__(self, pos, direction=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = WPS[direction]
        self.t = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.i = random.randint(0, 7)

    def update(self):
        if self.t==7:
            self.t = 0
            if self.i >= 3: self.i = 0
            else: self.i += 1
            self.image = self.images[self.i]
        else:
            self.t += 1


class Barrel(pygame.sprite.Sprite):

    def __init__(self, pos, player, boat, images=None):
        pygame.sprite.Sprite.__init__(self)
        self.p = player
        self.boat = boat
        self.t = random.randint(0, 5)
        self.i = 0
        if images!=None:
            self.images = images
        else:
            self.images = [M.get_at((34,131,17,15), True), \
                           M.get_at((52,131,17,15), True), \
                           M.get_at((70,131,17,15), True), \
                           M.get_at((88,131,17,15), True)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def die(self):
        self.p.collected += 1
        self.kill()

    def update(self):
        if self.t==5:
            self.t = 0
            if self.i >= 3: self.i = 0
            else: self.i += 1
            self.image = self.images[self.i]
        else:
            self.t += 1
        col = pygame.sprite.spritecollide(self, self.boat, False)
        if col:
            self.die()


class Scrolly(Barrel):

    def __init__(self, pos, player, boat):
        images = [M.get_at((50,93,12,22), True), \
                  M.get_at((63,93,12,22), True), \
                  M.get_at((76,93,12,22), True), \
                  M.get_at((89,93,12,22), True)]
        Barrel.__init__(self, pos, player, boat, images)

    def die(self):
        self.p.hasscroll = 1
        self.kill()
